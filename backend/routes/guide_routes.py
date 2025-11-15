from flask import Blueprint, request, jsonify, send_file
from database import db, Customer, Order, QuizResponse, ModuleAssigned
from services.pdf_generator import generate_personalized_pdf
import os

guide_bp = Blueprint('guide_bp', __name__)

@guide_bp.route('/api/generate-full-guide', methods=['GET'])
def generate_full_guide():
    """
    Generates and serves the full, personalized PDF guide for a customer.
    Expects an 'order_id' as a query parameter.
    """
    order_id = request.args.get('order_id')
    if not order_id:
        return jsonify({'error': 'Order ID is required'}), 400

    order = Order.query.get(order_id)
    if not order or order.status != 'completed':
        return jsonify({'error': 'Invalid or incomplete order ID'}), 404

    customer = Customer.query.get(order.customer_id)
    quiz = QuizResponse.query.filter_by(customer_id=customer.id).order_by(QuizResponse.created_at.desc()).first()
    modules_assigned = ModuleAssigned.query.filter_by(order_id=order.id).all()
    modules = [m.module_name for m in modules_assigned]

    if not all([customer, quiz, modules]):
        return jsonify({'error': 'Could not retrieve all required data for guide generation'}), 500

    try:
        # Generate the full PDF using the existing logic, with is_upsell=True to get FULL_CONTENT
        pdf_path = generate_personalized_pdf(
            customer=customer,
            quiz_data=quiz.to_dict(),
            modules=modules,
            is_upsell=True 
        )
        
        if not os.path.exists(pdf_path):
            return jsonify({'error': 'Failed to generate PDF file.'}), 500

        # Return the file for download
        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        print(f"Error generating full guide PDF: {str(e)}")
        return jsonify({'error': 'An error occurred while generating your guide.'}), 500

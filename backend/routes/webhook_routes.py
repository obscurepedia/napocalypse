from flask import request, jsonify, current_app
from . import webhook_bp
import stripe
from database import db, Customer, QuizResponse, Order
from services.module_selector import select_modules
from services.pdf_generator import generate_personalized_pdf
from services.email_service import send_delivery_email, schedule_email_sequence
from config import Config
from datetime import datetime

stripe.api_key = Config.STRIPE_SECRET_KEY

@webhook_bp.route('/stripe', methods=['POST'])
def stripe_webhook():
    """
    Handle Stripe webhook events
    """
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, Config.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        print(f"Invalid payload: {str(e)}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        print(f"Invalid signature: {str(e)}")
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_successful_payment(session)
    
    elif event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        print(f"Payment succeeded: {payment_intent['id']}")
    
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        print(f"Payment failed: {payment_intent['id']}")
    
    return jsonify({'success': True}), 200

def handle_successful_payment(session):
    """
    Process successful payment:
    1. Update order status
    2. Select modules based on quiz
    3. Generate personalized PDF
    4. Send email with PDF
    5. Schedule email sequence
    """
    try:
        # Get order
        order = Order.query.filter_by(
            stripe_checkout_session_id=session['id']
        ).first()
        
        if not order:
            print(f"Order not found for session: {session['id']}")
            return
        
        # Update order
        order.stripe_payment_intent_id = session.get('payment_intent')
        order.status = 'completed'
        order.completed_at = datetime.utcnow()
        
        # Get customer and quiz
        customer = Customer.query.get(order.customer_id)
        quiz = QuizResponse.query.filter_by(
            customer_id=customer.id
        ).order_by(QuizResponse.created_at.desc()).first()
        
        # Save session_id to customer for personalization tracking
        if customer and not customer.stripe_session_id:
            customer.stripe_session_id = session['id']
        
        if not customer or not quiz:
            print(f"Customer or quiz not found for order: {order.id}")
            return
        
        # Select modules based on quiz responses
        modules = select_modules(quiz.to_dict())
        
        # Save assigned modules
        from database import ModuleAssigned
        for module_name in modules:
            module_assigned = ModuleAssigned(
                customer_id=customer.id,
                order_id=order.id,
                module_name=module_name
            )
            db.session.add(module_assigned)
        
        # Generate personalized PDF
        pdf_path = generate_personalized_pdf(
            customer=customer,
            quiz_data=quiz.to_dict(),
            modules=modules
        )
        
        # Update order with PDF info
        order.pdf_generated = True
        order.pdf_url = pdf_path
        
        db.session.commit()
        
        # Send delivery email with PDF
        send_delivery_email(
            to_email=customer.email,
            customer_name=customer.name or 'there',
            pdf_path=pdf_path,
            modules=modules
        )
        
        # Schedule 7-day email sequence
        schedule_email_sequence(
            customer_id=customer.id,
            order_id=order.id
        )
        
        print(f"Successfully processed payment for customer: {customer.email}")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error handling successful payment: {str(e)}")
        raise
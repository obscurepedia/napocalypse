"""
Upsell Routes
Handles upsell checkout and fulfillment
"""

from flask import Blueprint, request, jsonify, render_template
from database import db, Customer, Order, Upsell, ModuleAssigned
from services.pdf_generator import generate_personalized_pdf
from services.email_service import send_upsell_confirmation_email
import stripe
import os

upsell_bp = Blueprint('upsell', __name__)

@upsell_bp.route('/upsell')
def upsell_page():
    """
    Render upsell landing page
    """
    return render_template('upsell.html')

@upsell_bp.route('/api/create-upsell-checkout', methods=['POST'])
def create_upsell_checkout():
    """
    Create Stripe checkout session for upsell
    """
    try:
        data = request.json
        customer_id = data.get('customer_id')
        modules = data.get('modules', '')
        
        if not customer_id or not modules:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Get customer
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Get original order
        original_order = Order.query.filter_by(
            customer_id=customer_id,
            status='completed'
        ).order_by(Order.created_at.desc()).first()
        
        if not original_order:
            return jsonify({'error': 'Original order not found'}), 404
        
        # Create Stripe checkout session
        # Upsell price: $21.60 (20% off $27)
        session = stripe.checkout.Session.create(
            customer=customer.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Complete Reference Library - Upgrade',
                        'description': 'Full versions of your personalized modules',
                    },
                    'unit_amount': 2160,  # $21.60 in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=os.getenv('DOMAIN') + '/upsell-success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=os.getenv('DOMAIN') + '/upsell?customer=' + str(customer_id) + '&modules=' + modules,
            metadata={
                'customer_id': customer_id,
                'original_order_id': original_order.id,
                'modules': modules,
                'type': 'upsell'
            }
        )
        
        # Create upsell record
        upsell = Upsell(
            customer_id=customer_id,
            original_order_id=original_order.id,
            modules_included=modules,
            stripe_checkout_session_id=session.id,
            amount=2160,
            currency='usd',
            status='pending'
        )
        db.session.add(upsell)
        db.session.commit()
        
        return jsonify({
            'sessionId': session.id
        })
        
    except Exception as e:
        print(f"Error creating upsell checkout: {str(e)}")
        return jsonify({'error': str(e)}), 500

@upsell_bp.route('/upsell-success')
def upsell_success():
    """
    Upsell success page
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Upgrade Complete - Napocalypse</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                padding: 50px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 600px;
                text-align: center;
            }
            h1 {
                color: #27ae60;
                font-size: 2.5em;
                margin-bottom: 20px;
            }
            p {
                font-size: 1.2em;
                color: #555;
                line-height: 1.6;
                margin: 15px 0;
            }
            .icon {
                font-size: 5em;
                margin-bottom: 20px;
            }
            .button {
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 40px;
                text-decoration: none;
                border-radius: 50px;
                margin-top: 30px;
                font-weight: bold;
                transition: transform 0.3s ease;
            }
            .button:hover {
                transform: translateY(-3px);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">🎉</div>
            <h1>Upgrade Complete!</h1>
            <p>Thank you for upgrading to the Complete Reference Library!</p>
            <p>Your full guide is being generated and will be emailed to you within the next few minutes.</p>
            <p>Check your inbox for your comprehensive sleep training system.</p>
            <a href="/" class="button">Return to Home</a>
        </div>
    </body>
    </html>
    """

def process_upsell_webhook(session):
    """
    Process upsell webhook from Stripe
    Called from main webhook handler
    """
    try:
        customer_id = session.metadata.get('customer_id')
        original_order_id = session.metadata.get('original_order_id')
        modules = session.metadata.get('modules', '')
        
        # Get customer and upsell record
        customer = Customer.query.get(customer_id)
        upsell = Upsell.query.filter_by(
            stripe_checkout_session_id=session.id
        ).first()
        
        if not customer or not upsell:
            print(f"Customer or upsell not found for session {session.id}")
            return
        
        # Update upsell record
        upsell.stripe_payment_intent_id = session.payment_intent
        upsell.status = 'completed'
        upsell.completed_at = db.func.now()
        
        # Create order record for upsell
        order = Order(
            customer_id=customer_id,
            stripe_payment_intent_id=session.payment_intent,
            stripe_checkout_session_id=session.id,
            amount=2160,
            currency='usd',
            status='completed',
            completed_at=db.func.now()
        )
        db.session.add(order)
        db.session.flush()
        
        # Link upsell to order
        upsell.upsell_order_id = order.id
        
        # Get quiz data from original order
        from models import QuizResponse
        quiz_response = QuizResponse.query.filter_by(
            customer_id=customer_id
        ).first()
        
        if not quiz_response:
            print(f"Quiz response not found for customer {customer_id}")
            return
        
        quiz_data = {
            'baby_age': quiz_response.baby_age,
            'sleep_situation': quiz_response.sleep_situation,
            'sleep_philosophy': quiz_response.sleep_philosophy,
            'living_situation': quiz_response.living_situation,
            'parenting_setup': quiz_response.parenting_setup,
            'work_schedule': quiz_response.work_schedule,
            'biggest_challenge': quiz_response.biggest_challenge,
            'sleep_associations': quiz_response.sleep_associations
        }
        
        # Generate FULL PDF (is_upsell=True)
        module_list = modules.split(',')
        pdf_path = generate_personalized_pdf(
            customer=customer,
            quiz_data=quiz_data,
            modules=module_list,
            is_upsell=True  # This will use FULL_CONTENT versions
        )
        
        # Update upsell record
        upsell.pdf_generated = True
        upsell.pdf_url = pdf_path
        
        # Update order record
        order.pdf_generated = True
        order.pdf_url = pdf_path
        
        db.session.commit()
        
        # Send confirmation email with FULL PDF
        send_upsell_confirmation_email(
            customer=customer,
            pdf_path=pdf_path,
            modules=module_list
        )
        
        print(f"Upsell processed successfully for customer {customer_id}")
        
    except Exception as e:
        print(f"Error processing upsell webhook: {str(e)}")
        db.session.rollback()
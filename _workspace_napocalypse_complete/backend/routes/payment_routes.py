from flask import request, jsonify, current_app
from . import payment_bp
import stripe
from database import db, Customer, QuizResponse, Order
from config import Config

# Initialize Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

@payment_bp.route('/create-checkout', methods=['POST'])
def create_checkout():
    """
    Create Stripe Checkout session
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'customer_id' not in data or 'quiz_id' not in data:
            return jsonify({'error': 'Missing customer_id or quiz_id'}), 400
        
        customer_id = data['customer_id']
        quiz_id = data['quiz_id']
        
        # Get customer and quiz
        customer = Customer.query.get(customer_id)
        quiz = QuizResponse.query.get(quiz_id)
        
        if not customer or not quiz:
            return jsonify({'error': 'Customer or quiz not found'}), 404
        
        # Create or get Stripe customer
        if not customer.stripe_customer_id:
            stripe_customer = stripe.Customer.create(
                email=customer.email,
                name=customer.name,
                metadata={
                    'customer_id': customer.id
                }
            )
            customer.stripe_customer_id = stripe_customer.id
            db.session.commit()
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=customer.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': Config.STRIPE_PRICE_ID,
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{Config.FRONTEND_URL}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{Config.FRONTEND_URL}/quiz",
            client_reference_id=str(quiz_id),
            metadata={
                'customer_id': customer.id,
                'quiz_id': quiz_id
            }
        )
        
        # Create pending order
        order = Order(
            customer_id=customer.id,
            stripe_checkout_session_id=checkout_session.id,
            amount=4700,  # $47.00 in cents
            currency='usd',
            status='pending'
        )
        db.session.add(order)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        }), 200
        
    except stripe.error.StripeError as e:
        print(f"Stripe error: {str(e)}")
        return jsonify({'error': 'Payment processing error'}), 500
    except Exception as e:
        db.session.rollback()
        print(f"Error creating checkout: {str(e)}")
        return jsonify({'error': 'Failed to create checkout'}), 500

@payment_bp.route('/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """
    Get Stripe checkout session details
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        return jsonify({
            'success': True,
            'session': {
                'id': session.id,
                'payment_status': session.payment_status,
                'customer_email': session.customer_details.email if session.customer_details else None
            }
        }), 200
        
    except stripe.error.StripeError as e:
        print(f"Stripe error: {str(e)}")
        return jsonify({'error': 'Failed to get session'}), 500
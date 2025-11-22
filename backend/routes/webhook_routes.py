from flask import request, jsonify, current_app
from . import webhook_bp
import stripe
from database import db, Customer, QuizResponse, Order
from services.module_selector import select_modules
from services.email_service import schedule_email_sequence
from config import Config
from datetime import datetime

stripe.api_key = Config.STRIPE_SECRET_KEY

@webhook_bp.route('/stripe', methods=['POST'])
def stripe_webhook():
    """
    Handle Stripe webhook events
    """
    print(f"=== WEBHOOK CALLED ===")
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    print(f"Webhook payload length: {len(payload)}")
    print(f"Signature header present: {sig_header is not None}")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, Config.STRIPE_WEBHOOK_SECRET
        )
        print(f"Webhook event received: {event['type']}")
    except ValueError as e:
        print(f"Invalid payload: {str(e)}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        print(f"Invalid signature: {str(e)}")
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(f"Processing checkout.session.completed for session: {session['id']}")
        handle_successful_payment(session)
    
    elif event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        print(f"Payment succeeded: {payment_intent['id']}")
    
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        print(f"Payment failed: {payment_intent['id']}")
    
    else:
        print(f"Unhandled webhook event type: {event['type']}")
    
    return jsonify({'success': True}), 200

def handle_successful_payment(session):
    """
    Process successful payment for the new flow:
    1. Update order status.
    2. Generate the Quick-Start Guide PDF.
    3. Immediately email the Quick-Start Guide.
    4. Schedule the 14-day email course to start the next day.
    """
    print(f"=== HANDLING SUCCESSFUL PAYMENT (NEW FLOW) ===")
    try:
        order = Order.query.filter_by(stripe_checkout_session_id=session['id']).first()
        if not order:
            print(f"❌ Order not found for session: {session['id']}")
            return

        print(f"✅ Found order {order.id} for session: {session['id']}")
        
        order.stripe_payment_intent_id = session.get('payment_intent')
        order.status = 'completed'
        order.completed_at = datetime.utcnow()
        
        customer = Customer.query.get(order.customer_id)
        if not customer:
            print(f"❌ Customer not found for order: {order.id}")
            return

        print(f"✅ Found customer: {customer.email}")

        # 1. Mark order ready for PDF generation (PDF will be generated after personalization)
        # The PDF and delivery email will be sent from the success page after user enters names
        order.pdf_generated = False
        order.delivery_email_sent = False
        print(f"📋 Order marked ready - PDF will be generated after personalization on success page")

        # 2. Schedule the 14-day email sequence
        print(f"📅 Scheduling 14-day email sequence...")
        schedule_email_sequence(customer_id=customer.id, order_id=order.id)
        print(f"✅ Email sequence scheduled for {customer.email}")

        db.session.commit()
        print(f"🎉 Successfully processed payment (new flow) for customer: {customer.email}")

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error handling successful payment (new flow): {str(e)}")
        import traceback
        print(f"📋 Full traceback: {traceback.format_exc()}")
        raise
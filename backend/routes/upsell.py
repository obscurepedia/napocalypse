"""
Upsell Routes
Handles upsell checkout and fulfillment with story-specific personalization
"""

from flask import Blueprint, request, jsonify, render_template
from database import db, Customer, Order, Upsell, ModuleAssigned
from services.pdf_generator import generate_personalized_pdf
from config import Config
from datetime import datetime
import stripe
import os

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

upsell_bp = Blueprint('upsell', __name__)

@upsell_bp.route('/upsell')
def upsell_page():
    """
    Render upsell landing page with story-specific content
    """
    # Get URL parameters
    story = request.args.get('story', 'generic')
    customer_id = request.args.get('customer')
    modules = request.args.get('modules', '')
    
    # Story-specific content configuration
    story_config = get_story_config(story)
    
    # Get customer data if available
    customer_data = None
    if customer_id:
        customer = Customer.query.get(customer_id)
        if customer:
            customer_data = {
                'name': customer.name,
                'email': customer.email,
                'id': customer.id
            }
    
    return render_template('upsell.html', 
                         story=story,
                         story_config=story_config,
                         customer=customer_data,
                         modules=modules,
                         stripe_publishable_key=Config.STRIPE_PUBLISHABLE_KEY)

def get_story_config(story):
    """
    Get story-specific configuration for upsell page
    """
    configs = {
        'sarah': {
            'hero_title': '🎓 Ready to Master the CIO Method Like Sarah?',
            'hero_subtitle': 'Sarah broke the feed-to-sleep cycle in 7 days. You can too.',
            'method': 'CIO',
            'method_full': 'Cry-It-Out',
            'challenge': 'feed-to-sleep',
            'challenge_full': 'Feed-to-Sleep Association',
            'discount_code': 'SARAH20',
            'discount_percent': 20,
            'price_original': 27.00,
            'price_sale': 21.60,
            'testimonial': {
                'quote': "The Advanced CIO Playbook answered every single question I had. The troubleshooting section saved us when we hit obstacles on night 4.",
                'author': 'Sarah M.',
                'context': 'Used CIO for feed-to-sleep'
            },
            'benefits': [
                '50+ troubleshooting scenarios for every CIO challenge',
                'Complete science behind why CIO works safely',
                'Advanced feed-to-sleep breaking strategies',
                'Expert modifications for different temperaments',
                'Long-term success and regression handling'
            ],
            'urgency': "Sarah's method works, but only if you have the complete strategy."
        },
        'rachel': {
            'hero_title': '🌱 Master Gentle Methods Like Rachel?',
            'hero_subtitle': 'Rachel broke feed-to-sleep gently in 3 weeks. Here\'s her complete system.',
            'method': 'Gentle',
            'method_full': 'Gentle/No-Cry Methods',
            'challenge': 'feed-to-sleep',
            'challenge_full': 'Feed-to-Sleep Association',
            'discount_code': 'RACHEL20',
            'discount_percent': 20,
            'price_original': 27.00,
            'price_sale': 21.60,
            'testimonial': {
                'quote': "The gentle protocols in the Advanced Playbook gave me confidence that I was doing everything right. Worth every penny for the peace of mind.",
                'author': 'Rachel L.',
                'context': 'Used gentle methods for nursing dependency'
            },
            'benefits': [
                'Complete gentle feed-to-sleep protocols',
                'Week-by-week implementation guides',
                'Pantley pull-off technique mastery',
                'Partner involvement strategies',
                'Preserving breastfeeding relationship'
            ],
            'urgency': "Gentle methods work when you have the complete roadmap."
        },
        'lisa': {
            'hero_title': '😴 Fix Short Naps Like Lisa?',
            'hero_subtitle': 'Lisa went from 30-minute naps to 2-hour sleeps in 1 week.',
            'method': 'CIO',
            'method_full': 'Cry-It-Out for Naps',
            'challenge': 'short-naps',
            'challenge_full': 'Short Nap Training',
            'discount_code': 'LISA20',
            'discount_percent': 20,
            'price_original': 27.00,
            'price_sale': 21.60,
            'testimonial': {
                'quote': "The nap-specific strategies in the Advanced Playbook made all the difference. My baby went from 30-minute naps to 2+ hours!",
                'author': 'Lisa T.',
                'context': 'Used CIO for nap training'
            },
            'benefits': [
                'Complete nap training protocols',
                'Short nap troubleshooting guide',
                'Age-specific nap strategies',
                'Nap transition timing guides',
                'Schedule optimization techniques'
            ],
            'urgency': "Short naps steal your time and baby's development. Fix them now."
        },
        'generic': {
            'hero_title': '🚀 Ready to Go Deeper?',
            'hero_subtitle': 'Upgrade to the Complete Reference Library',
            'method': 'Sleep Training',
            'method_full': 'Complete Sleep Training',
            'challenge': 'sleep-challenges',
            'challenge_full': 'All Sleep Challenges',
            'discount_code': 'SAVE20',
            'discount_percent': 20,
            'price_original': 27.00,
            'price_sale': 21.60,
            'testimonial': {
                'quote': "The Complete Library has everything you need to become a sleep training expert. Best investment I made as a parent.",
                'author': 'Jennifer M.',
                'context': 'Used complete system'
            },
            'benefits': [
                'Complete troubleshooting for every scenario',
                'Both CIO and Gentle method mastery',
                'All sleep challenges covered',
                'Expert-level implementation guides',
                'Lifetime reference library'
            ],
            'urgency': "Get the complete system and handle any sleep challenge with confidence."
        }
    }
    
    return configs.get(story, configs['generic'])

@upsell_bp.route('/api/create-upsell-checkout', methods=['POST'])
def create_upsell_checkout():
    """
    Create Stripe checkout session for upsell with story-specific pricing
    """
    try:
        data = request.json
        customer_id = data.get('customer_id')
        modules = data.get('modules', 'Advanced Sleep Training Playbook')
        story = data.get('story', 'generic')
        discount_code = data.get('discount_code', 'SAVE20')
        
        # Development mode check
        if not Config.STRIPE_SECRET_KEY or Config.STRIPE_SECRET_KEY.startswith('sk_test_51234'):
            # Return a mock session ID for development
            return jsonify({
                'sessionId': 'cs_test_development_mode_' + story,
                'dev_mode': True,
                'message': 'Development mode - Stripe not configured'
            })
        
        # For new visitors from blog posts, customer_id might not exist
        # In this case, we'll create a temporary customer record
        customer = None
        original_order = None
        
        if customer_id:
            # Get customer if provided
            customer = Customer.query.get(customer_id)
            if not customer:
                return jsonify({'error': 'Customer not found'}), 404
            
            # Get original order for existing customers
            original_order = Order.query.filter_by(
                customer_id=customer_id,
                status='completed'
            ).order_by(Order.created_at.desc()).first()
        else:
            # Create a temporary customer record for new visitors
            # We'll update this with real info after payment
            customer = Customer(
                email=f"temp_{story}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}@temp.com",
                name=f"Temp Customer {story.title()}",
                baby_name="Unknown"
            )
            db.session.add(customer)
            db.session.flush()  # Get the ID without committing
            customer_id = customer.id
        
        # Get story configuration for pricing and description
        story_config = get_story_config(story)
        
        # Dynamic product name and description based on story
        product_name = f"Advanced {story_config['method_full']} Playbook"
        product_description = f"Complete {story_config['method_full']} mastery system with expert troubleshooting"
        
        # Create Stripe checkout session with story-specific pricing
        session_data = {
            'payment_method_types': ['card'],
            'line_items': [{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product_name,
                        'description': product_description,
                    },
                    'unit_amount': int(story_config['price_sale'] * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            'mode': 'payment',
            'success_url': os.getenv('DOMAIN', 'http://localhost:5000') + '/upsell-success?session_id={CHECKOUT_SESSION_ID}',
            'cancel_url': os.getenv('DOMAIN', 'http://localhost:5000') + f'/upsell?story={story}',
            'metadata': {
                'modules': modules,
                'story': story,
                'discount_code': discount_code,
                'type': 'upsell'
            }
        }
        
        # Add customer to session if they exist
        if customer and customer.stripe_customer_id:
            session_data['customer'] = customer.stripe_customer_id
        
        # Add customer_id and original_order_id to metadata if they exist
        if customer_id:
            session_data['metadata']['customer_id'] = str(customer_id)
        if original_order:
            session_data['metadata']['original_order_id'] = str(original_order.id)
        
        session = stripe.checkout.Session.create(**session_data)
        
        # Create upsell record with story information only for existing customers
        # New visitors will be tracked via Stripe metadata and webhook
        if original_order:
            upsell = Upsell(
                customer_id=customer_id,
                original_order_id=original_order.id,
                modules_included=modules,
                stripe_checkout_session_id=session.id,
                amount=int(story_config['price_sale'] * 100),  # Store in cents
                currency='usd',
                status='pending'
            )
            db.session.add(upsell)
        
        db.session.commit()  # Commit customer and upsell (if created)
        
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
        from database import QuizResponse
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
        
        # Schedule Advanced Playbook drip delivery (Days 7, 14, 21, 28, 32)
        from services.advanced_playbook_service import schedule_advanced_playbook_delivery
        
        schedule = schedule_advanced_playbook_delivery(
            customer_id=customer_id,
            upsell_order_id=order.id,
            purchase_date=datetime.utcnow()
        )
        
        print(f"Upsell processed successfully for customer {customer_id}")
        print(f"Advanced Playbook delivery scheduled: {schedule}")
        
    except Exception as e:
        print(f"Error processing upsell webhook: {str(e)}")
        db.session.rollback()
from flask import request, jsonify, current_app
from . import payment_bp
import stripe
from database import db, Customer, QuizResponse, Order
from config import Config

# Initialize Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

@payment_bp.route('/test-checkout', methods=['GET'])
def test_checkout():
    """
    Test checkout creation with dummy data - bypass quiz for testing
    """
    print("=" * 50)
    print("🧪 TEST CHECKOUT STARTED")
    print("=" * 50)
    
    try:
        print("STEP 1: Starting test checkout function...")
        
        # Add detailed system info
        print(f"STEP 1.1: Python version check...")
        import sys
        print(f"Python version: {sys.version}")
        
        print(f"STEP 1.2: Checking Stripe configuration...")
        print(f"Stripe API Key configured: {stripe.api_key is not None}")
        print(f"Price ID configured: {Config.STRIPE_PRICE_ID}")
        
        print("STEP 2: Database operations starting...")
        # Create or get test customer
        print("STEP 2.1: Looking for existing test customer...")
        test_email = "test@example.com"
        customer = Customer.query.filter_by(email=test_email).first()
        
        if not customer:
            print(f"STEP 2.2: Creating new test customer: {test_email}")
            customer = Customer(
                email=test_email,
                name="Test User"
            )
            db.session.add(customer)
            print("STEP 2.3: Flushing customer to get ID...")
            db.session.flush()
            print(f"STEP 2.4: Customer created with ID: {customer.id}")
        else:
            print(f"STEP 2.2: Using existing customer ID: {customer.id}")
        
        # Create dummy quiz response
        print("STEP 3: Creating quiz response...")
        quiz_response = QuizResponse(
            customer_id=customer.id,
            baby_age="4-6 months",
            sleep_situation="wakes_3-5_times",
            sleep_philosophy="willing_gradual",
            living_situation="house_separate_nursery",
            parenting_setup="two_parents_sharing",
            work_schedule="working_parent",
            biggest_challenge="wont_sleep_without_feeding",
            sleep_associations="nursing_bottle"
        )
        print("STEP 3.1: Adding quiz response to session...")
        db.session.add(quiz_response)
        print("STEP 3.2: Committing to database...")
        db.session.commit()
        print(f"STEP 3.3: Quiz response created with ID: {quiz_response.id}")
        
        print(f"✅ Database operations complete - Customer ID: {customer.id}, Quiz ID: {quiz_response.id}")
        
        # Now call the regular checkout creation
        from flask import request
        # Simulate the request data
        test_data = {
            'customer_id': customer.id,
            'quiz_id': quiz_response.id
        }
        
        # Redirect directly to Stripe checkout
        print("🧪 Redirecting to Stripe checkout...")
        
        # Create or get Stripe customer - handle mode switching
        print("STEP 4: Stripe customer operations...")
        
        # Check if existing customer ID is compatible with current Stripe mode
        stripe_customer_id = customer.stripe_customer_id
        if stripe_customer_id:
            try:
                print(f"STEP 4.1: Checking existing Stripe customer: {stripe_customer_id}")
                # Try to retrieve the customer to see if it exists in current mode
                test_customer = stripe.Customer.retrieve(stripe_customer_id)
                print(f"STEP 4.2: Existing customer validated: {test_customer.id}")
            except stripe.error.InvalidRequestError as e:
                if "similar object exists in live mode" in str(e) or "similar object exists in test mode" in str(e):
                    print(f"STEP 4.2: Mode mismatch detected - clearing customer ID")
                    print(f"STEP 4.3: Error: {str(e)}")
                    stripe_customer_id = None
                    customer.stripe_customer_id = None
                    db.session.commit()
                    print("STEP 4.4: Customer ID cleared due to mode mismatch")
                else:
                    raise e
        
        if not stripe_customer_id:
            print("STEP 4.5: Creating new Stripe customer...")
            print(f"STEP 4.6: Customer email: {customer.email}")
            print(f"STEP 4.7: Customer name: {customer.name}")
            
            try:
                print("STEP 4.8: Executing stripe.Customer.create() call...")
                stripe_customer = stripe.Customer.create(
                    email=customer.email,
                    name=customer.name,
                    metadata={'customer_id': customer.id}
                )
                print(f"STEP 4.9: Stripe customer created successfully: {stripe_customer.id}")
                customer.stripe_customer_id = stripe_customer.id
                print("STEP 4.10: Saving Stripe customer ID to database...")
                db.session.commit()
                print("STEP 4.11: Stripe customer saved to database")
            except Exception as stripe_error:
                print("=" * 50)
                print("❌ STRIPE CUSTOMER CREATION FAILED!")
                print("=" * 50)
                print(f"Error Type: {type(stripe_error).__name__}")
                print(f"Error Message: {str(stripe_error)}")
                print(f"Error Args: {stripe_error.args}")
                if hasattr(stripe_error, 'user_message'):
                    print(f"User Message: {stripe_error.user_message}")
                if hasattr(stripe_error, 'code'):
                    print(f"Error Code: {stripe_error.code}")
                print("=" * 50)
                raise stripe_error
        else:
            print(f"STEP 4.12: Using validated Stripe customer: {stripe_customer_id}")
        
        # Create checkout session for test
        print("STEP 5: Creating Stripe checkout session...")
        print(f"STEP 5.1: Using customer: {customer.stripe_customer_id}")
        print(f"STEP 5.2: Using price: {Config.STRIPE_PRICE_ID}")
        print(f"STEP 5.3: Frontend URL: {Config.FRONTEND_URL}")
        
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
            client_reference_id=str(quiz_response.id),
            metadata={
                'customer_id': customer.id,
                'quiz_id': quiz_response.id
            }
        )
        print(f"STEP 5.4: Checkout session created: {checkout_session.id}")
        print(f"STEP 5.5: Checkout URL: {checkout_session.url}")
        
        print(f"✅ Test checkout session created: {checkout_session.id}")
        print(f"✅ Checkout URL: {checkout_session.url}")
        
        # Create order record for test
        print("🧪 Creating test order record...")
        try:
            order = Order(
                customer_id=customer.id,
                stripe_checkout_session_id=checkout_session.id,
                amount=4700,  # $47.00 in cents
                currency='usd',
                status='pending'
            )
            db.session.add(order)
            db.session.commit()
            print("✅ Test order record created successfully")
        except Exception as order_error:
            print(f"❌ Test order creation failed: {order_error}")
            # Don't crash - just log the error and continue
            import traceback
            traceback.print_exc()
        
        # Return JSON response instead of redirect for safer testing
        return jsonify({
            'success': True,
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id,
            'message': 'Test checkout created successfully - visit the checkout_url to complete payment'
        }), 200
        
    except Exception as e:
        print("=" * 50)
        print("❌ CRITICAL ERROR OCCURRED!")
        print("=" * 50)
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print(f"Error Args: {e.args}")
        print("=" * 50)
        print("FULL TRACEBACK:")
        import traceback
        traceback.print_exc()
        print("=" * 50)
        
        # Try to rollback database changes
        try:
            db.session.rollback()
            print("Database rollback successful")
        except Exception as rollback_error:
            print(f"Database rollback failed: {rollback_error}")
        
        return jsonify({
            'error': f'Test checkout failed: {type(e).__name__}: {str(e)}',
            'error_type': type(e).__name__,
            'details': str(e)
        }), 500

@payment_bp.route('/create-checkout', methods=['POST'])
def create_checkout():
    """
    Create Stripe Checkout session
    """
    print("🚀 Payment route called - starting checkout creation")
    try:
        print("📦 Step 1: Getting request data...")
        data = request.get_json()
        print(f"📦 Received data: {data}")
        
        # Validate required fields
        print("📦 Step 2: Validating required fields...")
        if 'customer_id' not in data or 'quiz_id' not in data:
            print("❌ Missing customer_id or quiz_id")
            return jsonify({'error': 'Missing customer_id or quiz_id'}), 400
        
        customer_id = data['customer_id']
        quiz_id = data['quiz_id']
        print(f"📦 Customer ID: {customer_id}, Quiz ID: {quiz_id}")
        
        # Get customer and quiz
        print("📦 Step 3: Fetching customer and quiz from database...")
        customer = Customer.query.get(customer_id)
        quiz = QuizResponse.query.get(quiz_id)
        print(f"📦 Customer found: {customer is not None}, Quiz found: {quiz is not None}")
        
        if not customer or not quiz:
            print("❌ Customer or quiz not found in database")
            return jsonify({'error': 'Customer or quiz not found'}), 404
        
        # Create or get Stripe customer - handle mode switching
        print("📦 Step 4: Handling Stripe customer...")
        
        # Check if existing customer ID is compatible with current Stripe mode
        stripe_customer_id = customer.stripe_customer_id
        if stripe_customer_id:
            try:
                print(f"📦 Checking existing Stripe customer: {stripe_customer_id}")
                # Try to retrieve the customer to see if it exists in current mode
                test_customer = stripe.Customer.retrieve(stripe_customer_id)
                print(f"📦 Existing customer validated: {test_customer.id}")
            except stripe.error.InvalidRequestError as e:
                if "similar object exists in live mode" in str(e) or "similar object exists in test mode" in str(e):
                    print(f"📦 Mode mismatch detected - clearing customer ID")
                    print(f"📦 Error: {str(e)}")
                    stripe_customer_id = None
                    customer.stripe_customer_id = None
                    db.session.commit()
                    print("📦 Customer ID cleared due to mode mismatch")
                else:
                    raise e
        
        if not stripe_customer_id:
            print(f"📦 Creating new Stripe customer for: {customer.email}")
            try:
                stripe_customer = stripe.Customer.create(
                    email=customer.email,
                    name=customer.name,
                    metadata={
                        'customer_id': customer.id
                    }
                )
                customer.stripe_customer_id = stripe_customer.id
                db.session.commit()
                print(f"✅ Created Stripe customer: {stripe_customer.id}")
            except Exception as stripe_error:
                print(f"❌ Stripe customer creation failed: {stripe_error}")
                raise stripe_error
        else:
            print(f"📦 Using validated Stripe customer: {stripe_customer_id}")
        
        # Create checkout session
        print("📦 Step 5: Creating Stripe checkout session...")
        print(f"📦 Using Price ID: {Config.STRIPE_PRICE_ID}")
        print(f"📦 Frontend URL: {Config.FRONTEND_URL}")
        
        try:
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
            print(f"✅ Created checkout session: {checkout_session.id}")
        except Exception as session_error:
            print(f"❌ Checkout session creation failed: {session_error}")
            raise session_error
        
        # Create pending order
        print("📦 Step 6: Creating order record...")
        try:
            order = Order(
                customer_id=customer.id,
                stripe_checkout_session_id=checkout_session.id,
                amount=4700,  # $47.00 in cents
                currency='usd',
                status='pending'
            )
            db.session.add(order)
            db.session.commit()
            print("✅ Order record created successfully")
        except Exception as order_error:
            print(f"❌ Order creation failed: {order_error}")
            raise order_error
        
        print("✅ All steps completed successfully!")
        return jsonify({
            'success': True,
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ CRASH PREVENTED - Error type: {type(e).__name__}")
        print(f"❌ Error message: {str(e)}")
        import traceback
        print("❌ Full traceback:")
        traceback.print_exc()
        return jsonify({'error': f'Payment error: {str(e)}'}), 500

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
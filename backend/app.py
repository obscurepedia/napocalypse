from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from config import Config
from database import db, init_db
from routes import quiz_bp, payment_bp, webhook_bp
from routes.upsell import upsell_bp
from scheduler import init_scheduler

# Create Flask app
app = Flask(__name__, 
            static_folder='../frontend',
            template_folder='../frontend')

# Load configuration
app.config.from_object(Config)
Config.init_app(app)

# Enable CORS
CORS(app)

# Initialize database
init_db(app)

# Register blueprints
app.register_blueprint(quiz_bp, url_prefix='/api/quiz')
app.register_blueprint(payment_bp, url_prefix='/api/payment')
app.register_blueprint(webhook_bp, url_prefix='/webhook')
app.register_blueprint(upsell_bp)

# Initialize scheduler for email sequences
init_scheduler(app)

# Routes
@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/quiz')
def quiz():
    """Quiz page"""
    return render_template('quiz.html')

@app.route('/success')
def success():
    """Success page after payment - personalization collection"""
    return render_template('success.html')

@app.route('/success-details')
def success_details():
    """Success details page - what happens next"""
    return render_template('success-details.html')

@app.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    """Terms of service page"""
    return render_template('terms.html')

# Static file routes
@app.route('/css/<path:filename>')
def css_static(filename):
    """Serve CSS files"""
    return send_from_directory(os.path.join(app.static_folder, 'css'), filename)

@app.route('/js/<path:filename>')
def js_static(filename):
    """Serve JavaScript files"""
    return send_from_directory(os.path.join(app.static_folder, 'js'), filename)

@app.route('/images/<path:filename>')
def images_static(filename):
    """Serve image files"""
    return send_from_directory(os.path.join(app.static_folder, 'images'), filename)

@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return send_from_directory(app.static_folder, 'favicon.ico')

@app.route('/api/personalize', methods=['POST'])
def personalize():
    """Handle personalization data from success page"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        session_id = data.get('session_id')
        parent_name = data.get('parent_name')
        baby_name = data.get('baby_name')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'Session ID required'}), 400
            
        # Find the customer by session_id or email
        from database import Customer, Order
        customer = Customer.query.filter_by(stripe_session_id=session_id).first()
        
        # If not found by session_id, try to find by order session_id
        if not customer:
            order = Order.query.filter_by(stripe_checkout_session_id=session_id).first()
            if order:
                customer = Customer.query.get(order.customer_id)
                # Update the customer with the session_id for future use
                if customer:
                    customer.stripe_session_id = session_id
                    print(f"Found customer via order lookup: {customer.email}")
        
        if customer:
            print(f"Found customer for personalization: {customer.email}")
            # Update customer with personalization data
            if parent_name:
                customer.name = parent_name
            if baby_name:
                customer.baby_name = baby_name
                
            db.session.commit()
            
            # Now send the personalized email with PDF
            try:
                from database import Order, ModuleAssigned
                from services.email_service import send_delivery_email, schedule_email_sequence
                
                # Get the order and modules for this customer
                order = Order.query.filter_by(stripe_checkout_session_id=session_id).first()
                if order and order.pdf_generated:
                    # Get assigned modules
                    module_assignments = ModuleAssigned.query.filter_by(order_id=order.id).all()
                    modules = [ma.module_name for ma in module_assignments]
                    
                    print(f"📧 Sending personalized delivery email to: {customer.email}")
                    print(f"Using name: {customer.name or 'there'}, baby: {customer.baby_name or 'your little one'}")
                    
                    # Send email with personalized information
                    send_delivery_email(
                        to_email=customer.email,
                        customer_name=customer.name or 'there',
                        pdf_path=order.pdf_url,
                        modules=modules
                    )
                    print(f"✅ Personalized delivery email sent successfully")
                    
                    # Schedule 7-day email sequence
                    print(f"📅 Scheduling 7-day email sequence...")
                    schedule_email_sequence(
                        customer_id=customer.id,
                        order_id=order.id
                    )
                    print(f"✅ Email sequence scheduled")
                    
                else:
                    print(f"⚠️ Order or PDF not found for session {session_id}")
                    
            except Exception as email_error:
                print(f"❌ Error sending personalized email: {str(email_error)}")
                import traceback
                print(f"📋 Email error traceback: {traceback.format_exc()}")
                # Don't fail the personalization if email fails
            
            return jsonify({
                'success': True, 
                'message': 'Personalization data saved and email sent successfully'
            }), 200
        else:
            # If customer not found, still return success to avoid user-facing errors
            # but log the issue
            print(f"Customer not found for session_id: {session_id}")
            return jsonify({
                'success': True, 
                'message': 'Personalization data received'
            }), 200
            
    except Exception as e:
        print(f"Error saving personalization data: {str(e)}")
        return jsonify({
            'success': False, 
            'error': 'Internal server error'
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/test-db')
def test_db():
    """Test database connection"""
    try:
        # Try to query the database
        from database import Customer
        customer_count = Customer.query.count()
        return jsonify({
            'database_status': 'connected',
            'customer_count': customer_count,
            'message': 'Database is working!'
        }), 200
    except Exception as e:
        return jsonify({
            'database_status': 'error',
            'error': str(e),
            'message': 'Database connection failed'
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)
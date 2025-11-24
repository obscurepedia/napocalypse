from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from config import Config
from database import db, init_db
from routes import quiz_bp, payment_bp, webhook_bp, email_bp
from scheduler import init_scheduler

# Create Flask app
app = Flask(__name__, 
            static_folder='../frontend',
            template_folder='../frontend')

# Load configuration
app.config.from_object(Config)

# Configure SQLAlchemy engine options for production reliability
if hasattr(Config, 'SQLALCHEMY_ENGINE_OPTIONS'):
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = Config.SQLALCHEMY_ENGINE_OPTIONS

Config.init_app(app)

# Enable CORS
CORS(app)

# Disable caching in development
@app.after_request
def after_request(response):
    if app.debug:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

# Initialize database
init_db(app)

# Register blueprints
app.register_blueprint(quiz_bp, url_prefix='/api/quiz')
app.register_blueprint(payment_bp, url_prefix='/api/payment')
app.register_blueprint(webhook_bp, url_prefix='/webhook')
app.register_blueprint(email_bp, url_prefix='/api/email')

# Initialize scheduler for email sequences
init_scheduler(app)

# Routes
@app.route('/')
def index():
    """Home page - brand hub for returning visitors"""
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

@app.route('/refund')
def refund():
    """Refund policy page"""
    return render_template('refund.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page - both display form and handle submissions"""
    if request.method == 'POST':
        # Handle form submission
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '')
        baby_age = request.form.get('baby_age', '').strip()
        message = request.form.get('message', '').strip()
        
        # Basic validation
        if not all([name, email, subject, message]):
            return render_template('contact.html', error='Please fill in all required fields.')
        
        # TODO: Implement email sending logic here
        # For now, just redirect to a success state
        return render_template('contact.html', success='Thank you for your message! We\'ll get back to you within 24 hours.')
    
    # GET request - show the contact form
    return render_template('contact.html')

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

@app.route('/start')
def start():
    """Landing page - conversion-focused sales page"""
    return render_template('start.html')

@app.route('/blog')
def blog_index():
    """Educational blog index page"""
    return render_template('blog/index.html')

@app.route('/blog/<slug>')
def blog_post(slug):
    """Individual blog post rendered as template"""
    try:
        # Add .html extension if not present
        if not slug.endswith('.html'):
            slug += '.html'
        # Check if file exists first
        blog_path = os.path.join(app.template_folder, 'blog', slug)
        if os.path.exists(blog_path):
            return render_template(f'blog/{slug}')
        else:
            return "Blog post not found", 404
    except Exception as e:
        app.logger.error(f"Error serving blog post {slug}: {e}")
        return "Blog post not found", 404

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
            print(f"✅ Personalization saved: name={customer.name}, baby={customer.baby_name}")

            # Now generate PDF and send delivery email (if not already sent)
            try:
                from database import Order, ModuleAssigned
                from services.email_service import send_delivery_email
                from services.pdf_generator import generate_quick_start_guide_pdf

                order = Order.query.filter_by(stripe_checkout_session_id=session_id).first()

                if order and not order.delivery_email_sent:
                    # Generate personalized PDF
                    print(f"📄 Generating personalized Quick-Start Guide PDF...")
                    pdf_path = generate_quick_start_guide_pdf(customer)
                    order.pdf_generated = True
                    order.pdf_url = pdf_path
                    print(f"✅ PDF generated at: {pdf_path}")

                    # Send delivery email with personalized PDF
                    print(f"📧 Sending Quick-Start Guide email to: {customer.email}")
                    send_delivery_email(
                        to_email=customer.email,
                        customer_name=customer.name or 'there',
                        pdf_path=pdf_path,
                        modules=[]
                    )
                    order.delivery_email_sent = True
                    db.session.commit()
                    print(f"✅ Delivery email sent successfully")
                else:
                    print(f"⚠️ Delivery email already sent or order not found")

            except Exception as email_error:
                print(f"❌ Error generating PDF/sending email: {str(email_error)}")
                import traceback
                print(f"📋 Traceback: {traceback.format_exc()}")

            return jsonify({
                'success': True,
                'message': 'Personalization saved and email sent'
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
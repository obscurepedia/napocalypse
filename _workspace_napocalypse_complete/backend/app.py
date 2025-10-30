from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from config import Config
from database import db, init_db
from routes import quiz_bp, payment_bp, webhook_bp
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
    """Success page after payment"""
    return render_template('success.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

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
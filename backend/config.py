import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # Fallback to SQLite for development if no PostgreSQL available
    if not DATABASE_URL:
        DATABASE_URL = 'sqlite:///napocalypse.db'
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Stripe
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
    STRIPE_PRICE_ID = os.getenv('STRIPE_PRICE_ID')
    
    # AWS SES
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    AWS_SES_FROM_EMAIL = os.getenv('AWS_SES_FROM_EMAIL', 'support@napocalypse.com')
    
    # Frontend
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5000')
    
    # PDF Generation
    PDF_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'generated_pdfs')
    
    # Email Sequence
    EMAIL_SEQUENCE_DAYS = 7
    
    @staticmethod
    def init_app(app):
        """Initialize application with config"""
        # Create PDF output directory if it doesn't exist
        os.makedirs(Config.PDF_OUTPUT_DIR, exist_ok=True)
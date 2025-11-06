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
        
        # Validate required environment variables for production
        Config.validate_environment()
    
    @staticmethod
    def validate_environment():
        """Validate required environment variables"""
        missing_vars = []
        warnings = []
        
        # Critical variables that must be present in production
        critical_vars = []
        
        # Check if we're in production (not development or testing)
        is_production = Config.FLASK_ENV == 'production'
        
        if is_production:
            # In production, these are absolutely required
            critical_vars = [
                ('STRIPE_SECRET_KEY', Config.STRIPE_SECRET_KEY),
                ('STRIPE_PUBLISHABLE_KEY', Config.STRIPE_PUBLISHABLE_KEY),
                ('STRIPE_WEBHOOK_SECRET', Config.STRIPE_WEBHOOK_SECRET),
                ('STRIPE_PRICE_ID', Config.STRIPE_PRICE_ID),
                ('AWS_ACCESS_KEY_ID', Config.AWS_ACCESS_KEY_ID),
                ('AWS_SECRET_ACCESS_KEY', Config.AWS_SECRET_ACCESS_KEY),
                ('SECRET_KEY', Config.SECRET_KEY)
            ]
            
            # Check if we're using default secret key in production
            if Config.SECRET_KEY == 'dev-secret-key-change-in-production':
                missing_vars.append('SECRET_KEY (using default development key)')
        
        # Check critical variables
        for var_name, var_value in critical_vars:
            if not var_value:
                missing_vars.append(var_name)
        
        # Check email configuration (warning if missing)
        if not Config.AWS_SES_FROM_EMAIL or Config.AWS_SES_FROM_EMAIL == 'support@napocalypse.com':
            if is_production:
                warnings.append('AWS_SES_FROM_EMAIL (using default email address)')
        
        # Check database configuration
        if is_production and Config.DATABASE_URL.startswith('sqlite://'):
            warnings.append('DATABASE_URL (using SQLite instead of PostgreSQL in production)')
        
        # Report findings
        if missing_vars:
            error_msg = f"ERROR: Missing required environment variables: {', '.join(missing_vars)}"
            print(error_msg)
            if is_production:
                raise RuntimeError(error_msg)
        
        if warnings:
            warning_msg = f"WARNING: Environment warnings: {', '.join(warnings)}"
            print(warning_msg)
        
        if not missing_vars and not warnings:
            print("SUCCESS: Environment configuration validated successfully")
from flask import Blueprint

# Create blueprints
quiz_bp = Blueprint('quiz', __name__)
payment_bp = Blueprint('payment', __name__)
webhook_bp = Blueprint('webhook', __name__)
guide_bp = Blueprint('guide', __name__)

# Import routes
from . import quiz_routes
from . import payment_routes
from . import webhook_routes
from . import guide_routes
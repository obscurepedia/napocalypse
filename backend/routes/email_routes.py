"""
Email routes for unsubscribe functionality
"""
from flask import request, jsonify, render_template_string
from . import email_bp
from database import db, Customer
from datetime import datetime
import hashlib
import hmac
from config import Config


def generate_unsubscribe_token(customer_id, email):
    """
    Generate a secure token for unsubscribe links.
    Uses HMAC with SECRET_KEY to prevent tampering.
    """
    secret = Config.SECRET_KEY or 'napocalypse-default-secret'
    message = f"{customer_id}:{email}".encode()
    token = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()[:32]
    return token


def verify_unsubscribe_token(customer_id, email, token):
    """
    Verify the unsubscribe token is valid.
    """
    expected_token = generate_unsubscribe_token(customer_id, email)
    return hmac.compare_digest(token, expected_token)


def get_unsubscribe_url(customer_id, email):
    """
    Generate a full unsubscribe URL for a customer.
    """
    token = generate_unsubscribe_token(customer_id, email)
    base_url = Config.FRONTEND_URL or 'https://napocalypse.com'
    return f"{base_url}/api/email/unsubscribe?id={customer_id}&token={token}"


@email_bp.route('/unsubscribe', methods=['GET'])
def unsubscribe():
    """
    Handle unsubscribe requests.
    Shows a confirmation page and processes the unsubscribe.
    """
    customer_id = request.args.get('id')
    token = request.args.get('token')

    if not customer_id or not token:
        return render_template_string(UNSUBSCRIBE_ERROR_TEMPLATE,
                                      error="Invalid unsubscribe link. Please contact support@napocalypse.com")

    try:
        customer_id = int(customer_id)
    except ValueError:
        return render_template_string(UNSUBSCRIBE_ERROR_TEMPLATE,
                                      error="Invalid unsubscribe link. Please contact support@napocalypse.com")

    # Get customer
    customer = Customer.query.get(customer_id)
    if not customer:
        return render_template_string(UNSUBSCRIBE_ERROR_TEMPLATE,
                                      error="Customer not found. You may have already been unsubscribed.")

    # Verify token
    if not verify_unsubscribe_token(customer_id, customer.email, token):
        return render_template_string(UNSUBSCRIBE_ERROR_TEMPLATE,
                                      error="Invalid unsubscribe link. Please contact support@napocalypse.com")

    # Process unsubscribe
    customer.email_unsubscribed = True
    customer.unsubscribed_at = datetime.utcnow()
    db.session.commit()

    print(f"Customer {customer.email} unsubscribed successfully")

    return render_template_string(UNSUBSCRIBE_SUCCESS_TEMPLATE, email=customer.email)


@email_bp.route('/resubscribe', methods=['GET'])
def resubscribe():
    """
    Handle resubscribe requests (in case they change their mind).
    """
    customer_id = request.args.get('id')
    token = request.args.get('token')

    if not customer_id or not token:
        return render_template_string(UNSUBSCRIBE_ERROR_TEMPLATE,
                                      error="Invalid link. Please contact support@napocalypse.com")

    try:
        customer_id = int(customer_id)
    except ValueError:
        return render_template_string(UNSUBSCRIBE_ERROR_TEMPLATE,
                                      error="Invalid link. Please contact support@napocalypse.com")

    customer = Customer.query.get(customer_id)
    if not customer:
        return render_template_string(UNSUBSCRIBE_ERROR_TEMPLATE,
                                      error="Customer not found.")

    if not verify_unsubscribe_token(customer_id, customer.email, token):
        return render_template_string(UNSUBSCRIBE_ERROR_TEMPLATE,
                                      error="Invalid link. Please contact support@napocalypse.com")

    # Process resubscribe
    customer.email_unsubscribed = False
    customer.unsubscribed_at = None
    db.session.commit()

    print(f"Customer {customer.email} resubscribed successfully")

    return render_template_string(RESUBSCRIBE_SUCCESS_TEMPLATE, email=customer.email)


# HTML Templates
UNSUBSCRIBE_SUCCESS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unsubscribed - Napocalypse</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
            padding: 20px;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            text-align: center;
            max-width: 500px;
        }
        h1 { color: #2c3e50; margin-bottom: 20px; }
        p { color: #666; line-height: 1.6; }
        .email { font-weight: bold; color: #667eea; }
        .support { margin-top: 30px; font-size: 14px; color: #999; }
        a { color: #667eea; }
    </style>
</head>
<body>
    <div class="container">
        <h1>You've Been Unsubscribed</h1>
        <p>We've removed <span class="email">{{ email }}</span> from our email list.</p>
        <p>You won't receive any more emails from our 14-day course.</p>
        <p>We're sorry to see you go! If you have any feedback, we'd love to hear it.</p>
        <p class="support">
            Questions? Contact us at <a href="mailto:support@napocalypse.com">support@napocalypse.com</a>
        </p>
    </div>
</body>
</html>
"""

RESUBSCRIBE_SUCCESS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resubscribed - Napocalypse</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
            padding: 20px;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            text-align: center;
            max-width: 500px;
        }
        h1 { color: #2c3e50; margin-bottom: 20px; }
        p { color: #666; line-height: 1.6; }
        .email { font-weight: bold; color: #667eea; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome Back!</h1>
        <p>We've re-added <span class="email">{{ email }}</span> to our email list.</p>
        <p>You'll continue receiving your 14-day sleep course emails.</p>
    </div>
</body>
</html>
"""

UNSUBSCRIBE_ERROR_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error - Napocalypse</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
            padding: 20px;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            text-align: center;
            max-width: 500px;
        }
        h1 { color: #e74c3c; margin-bottom: 20px; }
        p { color: #666; line-height: 1.6; }
        a { color: #667eea; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Oops!</h1>
        <p>{{ error }}</p>
        <p>Need help? Contact <a href="mailto:support@napocalypse.com">support@napocalypse.com</a></p>
    </div>
</body>
</html>
"""

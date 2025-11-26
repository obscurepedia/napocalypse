"""
Facebook Conversions API Service
Sends server-side events to Facebook for better tracking and attribution
"""

import requests
import hashlib
import time
from config import Config


def hash_data(value):
    """
    Hash data using SHA256 as required by Facebook.
    Returns lowercase hashed value.
    """
    if not value:
        return None
    return hashlib.sha256(value.lower().strip().encode()).hexdigest()


def send_event(event_name, user_email, event_id=None, user_ip=None, user_agent=None,
               value=None, currency='USD', content_name=None, event_source_url=None,
               fbc=None, fbp=None, external_id=None):
    """
    Send a conversion event to Facebook Graph API.

    Args:
        event_name: Facebook event name (Lead, InitiateCheckout, Purchase, etc.)
        user_email: Customer email address (will be hashed)
        event_id: Unique event ID for deduplication with browser pixel
        user_ip: Client IP address
        user_agent: Client user agent string
        value: Transaction value (for InitiateCheckout, Purchase)
        currency: Currency code (default: USD)
        content_name: Product/content name
        event_source_url: URL where event occurred
        fbc: Facebook click ID from URL (fbc parameter)
        fbp: Facebook browser ID from cookie (_fbp)
        external_id: External user ID (customer ID)

    Returns:
        bool: True if event sent successfully, False otherwise
    """
    if not Config.FACEBOOK_ACCESS_TOKEN:
        print("Warning: Facebook Access Token not configured. Skipping CAPI event.")
        return False

    if not Config.FACEBOOK_PIXEL_ID:
        print("Warning: Facebook Pixel ID not configured. Skipping CAPI event.")
        return False

    try:
        # Build user_data with hashed email
        user_data = {}

        if user_email:
            user_data['em'] = hash_data(user_email)

        if user_ip:
            user_data['client_ip_address'] = user_ip

        if user_agent:
            user_data['client_user_agent'] = user_agent

        if fbc:
            user_data['fbc'] = fbc

        if fbp:
            user_data['fbp'] = fbp

        if external_id:
            user_data['external_id'] = str(external_id)

        # Build event data
        event_data = {
            'event_name': event_name,
            'event_time': int(time.time()),
            'action_source': 'website',
            'user_data': user_data
        }

        # Add event_id for deduplication if provided
        if event_id:
            event_data['event_id'] = event_id

        # Add event source URL if provided
        if event_source_url:
            event_data['event_source_url'] = event_source_url

        # Add custom data for commerce events
        if value is not None or content_name:
            custom_data = {}
            if value is not None:
                custom_data['value'] = float(value)
                custom_data['currency'] = currency
            if content_name:
                custom_data['content_name'] = content_name
            event_data['custom_data'] = custom_data

        # Prepare API request
        url = f'https://graph.facebook.com/v18.0/{Config.FACEBOOK_PIXEL_ID}/events'

        payload = {
            'data': [event_data],
            'access_token': Config.FACEBOOK_ACCESS_TOKEN
        }

        # Send to Facebook
        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Facebook CAPI: {event_name} event sent successfully")
            print(f"   Events received: {result.get('events_received', 0)}")
            if 'messages' in result:
                print(f"   Messages: {result['messages']}")
            return True
        else:
            print(f"❌ Facebook CAPI Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Facebook CAPI Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def send_lead_event(user_email, event_id=None, user_ip=None, user_agent=None,
                    event_source_url=None, fbc=None, fbp=None, customer_id=None):
    """
    Send a Lead event (quiz completion).
    """
    return send_event(
        event_name='Lead',
        user_email=user_email,
        event_id=event_id,
        user_ip=user_ip,
        user_agent=user_agent,
        content_name='Baby Sleep Quiz Completion',
        event_source_url=event_source_url,
        fbc=fbc,
        fbp=fbp,
        external_id=customer_id
    )


def send_initiate_checkout_event(user_email, value=47.00, currency='USD', event_id=None,
                                   user_ip=None, user_agent=None, event_source_url=None,
                                   fbc=None, fbp=None, customer_id=None):
    """
    Send an InitiateCheckout event (checkout started).
    """
    return send_event(
        event_name='InitiateCheckout',
        user_email=user_email,
        event_id=event_id,
        user_ip=user_ip,
        user_agent=user_agent,
        value=value,
        currency=currency,
        content_name='Baby Sleep Course',
        event_source_url=event_source_url,
        fbc=fbc,
        fbp=fbp,
        external_id=customer_id
    )


def send_purchase_event(user_email, value=47.00, currency='USD', event_id=None,
                        user_ip=None, user_agent=None, event_source_url=None,
                        fbc=None, fbp=None, customer_id=None):
    """
    Send a Purchase event (payment confirmed).
    """
    return send_event(
        event_name='Purchase',
        user_email=user_email,
        event_id=event_id,
        user_ip=user_ip,
        user_agent=user_agent,
        value=value,
        currency=currency,
        content_name='Baby Sleep Course',
        event_source_url=event_source_url,
        fbc=fbc,
        fbp=fbp,
        external_id=customer_id
    )

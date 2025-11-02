import requests
import json

# Test webhook endpoint with a mock Stripe event
def test_webhook():
    webhook_url = "https://napocalypse.com/webhook/stripe"
    
    # Mock Stripe checkout.session.completed event
    mock_event = {
        "id": "evt_test_webhook",
        "object": "event",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_12345",
                "object": "checkout.session",
                "customer_email": "test@example.com",
                "payment_status": "paid",
                "metadata": {
                    "user_id": "123"
                }
            }
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Stripe-Signature": "t=1234567890,v1=test_signature"
    }
    
    print(f"Testing webhook URL: {webhook_url}")
    print(f"Sending mock event: {mock_event['type']}")
    
    try:
        response = requests.post(webhook_url, 
                               data=json.dumps(mock_event), 
                               headers=headers,
                               timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        print(f"📝 Response: {response.text}")
        print(f"📋 Headers: {dict(response.headers)}")
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_webhook()
#!/usr/bin/env python3
"""
Generate test emails using production code for a specific customer
Run this on Render or locally with production database access
"""

import sys
import os

sys.path.insert(0, '.')

from app import app
from database import db, Customer
from services.email_service import get_sequence_content

def generate_test_emails_for_customer(customer_id, output_dir='test_email_output/production'):
    """Generate all 14 day emails for a customer using production code"""

    with app.app_context():
        customer = Customer.query.get(customer_id)

        if not customer:
            print(f"❌ Customer {customer_id} not found")
            return

        print("=" * 70)
        print(f"GENERATING PRODUCTION TEST EMAILS FOR CUSTOMER {customer_id}")
        print("=" * 70)
        print()
        print(f"Customer: {customer.name}")
        print(f"Email: {customer.email}")
        print(f"Baby Name: {customer.baby_name or 'Not provided'}")
        print()

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        print("Generating emails...")
        print()

        for day in range(1, 15):
            try:
                # Use get_sequence_content which generates the email HTML
                result = get_sequence_content(
                    day,
                    customer.name,
                    personalization_vars=None,  # Will be generated from customer data
                    order_id=None,
                    customer_id=customer.id,
                    customer_email=customer.email
                )

                # Extract content from result dictionary
                html_content = result.get('html_body', '')
                text_content = result.get('text_body', '')
                subject = result.get('subject', f'Day {day}')

                # Save HTML file
                html_filename = os.path.join(output_dir, f'day_{day}.html')
                with open(html_filename, 'w', encoding='utf-8') as f:
                    f.write(f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<title>Day {day}: {subject}</title>
<style>
body {{ max-width: 800px; margin: 20px auto; padding: 20px; font-family: Arial, sans-serif; background: #f5f5f5; }}
.header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
.subject {{ background: #3498db; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
.content {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
</style>
</head><body>
<div class="header">
    <h2 style="margin:0">Production Email - Customer {customer_id}</h2>
    <p style="margin: 5px 0 0 0; opacity: 0.9;">{customer.name} | {customer.email}</p>
</div>
<div class="subject"><strong>Day {day}:</strong> {subject}</div>
<div class="content">
{html_content}
</div>
</body></html>""")

                # Save text file
                text_filename = os.path.join(output_dir, f'day_{day}.txt')
                with open(text_filename, 'w', encoding='utf-8') as f:
                    f.write(f"""{'=' * 70}
PRODUCTION EMAIL - CUSTOMER {customer_id}
{'=' * 70}
Customer: {customer.name}
Email: {customer.email}
Baby Name: {customer.baby_name or 'Not provided'}

Day {day}: {subject}
{'=' * 70}

{text_content}
""")

                print(f"   ✅ Day {day}: {subject}")

            except Exception as e:
                print(f"   ❌ Day {day}: Error - {str(e)}")

        print()
        print("=" * 70)
        print(f"✅ EMAILS GENERATED")
        print(f"📁 Location: {output_dir}")
        print("=" * 70)


if __name__ == '__main__':
    # Default to Customer 3, or pass customer ID as argument
    customer_id = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    generate_test_emails_for_customer(customer_id)

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
from services.email_service import generate_day_email

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
                html_content, subject = generate_day_email(customer, day)

                # Save to file
                filename = os.path.join(output_dir, f'day_{day}.html')
                with open(filename, 'w', encoding='utf-8') as f:
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

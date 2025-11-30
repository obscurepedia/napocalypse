#!/usr/bin/env python3
"""
Generate test emails using production code for a specific customer
Run this on Render or locally with production database access
"""

import sys
import os
import re
from html.parser import HTMLParser

sys.path.insert(0, '.')

from app import app
from database import db, Customer
from services.email_service import get_sequence_content
from services.personalization import get_personalization_data


class HTMLToText(HTMLParser):
    """Convert HTML to plain text"""
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ['script', 'style']:
            self.skip = True
        elif tag == 'br':
            self.text.append('\n')
        elif tag == 'p':
            self.text.append('\n\n')
        elif tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.text.append('\n\n')
        elif tag == 'li':
            self.text.append('\n  • ')

    def handle_endtag(self, tag):
        if tag in ['script', 'style']:
            self.skip = False
        elif tag in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.text.append('\n')

    def handle_data(self, data):
        if not self.skip:
            text = data.strip()
            if text:
                self.text.append(text)

    def get_text(self):
        result = ''.join(self.text)
        # Clean up multiple newlines
        result = re.sub(r'\n{3,}', '\n\n', result)
        return result.strip()


def html_to_text(html):
    """Convert HTML to readable plain text"""
    parser = HTMLToText()
    parser.feed(html)
    return parser.get_text()

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

        # Get quiz response for personalization
        quiz_response = customer.quiz_responses[0] if customer.quiz_responses else None

        if not quiz_response:
            print("❌ No quiz response found for this customer")
            return

        # Convert quiz response to dict
        quiz_data = {
            'baby_age': quiz_response.baby_age,
            'sleep_situation': quiz_response.sleep_situation,
            'sleep_philosophy': quiz_response.sleep_philosophy,
            'living_situation': quiz_response.living_situation,
            'parenting_setup': quiz_response.parenting_setup,
            'work_schedule': quiz_response.work_schedule,
            'biggest_challenge': quiz_response.biggest_challenge,
            'sleep_associations': quiz_response.sleep_associations
        }

        # Generate personalization variables
        personalization_vars = get_personalization_data(customer, quiz_data, [])

        print(f"Quiz Data: baby_age={quiz_data['baby_age']}, method={personalization_vars.get('method')}")
        print(f"Personalization: baby_name_or_age='{personalization_vars.get('baby_name_or_age')}'")
        print()

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        print("Generating emails...")
        print()

        for day in range(1, 15):
            try:
                # Use get_sequence_content which generates the email HTML with full personalization
                result = get_sequence_content(
                    day,
                    customer.name,
                    personalization_vars=personalization_vars,
                    order_id=None,
                    customer_id=customer.id,
                    customer_email=customer.email
                )

                # Extract content from result dictionary
                html_content = result.get('html_body', '')
                subject = result.get('subject', f'Day {day}')

                # Convert HTML to readable text
                text_content = html_to_text(html_content)

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

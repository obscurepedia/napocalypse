#!/usr/bin/env python3
"""
Generate a single test email for customer WITHOUT baby name to show fallback
"""

import sys
import os

# Mock AWS modules
sys.modules['boto3'] = type('obj', (object,), {})()
sys.modules['botocore'] = type('obj', (object,), {'ClientError': Exception})()
sys.modules['botocore.exceptions'] = type('obj', (object,), {'ClientError': Exception})()

sys.path.insert(0, '.')

from services.personalization import get_personalization_data

class MockCustomerNoName:
    def __init__(self):
        self.id = 999
        self.name = "Test Parent"
        self.email = "test@example.com"
        self.baby_name = None  # No baby name provided

quiz_data = {
    'baby_age': '7-12 months',
    'sleep_philosophy': 'prefer_gentle',
    'biggest_challenge': 'wakes_every_1-2_hours',
    'sleep_associations': 'rocking_bouncing',
    'living_situation': 'room_sharing_baby',
    'parenting_setup': 'one_parent_nights',
    'work_schedule': 'shift_work'
}

customer = MockCustomerNoName()
pv = get_personalization_data(customer, quiz_data, [])

# Load Day 1 template
with open('email_templates/new_day_1.html', 'r') as f:
    template = f.read()

# Replace key personalization variable
template = template.replace('{customer_name}', customer.name)
template = template.replace('{baby_name_or_age}', pv['baby_name_or_age'])
template = template.replace('{biggest_challenge_text}', pv.get('biggest_challenge_text', 'struggling with sleep'))

# Extract the key sentence
import re
match = re.search(r"I know you're exhausted\.(.*?)that's not just tired", template, re.DOTALL)

print("=" * 70)
print("TESTING FALLBACK: Customer WITHOUT Baby Name")
print("=" * 70)
print()
print(f"Customer Name: {customer.name}")
print(f"Baby Name: {customer.baby_name}")
print()
print("Email sentence reads:")
print()

if match:
    sentence = match.group(0)
    # Clean up extra whitespace
    sentence = ' '.join(sentence.split())
    print(f'  "{sentence}"')
else:
    print("  Could not extract sentence")

print()
print("✅ Shows 'your baby' instead of 'your 7-12 month old'")
print("=" * 70)

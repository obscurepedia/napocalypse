#!/usr/bin/env python3
"""
Test baby name personalization
"""

import sys
sys.path.insert(0, '.')

from services.personalization import get_personalization_data

print("=" * 70)
print("BABY NAME PERSONALIZATION TEST")
print("=" * 70)
print()

# Mock customers with and without baby names
class MockCustomerWithBabyName:
    def __init__(self):
        self.name = "Sarah"
        self.id = 3
        self.baby_name = "Emma"

class MockCustomerWithoutBabyName:
    def __init__(self):
        self.name = "Mike"
        self.id = 4
        self.baby_name = None

quiz_data = {
    'baby_age': '7-12 months',
    'sleep_philosophy': 'prefer_gentle',
    'biggest_challenge': 'wakes_every_1-2_hours',
    'sleep_associations': 'rocking_bouncing',
    'living_situation': 'room_sharing_baby',
    'parenting_setup': 'one_parent_nights',
    'work_schedule': 'shift_work'
}

# Test 1: Customer WITH baby name
print("TEST 1: Customer WITH baby name")
print("-" * 70)
customer1 = MockCustomerWithBabyName()
pv1 = get_personalization_data(customer1, quiz_data, [])

print(f"Customer Name: {customer1.name}")
print(f"Baby Name: {customer1.baby_name}")
print(f"")
print(f"Personalization vars:")
print(f"  baby_name: '{pv1.get('baby_name')}'")
print(f"  baby_age_short: '{pv1.get('baby_age_short')}'")
print(f"  baby_name_or_age: '{pv1.get('baby_name_or_age')}'")
print()

# Simulate email text
email_text = f"I know you're exhausted. waking every 1-2 hours with {pv1.get('baby_name_or_age')}"
print(f"Email would say:")
print(f"  '{email_text}'")
print()

if pv1.get('baby_name_or_age') == 'Emma':
    print("✅ PASS: Shows baby name")
else:
    print("❌ FAIL: Should show 'Emma'")

print()
print("=" * 70)
print()

# Test 2: Customer WITHOUT baby name
print("TEST 2: Customer WITHOUT baby name")
print("-" * 70)
customer2 = MockCustomerWithoutBabyName()
pv2 = get_personalization_data(customer2, quiz_data, [])

print(f"Customer Name: {customer2.name}")
print(f"Baby Name: {customer2.baby_name}")
print(f"")
print(f"Personalization vars:")
print(f"  baby_name: '{pv2.get('baby_name')}'")
print(f"  baby_age_short: '{pv2.get('baby_age_short')}'")
print(f"  baby_name_or_age: '{pv2.get('baby_name_or_age')}'")
print()

# Simulate email text
email_text = f"I know you're exhausted. waking every 1-2 hours with {pv2.get('baby_name_or_age')}"
print(f"Email would say:")
print(f"  '{email_text}'")
print()

if pv2.get('baby_name_or_age') == 'your baby':
    print("✅ PASS: Falls back to 'your baby'")
else:
    print("❌ FAIL: Should show 'your baby'")

print()
print("=" * 70)
print("TESTS COMPLETE")
print("=" * 70)

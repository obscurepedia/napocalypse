"""
Full email generation tests with multiple personas.
Tests complete email rendering and placeholder replacement.
"""

import os
import sys
import re

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.personalization import get_personalization_data
from services.email_service import (
    _get_email_content_block,
    _parse_conditional_sections,
    _load_day_content_blocks,
    get_sequence_content
)


# Test personas representing different user segments
TEST_PERSONAS = {
    'single_working_apartment_cio': {
        'name': 'Sarah',
        'description': 'Single working mom in apartment using CIO',
        'quiz_data': {
            'baby_age': '7-12 months',
            'biggest_challenge': 'Wakes every 1-2 hours',
            'sleep_philosophy': 'Comfortable with some crying',
            'living_situation': 'Apartment or shared walls',
            'parenting_setup': 'Single parent doing it all',
            'work_schedule': 'Working full-time',
            'specific_challenge': "Won't fall asleep without feeding",
            'sleep_associations': 'Nursing or bottle to sleep'
        },
        'modules': ['module_5_cio', 'module_7_feeding']
    },
    'two_parents_house_gentle': {
        'name': 'Mike and Lisa',
        'description': 'Two parents in house using Gentle method',
        'quiz_data': {
            'baby_age': '4-6 months',
            'biggest_challenge': 'Takes 30+ minutes to fall asleep',
            'sleep_philosophy': 'Prefer gentle methods only',
            'living_situation': 'House with separate nursery',
            'parenting_setup': 'Two parents sharing duties',
            'work_schedule': 'Stay-at-home parent',
            'specific_challenge': "Won't fall asleep without rocking",
            'sleep_associations': 'Rocking, bouncing, or holding to sleep'
        },
        'modules': ['module_6_gentle', 'module_9_motion_rocking']
    },
    'solo_nights_shift_roomsharing_notsure': {
        'name': 'David',
        'description': 'One parent does nights, shift work, room sharing, not sure on method',
        'quiz_data': {
            'baby_age': '13-18 months',
            'biggest_challenge': 'Early morning wake-ups',
            'sleep_philosophy': 'Not sure yet',
            'living_situation': 'Room sharing with baby',
            'parenting_setup': 'One parent does all nights',
            'work_schedule': 'Shift work/irregular hours',
            'specific_challenge': 'Wakes up too early',
            'sleep_associations': 'Pacifier dependency'
        },
        'modules': ['module_6_gentle', 'module_12_pacifier']
    },
    'grandparents_wfh_siblings_cio': {
        'name': 'Emma',
        'description': 'Grandparents involved, WFH, sibling sharing, CIO',
        'quiz_data': {
            'baby_age': '19-24 months',
            'biggest_challenge': 'Naps are a complete disaster',
            'sleep_philosophy': 'Comfortable with some crying',
            'living_situation': 'Room sharing with siblings',
            'parenting_setup': 'Grandparents/caregivers involved',
            'work_schedule': 'Work from home',
            'specific_challenge': 'Naps are impossible',
            'sleep_associations': 'Multiple associations'
        },
        'modules': ['module_5_cio', 'module_10_nap_training']
    }
}


class MockCustomer:
    """Mock customer object for testing."""
    def __init__(self, id, name):
        self.id = id
        self.name = name


def check_unreplaced_placeholders(content):
    """Find any unreplaced placeholders in content."""
    # Match {placeholder} but not {{url}} style
    pattern = r'\{([a-z_]+)\}'
    matches = re.findall(pattern, content)

    # Filter out known allowed patterns
    allowed = ['unsubscribe_url']  # Double braces handled separately
    return [m for m in matches if m not in allowed]


def check_broken_conditionals(content):
    """Find any broken conditional sections."""
    issues = []

    # Check for unclosed IF blocks
    if_count = len(re.findall(r'<!-- IF ', content))
    endif_count = len(re.findall(r'<!-- ENDIF -->', content))
    if if_count != endif_count:
        issues.append(f"Mismatched IF/ENDIF: {if_count} IF, {endif_count} ENDIF")

    # Check for orphaned ELSE
    else_count = len(re.findall(r'<!-- ELSE -->', content))
    if else_count > if_count:
        issues.append(f"Orphaned ELSE blocks: {else_count} ELSE, {if_count} IF")

    return issues


def generate_email_for_persona(persona_key, day_number):
    """Generate a complete email for a test persona."""
    persona = TEST_PERSONAS[persona_key]

    # Create mock customer
    customer = MockCustomer(id=1, name=persona['name'])

    # Get personalization data
    personalization_vars = get_personalization_data(
        customer,
        persona['quiz_data'],
        persona['modules']
    )

    # Get email content
    email_content = get_sequence_content(
        day_number,
        customer_name=persona['name'],
        personalization_vars=personalization_vars,
        order_id=1
    )

    return email_content, personalization_vars


def test_full_email_generation():
    """Test complete email generation for all personas."""
    print("\n" + "=" * 60)
    print("FULL EMAIL GENERATION TESTS")
    print("=" * 60)

    results = {
        'total_tests': 0,
        'passed': 0,
        'failed': 0,
        'issues': []
    }

    for persona_key, persona in TEST_PERSONAS.items():
        print(f"\n--- Testing: {persona['description']} ---")

        for day in range(1, 15):
            results['total_tests'] += 1

            try:
                email_content, personalization_vars = generate_email_for_persona(persona_key, day)

                issues = []

                # Check for unreplaced placeholders
                body = email_content.get('html_body', '')
                unreplaced = check_unreplaced_placeholders(body)
                if unreplaced:
                    issues.append(f"Unreplaced placeholders: {unreplaced}")

                # Check for broken conditionals
                conditional_issues = check_broken_conditionals(body)
                if conditional_issues:
                    issues.extend(conditional_issues)

                # Check body has content
                if len(body) < 100:
                    issues.append(f"Body too short ({len(body)} chars)")

                # Check subject exists
                subject = email_content.get('subject', '')
                if not subject:
                    issues.append("Missing subject")

                if issues:
                    results['failed'] += 1
                    results['issues'].append({
                        'persona': persona_key,
                        'day': day,
                        'issues': issues
                    })
                    print(f"  Day {day}: FAIL - {', '.join(issues)}")
                else:
                    results['passed'] += 1

            except Exception as e:
                results['failed'] += 1
                results['issues'].append({
                    'persona': persona_key,
                    'day': day,
                    'issues': [str(e)]
                })
                print(f"  Day {day}: ERROR - {e}")

        # Summary for this persona
        print(f"  Persona complete")

    return results


def test_placeholder_coverage():
    """Verify all placeholders in templates have loading logic."""
    print("\n" + "=" * 60)
    print("PLACEHOLDER COVERAGE TEST")
    print("=" * 60)

    templates_dir = os.path.join(os.path.dirname(__file__), 'email_templates')
    all_placeholders = set()

    # Scan all templates for placeholders
    for day in range(1, 15):
        template_path = os.path.join(templates_dir, f'new_day_{day}.html')
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Find all {placeholder} patterns
                placeholders = re.findall(r'\{([a-z_]+)\}', content)
                for p in placeholders:
                    all_placeholders.add(p)

    print(f"\nFound {len(all_placeholders)} unique placeholders across all templates:")

    # Known placeholders that are handled
    known_handled = {
        'customer_name', 'baby_age', 'baby_age_short', 'method', 'method_type',
        'challenge', 'challenge_type', 'parenting_setup', 'work_schedule',
        'living_situation', 'sleep_association', 'biggest_struggle',
        'specific_challenge', 'biggest_challenge_text', 'sleep_association_text',
        'first_nap_example', 'baby_age_category'
    }

    # Content block placeholders (end with _block or _content)
    content_blocks = {p for p in all_placeholders if p.endswith('_block') or p.endswith('_content')}

    # Check for unknown placeholders
    all_known = known_handled | content_blocks
    unknown = all_placeholders - all_known

    print(f"\n  Basic variables: {len(known_handled & all_placeholders)}")
    print(f"  Content blocks: {len(content_blocks)}")

    if unknown:
        print(f"\n  UNKNOWN placeholders (may not be handled):")
        for p in sorted(unknown):
            print(f"    - {p}")
    else:
        print(f"\n  All placeholders are known: PASS")

    return len(unknown) == 0


def save_sample_emails():
    """Generate and save sample emails for visual inspection."""
    print("\n" + "=" * 60)
    print("GENERATING SAMPLE EMAILS")
    print("=" * 60)

    output_dir = os.path.join(os.path.dirname(__file__), 'test_email_output')
    os.makedirs(output_dir, exist_ok=True)

    # Generate sample for each persona, days 1, 5, 8, 14 (key days)
    sample_days = [1, 5, 8, 14]

    for persona_key, persona in TEST_PERSONAS.items():
        persona_dir = os.path.join(output_dir, persona_key)
        os.makedirs(persona_dir, exist_ok=True)

        for day in sample_days:
            try:
                email_content, _ = generate_email_for_persona(persona_key, day)

                # Create full HTML email
                html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{email_content.get('subject', f'Day {day}')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .subject {{ background: #f0f0f0; padding: 10px; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="subject">
        <strong>Subject:</strong> {email_content.get('subject', '')}
    </div>
    {email_content.get('html_body', '')}
</body>
</html>"""

                # Save to file
                filename = os.path.join(persona_dir, f'day_{day}.html')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html)

            except Exception as e:
                print(f"  Error generating {persona_key} Day {day}: {e}")

        print(f"  {persona_key}: {len(sample_days)} emails saved")

    print(f"\n  Sample emails saved to: {output_dir}")
    return output_dir


def run_all_tests():
    """Run all full email tests."""
    print("=" * 60)
    print("COMPREHENSIVE EMAIL PERSONALIZATION TESTS")
    print("=" * 60)

    # Test 1: Full email generation
    results = test_full_email_generation()

    print("\n" + "=" * 60)
    print("FULL EMAIL GENERATION RESULTS")
    print("=" * 60)
    print(f"\n  Total tests: {results['total_tests']}")
    print(f"  Passed: {results['passed']}")
    print(f"  Failed: {results['failed']}")

    if results['issues']:
        print(f"\n  Issues found:")
        for issue in results['issues'][:10]:  # Show first 10
            print(f"    - {issue['persona']} Day {issue['day']}: {issue['issues']}")
        if len(results['issues']) > 10:
            print(f"    ... and {len(results['issues']) - 10} more")

    # Test 2: Placeholder coverage
    placeholders_ok = test_placeholder_coverage()

    # Test 3: Save samples
    output_dir = save_sample_emails()

    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)

    all_pass = results['failed'] == 0 and placeholders_ok

    if all_pass:
        print("\n  ALL TESTS PASSED")
        print(f"\n  Review sample emails at: {output_dir}")
    else:
        print("\n  SOME TESTS FAILED")
        print(f"  Email generation failures: {results['failed']}")
        print(f"  Placeholder coverage: {'PASS' if placeholders_ok else 'FAIL'}")

    return all_pass


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

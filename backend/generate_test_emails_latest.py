#!/usr/bin/env python3
"""
Generate test emails for Customer 3 with proper conditional logic and content blocks
"""

import sys
import os
import re

# Mock AWS modules before importing email_service
sys.modules['boto3'] = type('obj', (object,), {})()
sys.modules['botocore'] = type('obj', (object,), {'ClientError': Exception})()
sys.modules['botocore.exceptions'] = type('obj', (object,), {'ClientError': Exception})()

sys.path.insert(0, '.')

from services.personalization import get_personalization_data


def simple_markdown_to_html(markdown_text):
    """Convert basic markdown to HTML without external dependencies"""
    if not markdown_text:
        return ""

    html = markdown_text

    # Headers
    html = re.sub(r'^### (.*?)$', r'<h3 style="color: #2c3e50; margin: 20px 0 10px 0;">\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2 style="color: #2c3e50; margin: 20px 0 10px 0;">\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', r'<h1 style="color: #2c3e50; margin: 20px 0 10px 0;">\1</h1>', html, flags=re.MULTILINE)

    # Bold
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #2c3e50;">\1</strong>', html)

    # Lists - Unordered
    html = re.sub(r'^\- (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*?</li>\n?)+', r'<ul style="line-height: 1.8; padding-left: 20px;">\n\g<0></ul>\n', html)

    # Lists - Ordered (numbered)
    lines = html.split('\n')
    in_ordered_list = False
    result_lines = []

    for line in lines:
        if re.match(r'^\d+\.\s', line):
            if not in_ordered_list:
                result_lines.append('<ol style="line-height: 1.8; padding-left: 20px;">')
                in_ordered_list = True
            item = re.sub(r'^\d+\.\s(.*?)$', r'<li>\1</li>', line)
            result_lines.append(item)
        else:
            if in_ordered_list:
                result_lines.append('</ol>')
                in_ordered_list = False
            result_lines.append(line)

    if in_ordered_list:
        result_lines.append('</ol>')

    html = '\n'.join(result_lines)

    # Paragraphs
    html = re.sub(r'^(?!<[huo]|<li)(.*?)$', r'<p style="margin: 10px 0;">\1</p>', html, flags=re.MULTILINE)

    # Clean up empty paragraphs
    html = re.sub(r'<p style="margin: 10px 0;"></p>', '', html)

    return html


def load_content_block(block_name, customer_profile, quiz_data):
    """Load a content block from markdown file"""
    base_path = "../content_blocks/email/"

    # Map block names to file paths based on customer profile and quiz data
    block_mapping = {
        'age_intro_block': f"intro/intro_age_{customer_profile['baby_age_range']}.md",
        'environment_block': f"environment/environment_{customer_profile['environment']}.md",
        'method_block': f"method/method_{customer_profile['method']}.md",
        'method_environment_block': f"method/method_{customer_profile['method']}_{customer_profile['environment']}.md",
        'naps_block': f"naps/naps_age_{customer_profile['baby_age_range']}.md",
        'routine_block': f"routine/routine_age_{customer_profile['age_group']}.md",
        'age_expectations_block': f"method/method_age_expectations_{customer_profile['age_group']}.md",
    }

    # Handle routine_association_block based on sleep_associations
    if block_name == 'routine_association_block':
        association = quiz_data.get('sleep_associations', '')
        if 'rocking' in association or 'bouncing' in association:
            block_mapping[block_name] = "routine/routine_rocking_association.md"
        elif 'feeding' in association:
            block_mapping[block_name] = "routine/routine_feeding_association.md"
        elif 'pacifier' in association:
            block_mapping[block_name] = "routine/routine_pacifier_association.md"

    # Handle routine_work_block for working parents
    if block_name == 'routine_work_block':
        if quiz_data.get('work_schedule') == 'working':
            block_mapping[block_name] = "routine/routine_working_parent.md"

    file_path = block_mapping.get(block_name)
    if not file_path:
        return ""

    full_path = os.path.join(base_path, file_path)

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
            return simple_markdown_to_html(markdown_content)
    except FileNotFoundError:
        return ""


def find_all_block_placeholders(html_content):
    """Find all {.*_block}, {.*_content}, and {.*_text} placeholders in HTML content"""
    # Match *_block, *_content, and *_text patterns (but not regular personalization vars)
    return re.findall(r'\{([a-z_]*(?:_block|_content|_text))\}', html_content)


def load_all_content_blocks(template_html, customer_profile, quiz_data):
    """Automatically load all content blocks found in template"""
    blocks = {}
    block_names = find_all_block_placeholders(template_html)

    base_path = "../content_blocks/email/"

    for block_name in block_names:
        # Build file path based on block name patterns
        file_path = None

        # Pattern matching for different block types
        if block_name == 'age_intro_block':
            file_path = f"intro/intro_age_{customer_profile['baby_age_range']}.md"
        elif block_name == 'age_based_content':
            file_path = f"age/age_{customer_profile['baby_age_range']}.md"
        elif block_name == 'environment_block':
            file_path = f"environment/environment_{customer_profile['environment']}.md"
        elif block_name == 'routine_association_block':
            association = quiz_data.get('sleep_associations', '')
            if 'rocking' in association or 'bouncing' in association:
                file_path = "routine/routine_rocking_association.md"
            elif 'feeding' in association:
                file_path = "routine/routine_feeding_association.md"
            elif 'pacifier' in association:
                file_path = "routine/routine_pacifier_association.md"
        elif block_name == 'routine_work_block':
            if quiz_data.get('work_schedule') == 'working':
                file_path = "routine/routine_working_parent.md"
        elif block_name == 'method_block':
            file_path = f"method/method_{customer_profile['method']}.md"
        elif block_name == 'method_instructions':
            file_path = f"method/method_{customer_profile['method']}.md"
        elif block_name == 'method_environment_block':
            file_path = f"method/method_{customer_profile['method']}_{customer_profile['environment']}.md"
        elif block_name == 'method_room_sharing_block':
            file_path = f"method/method_{customer_profile['method']}_{customer_profile['environment']}.md"
        elif block_name == 'age_expectations_block' or block_name == 'age_expectation_block':
            file_path = f"method/method_age_expectations_{customer_profile['age_group']}.md"
        elif block_name == 'naps_block' or block_name == 'naps_age_block':
            file_path = f"naps/naps_age_{customer_profile['baby_age_range']}.md"
        elif block_name == 'naps_working_parent_block':
            if quiz_data.get('work_schedule') == 'working':
                file_path = "naps/naps_working_parent.md"
        elif block_name == 'troubleshoot_method_block':
            file_path = f"troubleshoot/troubleshoot_{customer_profile['method']}.md"
        elif block_name == 'troubleshoot_apartment_block':
            if customer_profile['environment'] == 'apartment':
                file_path = "troubleshoot/troubleshoot_apartment.md"
        elif block_name == 'troubleshoot_single_parent_block':
            if quiz_data.get('parenting_setup') == 'one_parent_nights':
                file_path = "troubleshoot/troubleshoot_single_parent.md"
        elif block_name == 'troubleshoot_early_morning_block':
            if quiz_data.get('biggest_challenge') == 'early_morning_waking':
                file_path = "troubleshoot/troubleshoot_early_morning.md"
        elif block_name == 'celebration_challenge_block' or block_name == 'wins_challenge_block':
            challenge = quiz_data.get('biggest_challenge', '')
            if 'frequent' in challenge or 'wakes' in challenge:
                file_path = "wins/wins_frequent_waker.md"
            elif 'early_morning' in challenge:
                file_path = "wins/wins_early_morning.md"
            elif 'nap' in challenge:
                file_path = "wins/wins_nap_disaster.md"
            elif 'bedtime' in challenge:
                file_path = "wins/wins_bedtime_battle.md"
        elif block_name == 'celebration_working_parent_block' or block_name == 'wins_work_block':
            if quiz_data.get('work_schedule') == 'working':
                file_path = "wins/wins_working_parent.md"
        elif block_name == 'celebration_single_parent_block':
            if quiz_data.get('parenting_setup') == 'one_parent_nights':
                file_path = "celebration/celebration_single_parent.md"
        elif block_name == 'regression_age_block':
            age_range = customer_profile['baby_age_range'].replace('_', '-')
            file_path = f"regression/regression_{age_range}.md"
        elif block_name == 'regression_apartment_block':
            if customer_profile['environment'] == 'apartment':
                file_path = "regression/regression_apartment.md"
        elif block_name == 'regression_single_parent_block':
            if quiz_data.get('parenting_setup') == 'one_parent_nights':
                file_path = "regression/regression_single_parent.md"
        elif block_name == 'future_age_block':
            file_path = f"future/future_{customer_profile['age_group']}.md"
        elif block_name == 'feeding_main_challenge_block':
            if 'feeding' in quiz_data.get('sleep_associations', ''):
                file_path = "feeding/feeding_main_challenge.md"
        elif block_name == 'feeding_night_needs_baby_block':
            if customer_profile['age_group'] == 'baby':
                file_path = "feeding/feeding_night_needs_baby.md"
        elif block_name == 'feeding_night_needs_older_block':
            if customer_profile['age_group'] == 'toddler':
                file_path = "feeding/feeding_night_needs_older.md"
        elif block_name == 'pacifier_main_challenge_block':
            if 'pacifier' in quiz_data.get('sleep_associations', ''):
                file_path = "pacifier/pacifier_main_challenge.md"
        elif block_name == 'weaning_frequent_waker_block':
            if 'frequent' in quiz_data.get('biggest_challenge', ''):
                file_path = "weaning/weaning_frequent_waker.md"
        elif block_name == 'weaning_single_parent_block':
            if quiz_data.get('parenting_setup') == 'one_parent_nights':
                file_path = "weaning/weaning_single_parent.md"
        elif block_name == 'method_apartment_block':
            if customer_profile['environment'] == 'apartment':
                file_path = f"method/method_{customer_profile['method']}_apartment.md"
        elif block_name == 'method_single_parent_block':
            if quiz_data.get('parenting_setup') == 'one_parent_nights':
                file_path = "method/method_single_parent.md"
        elif block_name == 'method_partner_alignment_block':
            if quiz_data.get('parenting_setup') == 'two_sharing':
                file_path = "method/method_partner_alignment.md"
        elif block_name.startswith('disruption_'):
            # Handle disruption blocks
            if 'grandparents' in block_name:
                file_path = "disruption/disruption_grandparents.md"
            elif 'siblings' in block_name:
                file_path = "disruption/disruption_siblings.md"
            elif 'work' in block_name or 'travel' in block_name:
                file_path = "disruption/disruption_work_travel.md"

        # Try to load the block if we have a path
        if file_path:
            full_path = os.path.join(base_path, file_path)
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()
                    blocks[block_name] = simple_markdown_to_html(markdown_content)
            except FileNotFoundError:
                pass  # Block not found, will be removed later

    return blocks


def parse_conditional_sections(html_content, personalization_vars):
    """Parse and process conditional sections in email templates"""

    # Process all IF/ELSE/ENDIF blocks in one pass
    if_else_pattern = r'<!-- IF (\w+) == (\w+) -->(.*?)<!-- ELSE -->(.*?)<!-- ENDIF -->'

    def replace_if_else(match):
        var_name = match.group(1)
        expected_value = match.group(2)
        if_content = match.group(3)
        else_content = match.group(4)

        actual_value = personalization_vars.get(var_name, '')

        # Handle partial matches (e.g., room_sharing_baby should match room_sharing)
        if expected_value in actual_value or actual_value == expected_value:
            return if_content
        else:
            return else_content

    html_content = re.sub(if_else_pattern, replace_if_else, html_content, flags=re.DOTALL)

    # Then process all simple IF/ENDIF blocks
    if_pattern = r'<!-- IF (\w+) == (\w+) -->(.*?)<!-- ENDIF -->'

    def replace_conditional(match):
        var_name = match.group(1)
        expected_value = match.group(2)
        content = match.group(3)

        actual_value = personalization_vars.get(var_name, '')

        # Handle partial matches (e.g., room_sharing_baby should match room_sharing)
        if expected_value in actual_value or actual_value == expected_value:
            return content
        else:
            return ''

    html_content = re.sub(if_pattern, replace_conditional, html_content, flags=re.DOTALL)

    return html_content


def generate_email_for_day(day_num, customer, quiz_data, output_dir):
    """Generate a single email for a specific day"""

    # Get personalization data
    pv = get_personalization_data(customer, quiz_data, [])

    # Create customer profile for content block loading
    customer_profile = {
        'baby_age_range': quiz_data['baby_age'].replace(' ', '_'),
        'method': 'gentle' if quiz_data['sleep_philosophy'] == 'prefer_gentle' else 'cio',
        'environment': 'apartment' if 'apartment' in quiz_data['living_situation'] else 'room_sharing' if 'room_sharing' in quiz_data['living_situation'] else 'house',
        'age_group': 'baby' if quiz_data['baby_age'] in ['4-6 months', '7-12 months'] else 'toddler',
    }

    # Load template
    template_path = f'email_templates/new_day_{day_num}.html'
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"   ⚠️  Template not found: {template_path}")
        return

    # Load all content blocks found in template
    content_blocks = load_all_content_blocks(html_content, customer_profile, quiz_data)

    # Replace content blocks first
    for block_name, block_content in content_blocks.items():
        placeholder = '{' + block_name + '}'
        html_content = html_content.replace(placeholder, block_content)

    # Process conditional sections
    html_content = parse_conditional_sections(html_content, pv)

    # Replace all personalization variables
    for key, value in pv.items():
        placeholder = '{' + key + '}'
        html_content = html_content.replace(placeholder, str(value))

    # Replace any remaining common placeholders
    html_content = html_content.replace('{{unsubscribe_url}}', '#unsubscribe')

    # Remove any remaining block/content/text placeholders that weren't loaded
    html_content = re.sub(r'\{[a-z_]*(?:_block|_content|_text)\}', '', html_content)

    # Generate subject line based on day
    subjects = {
        1: "Day 1: Your Sleep Journey Starts Here",
        2: "Day 2: The Sleep Environment",
        3: "Day 3: Understanding Wake Windows",
        4: "Day 4: Building Your Bedtime Routine",
        5: "Day 5: Tonight's the Night",
        6: "Day 6: How Did Last Night Go?",
        7: "Day 7: Troubleshooting Common Issues",
        8: "Day 8: Night Wakings",
        9: "Day 9: Early Morning Wakings",
        10: "Day 10: Naps",
        11: "Day 11: Dealing with Regressions",
        12: "Day 12: Travel and Disruptions",
        13: "Day 13: Looking Ahead",
        14: "Day 14: You Did It",
    }

    subject = subjects.get(day_num, f"Day {day_num}")

    # Wrap in test harness HTML
    output_html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<title>Day {day_num}: {subject}</title>
<style>
body {{ max-width: 800px; margin: 20px auto; padding: 20px; font-family: Arial, sans-serif; background: #f5f5f5; }}
.header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
.subject {{ background: #3498db; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
.content {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
.check {{ color: #27ae60; font-weight: bold; }}
</style>
</head><body>
<div class="header">
    <h2 style="margin:0">✅ Test Email - Customer ID {customer.id}</h2>
    <p style="margin: 5px 0 0 0; opacity: 0.9;">{pv.get('method_name', 'Unknown')} Method | {quiz_data['baby_age']} | {quiz_data['parenting_setup']} | {quiz_data['work_schedule']}</p>
</div>
<div class="subject"><strong>Day {day_num}:</strong> {subject}</div>
<div class="content">{html_content}</div>
</body></html>"""

    # Write output file
    output_file = os.path.join(output_dir, f'day_{day_num}.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_html)

    print(f"   ✅ Day {day_num}: {subject}")


# Mock Customer class
class MockCustomer:
    def __init__(self):
        self.id = 3
        self.name = "Test Customer"
        self.email = "test@example.com"
        self.baby_name = "Emma"  # Baby name for personalization


def main():
    print("=" * 70)
    print("GENERATING TEST EMAILS FOR CUSTOMER 3")
    print("=" * 70)
    print()

    # Customer 3 quiz data
    quiz_data = {
        'baby_age': '7-12 months',
        'sleep_philosophy': 'prefer_gentle',
        'biggest_challenge': 'wakes_every_1-2_hours',
        'sleep_associations': 'rocking_bouncing',
        'living_situation': 'room_sharing_baby',
        'parenting_setup': 'one_parent_nights',
        'work_schedule': 'shift_work'
    }

    customer = MockCustomer()

    # Create output directory
    output_dir = 'test_email_output/customer_3_latest_test'
    os.makedirs(output_dir, exist_ok=True)

    print(f"Output directory: {output_dir}")
    print()
    print("Customer Profile:")
    print(f"  - Baby Age: {quiz_data['baby_age']}")
    print(f"  - Baby Name: {customer.baby_name}")
    print(f"  - Method: Gentle (prefer_gentle)")
    print(f"  - Challenge: Wakes every 1-2 hours")
    print(f"  - Living: Room sharing with baby")
    print(f"  - Parenting: Solo nights")
    print(f"  - Work: Shift work")
    print()
    print("Generating emails...")
    print()

    # Generate all 14 emails
    for day in range(1, 15):
        generate_email_for_day(day, customer, quiz_data, output_dir)

    print()
    print("=" * 70)
    print(f"✅ ALL EMAILS GENERATED")
    print(f"📁 Location: {output_dir}")
    print("=" * 70)


if __name__ == '__main__':
    main()

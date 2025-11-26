"""
Email Service using AWS SES
Handles delivery emails and automated 14-day sequences with full personalization.
Supports 67+ content blocks and conditional section parsing.
"""

import os
import re
import boto3
from botocore.exceptions import ClientError
import markdown2
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta
from config import Config
from database import db, EmailSequence

# Initialize SES client
ses_client = boto3.client(
    'ses',
    region_name=Config.AWS_REGION,
    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
)


def send_delivery_email(to_email, customer_name, pdf_path, modules):
    """
    Send initial delivery email with the Quick-Start Guide PDF.
    """
    from_email = f"{Config.AWS_SES_FROM_NAME} <{Config.AWS_SES_FROM_EMAIL}>"

    # Safe customer name handling
    safe_customer_name = customer_name if customer_name else "there"

    # New subject line for the Quick-Start Guide
    subject = f"Your Quick-Start Guide to Better Sleep is Here!"

    # New HTML body for the Quick-Start Guide
    html_body = f"""
    <html>
    <head></head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2c3e50;">Hi {safe_customer_name}, let's get started!</h2>

            <p>Thank you for joining the Napocalypse program! Your attached <strong>Quick-Start Guide</strong> has the first simple steps you can take tonight.</p>

            <div style="background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #2c3e50;">What's Next?</h3>
                <p>This guide has quick wins you can start using tonight. Your comprehensive 14-day email coaching course begins tomorrow.</p>
                <ul>
                    <li><strong>Today:</strong> Read the Quick-Start Guide and try the "One Thing".</li>
                    <li><strong>Tomorrow:</strong> Look for the "Day 1" email in your inbox.</li>
                </ul>
            </div>

            <p>We're so excited to guide you on this journey to better sleep for your entire family.</p>

            <p><strong>You've got this!</strong></p>

            <p>Best,<br>
            The Napocalypse Team</p>

            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            <p style="font-size: 12px; color: #666;">
                Questions? Reply to this email or visit <a href="https://napocalypse.com">napocalypse.com</a>
            </p>
        </div>
    </body>
    </html>
    """

    # New text body for the Quick-Start Guide
    text_body = f"""
    Hi {safe_customer_name}, let's get started!

    Thank you for joining the Napocalypse program! Your attached Quick-Start Guide has the first simple steps you can take tonight.

    What's Next?
    - Today: Read the Quick-Start Guide and try the "One Thing".
    - Tomorrow: Look for the "Day 1" email in your inbox.

    We're so excited to guide you on this journey to better sleep for your entire family.

    You've got this!

    Best,
    The Napocalypse Team

    ---
    Questions? Reply to this email or visit napocalypse.com
    """

    try:
        # Read PDF file
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()

        # Create MIME message
        msg = MIMEMultipart('mixed')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email

        # Add body
        msg_body = MIMEMultipart('alternative')
        msg_body.attach(MIMEText(text_body, 'plain'))
        msg_body.attach(MIMEText(html_body, 'html'))
        msg.attach(msg_body)

        # Add PDF attachment with a new filename
        attachment = MIMEApplication(pdf_data)
        attachment.add_header('Content-Disposition', 'attachment',
                              filename='Napocalypse_Quick_Start_Guide.pdf')
        msg.attach(attachment)

        # Send email
        response = ses_client.send_raw_email(
            Source=from_email,
            Destinations=[to_email],
            RawMessage={'Data': msg.as_string()}
        )

        print(f"Delivery email sent to {to_email}. Message ID: {response['MessageId']}")
        return True

    except ClientError as e:
        print(f"Error sending delivery email: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"Error sending delivery email: {str(e)}")
        return False


def send_sequence_email(to_email, customer_name, day_number, order_id=None, customer_id=None, modules=None, quiz_data=None, customer=None):
    """
    Send automated sequence email (Days 1-14) with full personalization.

    Args:
        to_email: Recipient email
        customer_name: Customer name
        day_number: Day in sequence (1-14)
        order_id: Order ID for personalization
        customer_id: Customer ID
        modules: List of module names
        quiz_data: Quiz response data (for personalization)
        customer: Customer object (for full personalization)
    """
    from_email = f"{Config.AWS_SES_FROM_NAME} <{Config.AWS_SES_FROM_EMAIL}>"

    # Get personalization data if available
    personalization_vars = None
    if customer and quiz_data and modules:
        from services.personalization import get_personalization_data
        personalization_vars = get_personalization_data(customer, quiz_data, modules)

    # Email content based on day and personalization
    email_content = get_sequence_content(
        day_number, customer_name, personalization_vars, order_id,
        customer_id=customer_id, customer_email=to_email
    )

    try:
        response = ses_client.send_email(
            Source=from_email,
            Destination={
                'ToAddresses': [to_email]
            },
            Message={
                'Subject': {'Data': email_content['subject']},
                'Body': {
                    'Html': {'Data': email_content['html_body']},
                    'Text': {'Data': email_content.get('text_body', '')}
                }
            }
        )

        print(f"Day {day_number} email sent successfully to {to_email}")
        return True

    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def schedule_email_sequence(customer_id, order_id):
    """
    Schedule 14-day email sequence.
    """
    try:
        # Check if sequence already exists for this order
        from database import EmailSequence
        existing = EmailSequence.query.filter_by(order_id=order_id).first()
        if existing:
            print(f"⚠️ Email sequence already exists for order {order_id}. Skipping duplicate creation.")
            return True

        # Get customer for email personalization
        from database import Customer
        customer = Customer.query.get(customer_id)

        for day in range(1, 15):
            scheduled_time = datetime.utcnow() + timedelta(days=day)

            # Get email content for this day
            email_content = get_sequence_content(
                day_number=day,
                customer_name=customer.name if customer else None,
                personalization_vars=None,  # This will be populated by the scheduler job
                order_id=order_id
            )

            email_seq = EmailSequence(
                customer_id=customer_id,
                order_id=order_id,
                day_number=day,
                email_type=f'day{day}',
                subject=email_content['subject'],
                scheduled_for=scheduled_time,
                status='pending'
            )
            db.session.add(email_seq)

        db.session.commit()
        print(f"Scheduled 14-day email sequence for customer {customer_id}")
        return True

    except Exception as e:
        db.session.rollback()
        print(f"Error scheduling email sequence: {str(e)}")
        return False


def _get_email_content_block(category, block_id):
    """
    Load email-optimized content block from markdown and convert to HTML.

    Args:
        category: Block category (e.g., 'intro', 'method', 'challenge')
        block_id: Block identifier (e.g., 'intro_age_4_6_months')

    Returns:
        str: HTML content or empty string if not found
    """
    try:
        content_path = os.path.join(
            os.path.dirname(__file__),
            '../../content_blocks/email',
            category,
            f'{block_id}.md'
        )

        # Normalize path for cross-platform compatibility
        content_path = os.path.normpath(content_path)

        with open(content_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        html_content = markdown2.markdown(
            markdown_content,
            extras=['fenced-code-blocks', 'tables', 'break-on-newline']
        )

        # Style the HTML for email compatibility
        # Add inline styles for paragraphs and lists
        html_content = html_content.replace('<p>', '<p style="margin: 10px 0;">')
        html_content = html_content.replace('<ul>', '<ul style="line-height: 1.8; padding-left: 20px;">')
        html_content = html_content.replace('<ol>', '<ol style="line-height: 1.8; padding-left: 20px;">')
        html_content = html_content.replace('<h3>', '<h3 style="color: #2c3e50; margin: 20px 0 10px 0;">')
        html_content = html_content.replace('<h4>', '<h4 style="color: #2c3e50; margin: 15px 0 8px 0;">')
        html_content = html_content.replace('<strong>', '<strong style="color: #2c3e50;">')

        return html_content
    except FileNotFoundError:
        print(f"Warning: Email content block not found: {category}/{block_id}")
        return ""
    except Exception as e:
        print(f"Error loading content block {category}/{block_id}: {str(e)}")
        return ""


def _parse_conditional_sections(html_content, personalization_vars):
    """
    Parse and process conditional sections in HTML templates.

    Handles IF/ELSE/ENDIF blocks like:
    <!-- IF parenting_setup == single -->
    <p>Content for single parents</p>
    <!-- ELSE -->
    <p>Content for others</p>
    <!-- ENDIF -->

    Also supports IN operator for checking multiple values:
    <!-- IF work_schedule IN working,shift_work -->

    Args:
        html_content: HTML template with conditional sections
        personalization_vars: Dict of personalization variables

    Returns:
        str: Processed HTML with conditionals resolved
    """
    if not personalization_vars:
        # Remove all conditional blocks if no personalization
        html_content = re.sub(
            r'<!-- IF .+? -->.*?<!-- ENDIF -->',
            '',
            html_content,
            flags=re.DOTALL
        )
        return html_content

    # Pattern to match IF blocks with optional ELSE
    # Supports ==, !=, and IN operators
    pattern = r'<!-- IF (\w+) (==|!=|IN) ([^\s]+?) -->(.*?)(?:<!-- ELSE -->(.*?))?<!-- ENDIF -->'

    def replace_conditional(match):
        var_name = match.group(1)
        operator = match.group(2)
        value = match.group(3)
        if_content = match.group(4) or ''
        else_content = match.group(5) or ''

        # Get actual value from personalization vars
        actual_value = str(personalization_vars.get(var_name, '')).lower()

        # Evaluate condition
        condition_met = False
        if operator == '==':
            condition_met = actual_value == value.lower()
        elif operator == '!=':
            condition_met = actual_value != value.lower()
        elif operator == 'IN':
            # Support comma-separated list of values
            allowed_values = [v.strip().lower() for v in value.split(',')]
            condition_met = actual_value in allowed_values

        # Return appropriate content
        if condition_met:
            return if_content.strip()
        else:
            return else_content.strip()

    # Process all conditional blocks
    result = re.sub(pattern, replace_conditional, html_content, flags=re.DOTALL)

    return result


def _load_day_content_blocks(day_number, personalization_vars):
    """
    Load all content blocks needed for a specific day.

    Args:
        day_number: Day in sequence (1-14)
        personalization_vars: Personalization variables dict

    Returns:
        dict: Content blocks keyed by placeholder name
    """
    content = {}

    if not personalization_vars:
        return content

    # Extract common variables
    baby_age = personalization_vars.get('baby_age', '')
    baby_age_category = personalization_vars.get('baby_age_category', 'baby')
    method_type = personalization_vars.get('method_type', 'gentle')
    challenge_type = personalization_vars.get('challenge_type', 'general')
    parenting_setup = personalization_vars.get('parenting_setup', 'two_sharing')
    work_schedule = personalization_vars.get('work_schedule', 'working')
    living_situation = personalization_vars.get('living_situation', 'house')
    sleep_association = personalization_vars.get('sleep_association', 'none')
    biggest_struggle = personalization_vars.get('biggest_struggle', 'frequent_waking')
    specific_challenge = personalization_vars.get('specific_challenge', '')

    # Age block mapping
    age_block_map = {
        '0-3_months': 'age_4_6_months',
        '4-6_months': 'age_4_6_months',
        '7-12_months': 'age_7_12_months',
        '13-18_months': 'age_13_18_months',
        '13-24_months': 'age_13_18_months',
        '19-24_months': 'age_19_24_months',
        '2_plus_years': 'age_19_24_months'
    }

    # Normalize baby_age for lookup
    age_key = baby_age.lower().replace(' ', '_').replace('-', '_')
    if '0' in age_key and '3' in age_key:
        age_key = '0-3_months'
    elif '4' in age_key and '6' in age_key:
        age_key = '4-6_months'
    elif '7' in age_key and '12' in age_key:
        age_key = '7-12_months'
    elif '13' in age_key and ('18' in age_key or '24' in age_key):
        age_key = '13-18_months'
    elif '19' in age_key or '24' in age_key:
        age_key = '19-24_months'
    else:
        age_key = '7-12_months'  # Default

    # Day-specific content block loading
    if day_number == 1:
        # Day 1: Welcome & Start
        # Age intro block
        intro_age_map = {
            '0-3_months': 'intro_age_4_6_months',
            '4-6_months': 'intro_age_4_6_months',
            '7-12_months': 'intro_age_7_12_months',
            '13-18_months': 'intro_age_13_18_months',
            '19-24_months': 'intro_age_19_24_months'
        }
        intro_block = intro_age_map.get(age_key, 'intro_age_7_12_months')
        content['age_intro_block'] = _get_email_content_block('intro', intro_block)

    elif day_number == 2:
        # Day 2: Sleep Environment
        env_block_map = {
            'apartment': 'environment_apartment',
            'room_sharing': 'environment_room_sharing',
            'sibling_sharing': 'environment_sibling_sharing',
            'house': 'environment_house'
        }
        env_block = env_block_map.get(living_situation, 'environment_house')
        content['environment_block'] = _get_email_content_block('environment', env_block)

    elif day_number == 3:
        # Day 3: Bedtime Routine
        # Sleep association routine block - check both sleep_association and specific_challenge
        assoc_block_map = {
            'nursing': 'routine_feeding_association',
            'rocking': 'routine_rocking_association',
            'pacifier': 'routine_pacifier_association'
        }
        # Map specific_challenge to association blocks
        specific_to_assoc = {
            'feeding': 'nursing',
            'rocking': 'rocking'
        }
        # Determine which association to use
        effective_association = sleep_association
        if sleep_association not in assoc_block_map and specific_challenge in specific_to_assoc:
            effective_association = specific_to_assoc[specific_challenge]

        if effective_association in assoc_block_map:
            content['routine_association_block'] = _get_email_content_block(
                'routine', assoc_block_map[effective_association]
            )

        # Work schedule routine block
        if work_schedule in ['working', 'shift_work']:
            content['routine_work_block'] = _get_email_content_block(
                'routine', 'routine_working_parent'
            )

        # Age-based routine
        if baby_age_category == 'toddler':
            content['routine_age_block'] = _get_email_content_block('routine', 'routine_age_toddler')
        else:
            content['routine_age_block'] = _get_email_content_block('routine', 'routine_age_baby')

    elif day_number == 4:
        # Day 4: Wake Windows
        age_block = age_block_map.get(age_key, 'age_7_12_months')
        content['age_based_content'] = _get_email_content_block('age', age_block)

        # Calculate first nap example based on age
        first_nap_times = {
            '4-6_months': '8:30-9:00 AM',
            '7-12_months': '9:00-9:30 AM',
            '13-18_months': '9:30-10:00 AM',
            '19-24_months': '10:00-10:30 AM'
        }
        content['first_nap_example'] = first_nap_times.get(age_key, '9:00-9:30 AM')

    elif day_number == 5:
        # Day 5: Method Introduction (The Big Night)
        # Method instructions
        if method_type == 'cio':
            method_block = 'method_cio'
        elif method_type == 'not_sure':
            method_block = 'method_hybrid'
        else:
            method_block = 'method_gentle'
        content['method_instructions'] = _get_email_content_block('method', method_block)

        # Parenting setup blocks
        if parenting_setup == 'single':
            content['method_single_parent_block'] = _get_email_content_block(
                'method', 'method_single_parent'
            )
        elif parenting_setup == 'two_sharing':
            content['method_partner_alignment_block'] = _get_email_content_block(
                'method', 'method_partner_alignment'
            )

        # Living situation method blocks
        if living_situation == 'apartment':
            apt_block = f'method_{method_type}_apartment'
            content['method_apartment_block'] = _get_email_content_block('method', apt_block)
        elif living_situation == 'room_sharing':
            room_block = f'method_{method_type}_room_sharing'
            content['method_room_sharing_block'] = _get_email_content_block('method', room_block)

        # Age expectations
        if baby_age_category == 'toddler':
            content['age_expectation_block'] = _get_email_content_block(
                'method', 'method_age_expectations_toddler'
            )
        else:
            content['age_expectation_block'] = _get_email_content_block(
                'method', 'method_age_expectations_baby'
            )

    elif day_number == 6:
        # Day 6: Troubleshooting
        # Method-specific troubleshooting
        ts_method = 'troubleshoot_cio' if method_type == 'cio' else 'troubleshoot_gentle'
        content['troubleshoot_method_block'] = _get_email_content_block('troubleshoot', ts_method)

        # Parenting setup troubleshooting
        if parenting_setup == 'single':
            content['troubleshoot_single_parent_block'] = _get_email_content_block(
                'troubleshoot', 'troubleshoot_single_parent'
            )

        # Living situation troubleshooting
        if living_situation == 'apartment':
            content['troubleshoot_apartment_block'] = _get_email_content_block(
                'troubleshoot', 'troubleshoot_apartment'
            )

        # Challenge-specific troubleshooting
        if biggest_struggle == 'early_morning':
            content['troubleshoot_early_morning_block'] = _get_email_content_block(
                'troubleshoot', 'troubleshoot_early_morning'
            )
        elif biggest_struggle == 'frequent_waking':
            content['troubleshoot_frequent_waking_block'] = _get_email_content_block(
                'troubleshoot', 'troubleshoot_frequent_waking'
            )

    elif day_number == 7:
        # Day 7: Finding Wins
        # Challenge-specific wins
        wins_map = {
            'frequent_waking': 'wins_frequent_waker',
            'early_morning': 'wins_early_morning',
            'naps': 'wins_nap_disaster',
            'bedtime_battles': 'wins_bedtime_battle'
        }
        wins_block = wins_map.get(biggest_struggle, 'wins_frequent_waker')
        content['wins_challenge_block'] = _get_email_content_block('wins', wins_block)

        # Working parent wins
        if work_schedule in ['working', 'shift_work', 'wfh']:
            content['wins_work_block'] = _get_email_content_block('wins', 'wins_working_parent')

    elif day_number == 8:
        # Day 8: Naps Deep Dive
        # Challenge-based content
        challenge_block_map = {
            'feeding': 'challenge_feeding',
            'motion': 'challenge_motion',
            'pacifier': 'challenge_pacifier',
            'naps': 'challenge_naps',
            'early_morning': 'challenge_early_morning'
        }
        challenge_block = challenge_block_map.get(challenge_type, '')
        if challenge_block:
            content['challenge_based_content'] = _get_email_content_block('challenge', challenge_block)

        # Age-specific naps
        naps_age_map = {
            '4-6_months': 'naps_age_4_6_months',
            '7-12_months': 'naps_age_7_12_months',
            '13-18_months': 'naps_age_13_18_months',
            '19-24_months': 'naps_age_13_18_months'
        }
        naps_block = naps_age_map.get(age_key, 'naps_age_7_12_months')
        content['naps_age_block'] = _get_email_content_block('naps', naps_block)

        # Working parent naps
        if work_schedule in ['working', 'shift_work']:
            content['naps_working_parent_block'] = _get_email_content_block(
                'naps', 'naps_working_parent'
            )

    elif day_number == 9:
        # Day 9: Sleep Regressions
        # Age-specific regression
        regression_age_map = {
            '4-6_months': 'regression_4_6_months',
            '7-12_months': 'regression_7_12_months',
            '13-18_months': 'regression_13_18_months',
            '19-24_months': 'regression_13_18_months'
        }
        regression_block = regression_age_map.get(age_key, 'regression_7_12_months')
        content['regression_age_block'] = _get_email_content_block('regression', regression_block)

        # Parenting setup regression
        if parenting_setup == 'single':
            content['regression_single_parent_block'] = _get_email_content_block(
                'regression', 'regression_single_parent'
            )

        # Living situation regression
        if living_situation == 'apartment':
            content['regression_apartment_block'] = _get_email_content_block(
                'regression', 'regression_apartment'
            )

    elif day_number == 10:
        # Day 10: Pacifier Problem
        # Check sleep_association, challenge_type, and specific_challenge for pacifier relevance
        is_pacifier_issue = (
            sleep_association == 'pacifier' or
            challenge_type == 'pacifier' or
            specific_challenge == 'pacifier'
        )
        if is_pacifier_issue:
            content['pacifier_main_challenge_block'] = _get_email_content_block(
                'pacifier', 'pacifier_main_challenge'
            )
        else:
            content['pacifier_not_relevant_block'] = _get_email_content_block(
                'pacifier', 'pacifier_not_relevant'
            )

    elif day_number == 11:
        # Day 11: Feeding to Sleep
        # Check sleep_association, challenge_type, and specific_challenge for feeding relevance
        is_feeding_issue = (
            sleep_association == 'nursing' or
            challenge_type == 'feeding' or
            specific_challenge == 'feeding'
        )
        if is_feeding_issue:
            content['feeding_main_challenge_block'] = _get_email_content_block(
                'feeding', 'feeding_main_challenge'
            )
        else:
            content['feeding_not_relevant_block'] = _get_email_content_block(
                'feeding', 'feeding_not_relevant'
            )

        # Night feed needs by age
        if age_key in ['0-3_months', '4-6_months']:
            content['feeding_night_needs_baby_block'] = _get_email_content_block(
                'feeding', 'feeding_night_needs_baby'
            )
        else:
            content['feeding_night_needs_older_block'] = _get_email_content_block(
                'feeding', 'feeding_night_needs_older'
            )

    elif day_number == 12:
        # Day 12: Night Weaning
        # Age-appropriate weaning
        if age_key in ['0-3_months', '4-6_months']:
            content['weaning_too_young_block'] = _get_email_content_block(
                'weaning', 'weaning_too_young'
            )
        else:
            content['weaning_ready_block'] = _get_email_content_block('weaning', 'weaning_ready')

        # Frequent waker weaning emphasis
        if biggest_struggle == 'frequent_waking':
            content['weaning_frequent_waker_block'] = _get_email_content_block(
                'weaning', 'weaning_frequent_waker'
            )

        # Single parent weaning
        if parenting_setup == 'single':
            content['weaning_single_parent_block'] = _get_email_content_block(
                'weaning', 'weaning_single_parent'
            )

    elif day_number == 13:
        # Day 13: Life Disruptions
        # Work travel
        if work_schedule in ['working', 'shift_work']:
            content['disruption_work_travel_block'] = _get_email_content_block(
                'disruption', 'disruption_work_travel'
            )

        # Sibling sharing
        if living_situation == 'sibling_sharing':
            content['disruption_siblings_block'] = _get_email_content_block(
                'disruption', 'disruption_siblings'
            )

        # Grandparents (always include - universal concern)
        content['disruption_grandparents_block'] = _get_email_content_block(
            'disruption', 'disruption_grandparents'
        )

        # Situation-based content (existing blocks)
        situation = personalization_vars.get('situation', '')
        if situation == 'room_sharing':
            content['situation_based_content'] = _get_email_content_block(
                'situation', 'situation_room_sharing'
            )
        elif situation == 'apartment':
            content['situation_based_content'] = _get_email_content_block(
                'situation', 'situation_apartment'
            )

    elif day_number == 14:
        # Day 14: Celebration & Future
        # Parenting celebration
        if parenting_setup == 'single':
            content['celebration_single_parent_block'] = _get_email_content_block(
                'celebration', 'celebration_single_parent'
            )

        # Work celebration
        if work_schedule in ['working', 'shift_work', 'wfh']:
            content['celebration_working_parent_block'] = _get_email_content_block(
                'celebration', 'celebration_working_parent'
            )

        # Challenge-specific celebration
        celebration_map = {
            'frequent_waking': 'celebration_frequent_waker',
            'early_morning': 'celebration_early_waker',
            'naps': 'celebration_nap_disaster'
        }
        celebration_block = celebration_map.get(biggest_struggle, 'celebration_frequent_waker')
        content['celebration_challenge_block'] = _get_email_content_block(
            'celebration', celebration_block
        )

        # Future content by age
        if baby_age_category == 'toddler':
            content['future_age_block'] = _get_email_content_block('future', 'future_toddler')
        else:
            content['future_age_block'] = _get_email_content_block('future', 'future_baby')

    return content


def get_sequence_content(day_number, customer_name, personalization_vars=None, order_id=None, customer_id=None, customer_email=None):
    """
    Get email content for the new 14-day sequence.
    Loads from new_day_X.html templates and injects dynamic content.

    Args:
        day_number: Day in sequence (1-14)
        customer_name: Customer name
        personalization_vars: Dict of personalization variables
        order_id: Order ID
        customer_id: Customer ID for unsubscribe link
        customer_email: Customer email for unsubscribe link

    Returns:
        dict: Email content with subject, text_body, html_body
    """
    template_file = f'new_day_{day_number}.html'
    template_path = os.path.join(os.path.dirname(__file__), '..', 'email_templates', template_file)

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Load all content blocks for this day
        content_blocks = _load_day_content_blocks(day_number, personalization_vars)

        # Inject content blocks into template
        for placeholder, content in content_blocks.items():
            html_content = html_content.replace(f'{{{placeholder}}}', content)

        # Process conditional sections (IF/ELSE/ENDIF)
        html_content = _parse_conditional_sections(html_content, personalization_vars)

        # Replace simple placeholders
        html_content = html_content.replace('{customer_name}', customer_name or 'there')

        if personalization_vars:
            # Method
            html_content = html_content.replace(
                '{method}',
                personalization_vars.get('method_short', personalization_vars.get('method', 'your chosen method'))
            )

            # Baby age
            html_content = html_content.replace(
                '{baby_age_short}',
                personalization_vars.get('baby_age_short', 'your baby')
            )

            # Biggest challenge text
            html_content = html_content.replace(
                '{biggest_challenge_text}',
                personalization_vars.get('biggest_challenge_text', 'struggling with sleep')
            )

            # Sleep association text
            html_content = html_content.replace(
                '{sleep_association_text}',
                personalization_vars.get('sleep_association_text', '')
            )

            # Parenting context
            html_content = html_content.replace(
                '{parenting_setup_context}',
                personalization_vars.get('parenting_setup_context', '')
            )

            # Work context
            html_content = html_content.replace(
                '{work_schedule_context}',
                personalization_vars.get('work_schedule_context', '')
            )

            # Living situation context
            html_content = html_content.replace(
                '{living_situation_context}',
                personalization_vars.get('living_situation_context', '')
            )

            # Challenge type for conditional sections
            html_content = html_content.replace(
                '{challenge_type}',
                personalization_vars.get('challenge_type', '')
            )

            # Baby age category
            html_content = html_content.replace(
                '{baby_age_category}',
                personalization_vars.get('baby_age_category', 'baby')
            )
        else:
            # Default replacements when no personalization
            html_content = html_content.replace('{method}', 'your chosen method')
            html_content = html_content.replace('{baby_age_short}', 'your baby')
            html_content = html_content.replace('{biggest_challenge_text}', 'struggling with sleep')
            html_content = html_content.replace('{sleep_association_text}', '')
            html_content = html_content.replace('{parenting_setup_context}', '')
            html_content = html_content.replace('{work_schedule_context}', '')
            html_content = html_content.replace('{living_situation_context}', '')
            html_content = html_content.replace('{challenge_type}', '')
            html_content = html_content.replace('{baby_age_category}', 'baby')

        # Replace first_nap_example from content blocks (Day 4)
        if 'first_nap_example' in content_blocks:
            html_content = html_content.replace(
                '{first_nap_example}',
                content_blocks.get('first_nap_example', '9:00 AM')
            )

        # Order ID
        if order_id:
            html_content = html_content.replace('{{order_id}}', str(order_id))

        # Unsubscribe URL
        if customer_id and customer_email:
            from routes.email_routes import get_unsubscribe_url
            unsubscribe_url = get_unsubscribe_url(customer_id, customer_email)
            html_content = html_content.replace('{{unsubscribe_url}}', unsubscribe_url)
        else:
            # Fallback to support email if no customer info
            html_content = html_content.replace('{{unsubscribe_url}}', 'mailto:support@napocalypse.com?subject=Unsubscribe')

        # Clean up any unused placeholders to avoid them showing up in the email
        unused_placeholders = [
            '{age_based_content}', '{challenge_based_content}', '{situation_based_content}',
            '{method_instructions}', '{age_intro_block}', '{environment_block}',
            '{routine_association_block}', '{routine_work_block}', '{routine_age_block}',
            '{method_single_parent_block}', '{method_partner_alignment_block}',
            '{method_apartment_block}', '{method_room_sharing_block}',
            '{age_expectation_block}', '{troubleshoot_method_block}',
            '{troubleshoot_single_parent_block}', '{troubleshoot_apartment_block}',
            '{troubleshoot_early_morning_block}', '{troubleshoot_frequent_waking_block}',
            '{wins_challenge_block}', '{wins_work_block}',
            '{naps_age_block}', '{naps_working_parent_block}',
            '{regression_age_block}', '{regression_single_parent_block}',
            '{regression_apartment_block}',
            '{pacifier_main_challenge_block}', '{pacifier_not_relevant_block}',
            '{feeding_main_challenge_block}', '{feeding_not_relevant_block}',
            '{feeding_night_needs_baby_block}', '{feeding_night_needs_older_block}',
            '{weaning_too_young_block}', '{weaning_ready_block}',
            '{weaning_frequent_waker_block}', '{weaning_single_parent_block}',
            '{disruption_work_travel_block}', '{disruption_siblings_block}',
            '{disruption_grandparents_block}',
            '{celebration_single_parent_block}', '{celebration_working_parent_block}',
            '{celebration_challenge_block}', '{future_age_block}',
            '{first_nap_example}',
            # Additional placeholders that might be unused
            '{challenge_type}', '{baby_age_category}',
            '{parenting_setup}', '{work_schedule}', '{living_situation}',
            '{sleep_association}'
        ]

        for placeholder in unused_placeholders:
            html_content = html_content.replace(placeholder, '')

        # Generate subject lines
        subjects = {
            1: "Day 1: Welcome to Your Sleep Transformation",
            2: "Day 2: The Perfect Sleep Environment",
            3: "Day 3: The Magic of a Bedtime Routine",
            4: "Day 4: Understanding Wake Windows",
            5: "Day 5: Tonight's the Night - Your Sleep Training Method",
            6: "Day 6: Troubleshooting & Staying Strong",
            7: "Day 7: Finding the Wins",
            8: "Day 8: The Tricky World of Naps",
            9: "Day 9: The Dreaded Sleep Regression",
            10: "Day 10: The Pacifier Problem",
            11: "Day 11: Breaking the Feed-to-Sleep Association",
            12: "Day 12: A Guide to Night Weaning",
            13: "Day 13: Life Happens - Staying on Track",
            14: "Day 14: You Did It! What's Next?"
        }
        subject = subjects.get(day_number, f"Day {day_number}: Your Napocalypse Update")
        text_body = "This email is best viewed in HTML format. If you're having trouble, please contact support."

        return {
            'subject': subject,
            'text_body': text_body,
            'html_body': html_content
        }

    except Exception as e:
        print(f"Error loading or personalizing email template for day {day_number}: {str(e)}")
        # Fallback content
        return {
            'subject': f"Day {day_number}: Your Napocalypse Update",
            'text_body': "There was an error loading the email content. Please contact support.",
            'html_body': f"<h2>Hi {customer_name or 'there'}!</h2><p>There was an error loading the content for Day {day_number}. Please contact our support team for assistance.</p>"
        }

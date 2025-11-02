"""
Email Service using AWS SES
Handles delivery emails and automated sequences
"""

import os
import boto3
from botocore.exceptions import ClientError
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
    Send initial delivery email with PDF attachment
    """
    from_email = Config.AWS_SES_FROM_EMAIL
    
    # Personalized subject line
    if customer_name:
        subject = f"🌙 {customer_name}, your personalized sleep guide is ready!"
    else:
        subject = "🌙 Your personalized sleep guide is ready!"
    
    # HTML body
    html_body = f"""
    <html>
    <head></head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2c3e50;">Hi {customer_name}!</h2>
            
            <p>Your personalized sleep guide is attached and ready to go!</p>
            
            <div style="background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #2c3e50;">Your Custom Guide Includes:</h3>
                <ul>
                    <li>✓ Personalized for your baby's age and situation</li>
                    <li>✓ {len(modules)} targeted modules just for you</li>
                    <li>✓ Step-by-step action plan</li>
                    <li>✓ Troubleshooting guide</li>
                </ul>
            </div>
            
            <h3 style="color: #2c3e50;">What to Do First:</h3>
            <ol>
                <li>Read the introduction (page 1)</li>
                <li>Review your personalized approach</li>
                <li>Set up your baby's environment</li>
                <li>Start tonight!</li>
            </ol>
            
            <p>Tomorrow, I'll send you Day 1 implementation tips.</p>
            
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
    
    # Text body
    text_body = f"""
    Hi {customer_name}!
    
    Your personalized sleep guide is attached and ready to go!
    
    Your Custom Guide Includes:
    - Personalized for your baby's age and situation
    - {len(modules)} targeted modules just for you
    - Step-by-step action plan
    - Troubleshooting guide
    
    What to Do First:
    1. Read the introduction (page 1)
    2. Review your personalized approach
    3. Set up your baby's environment
    4. Start tonight!
    
    Tomorrow, I'll send you Day 1 implementation tips.
    
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
        
        # Add PDF attachment
        attachment = MIMEApplication(pdf_data)
        attachment.add_header('Content-Disposition', 'attachment', 
                            filename='Your_Personalized_Sleep_Guide.pdf')
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

def send_sequence_email(customer_id, day_number):
    """
    Send specific day email in the sequence
    """
    from database import Customer
    customer = Customer.query.get(customer_id)
    
    if not customer:
        print(f"Customer {customer_id} not found")
        return False
    
    # Get email content with personalization
    email_content = get_sequence_content(day_number, customer.name, customer.baby_name)
    
    try:
        response = ses_client.send_email(
            Source=Config.AWS_SES_FROM_EMAIL,
            Destination={
                'ToAddresses': [customer.email]
            },
            Message={
                'Subject': {'Data': email_content['subject']},
                'Body': {
                    'Html': {'Data': email_content['html_body']},
                    'Text': {'Data': email_content['text_body']}
                }
            }
        )
        
        print(f"Email sent successfully to {customer.email}")
        return True
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def schedule_email_sequence(customer_id, order_id):
    """
    Schedule 7-day email sequence
    """
    try:
        # Get customer for email personalization
        from database import Customer
        customer = Customer.query.get(customer_id)
        
        for day in range(1, 8):
            scheduled_time = datetime.utcnow() + timedelta(days=day)
            
            email_seq = EmailSequence(
                customer_id=customer_id,
                order_id=order_id,
                day_number=day,
                email_type=f'day{day}',
                subject=get_sequence_content(day, customer.name if customer else None, customer.baby_name if customer else None)['subject'],
                scheduled_for=scheduled_time,
                status='pending'
            )
            db.session.add(email_seq)
        
        db.session.commit()
        print(f"Scheduled 7-day email sequence for customer {customer_id}")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Error scheduling email sequence: {str(e)}")
        return False

def generate_personalized_subject(day_number, customer_name=None, baby_name=None):
    """
    Generate highly optimized, personalized subject lines for maximum open rates
    """
    # Fallback names for personalization
    parent_name = customer_name or ""
    child_name = baby_name or "your baby"
    
    subjects = {
        1: {
            # High urgency + personal + benefit
            'both': f"🌙 {parent_name}, {child_name}'s sleep guide is here!",
            'parent_only': f"🌙 {parent_name}, your personalized sleep guide is ready!",
            'baby_only': f"🌙 {child_name}'s personalized sleep guide is here!",
            'neither': "🌙 Your personalized sleep guide is ready!"
        },
        2: {
            # Question + urgency + personal
            'both': f"✅ {parent_name}, ready for {child_name}'s first night?",
            'parent_only': f"✅ {parent_name}, ready for night 1? Here's your checklist",
            'baby_only': f"✅ Ready for {child_name}'s first sleep training night?",
            'neither': "✅ Ready for night 1? Your checklist inside"
        },
        3: {
            # Problem-focused + solution hint + personal
            'both': f"🛠️ {parent_name}, tough night with {child_name}? Quick fixes inside",
            'parent_only': f"🛠️ {parent_name}, struggling? Here's what to do next",
            'baby_only': f"🛠️ {child_name} having a tough time? Solutions inside",
            'neither': "🛠️ Rough night? Here's exactly what to do"
        },
        4: {
            # Social proof + encouragement + personal
            'both': f"⭐ {parent_name}, proof that you and {child_name} can do this!",
            'parent_only': f"⭐ {parent_name}, real success stories (you're next!)",
            'baby_only': f"⭐ Success stories: babies like {child_name} who made it!",
            'neither': "⭐ Real success stories (you can do this too!)"
        },
        5: {
            # Crisis help + immediacy + personal
            'both': f"🔧 {parent_name}, your 2AM lifeline for {child_name}",
            'parent_only': f"🔧 {parent_name}, emergency help for tough nights",
            'baby_only': f"🔧 When {child_name} won't sleep: your emergency guide",
            'neither': "🔧 Emergency help: what to do at 2AM"
        },
        6: {
            # Advancement + exclusivity + personal
            'both': f"📚 {parent_name}, advanced secrets for {child_name}'s sleep",
            'parent_only': f"📚 {parent_name}, expert sleep secrets revealed",
            'baby_only': f"📚 Next-level sleep tips for {child_name}",
            'neither': "📚 Expert sleep secrets (most parents don't know these)"
        },
        7: {
            # Achievement + celebration + future + personal
            'both': f"🎉 {parent_name}, you and {child_name} did it! What's next?",
            'parent_only': f"🎉 {parent_name}, you made it! Share your success?",
            'baby_only': f"🎉 {child_name} is sleeping! Your success story inside",
            'neither': "🎉 You did it! Share your success story?"
        }
    }
    
    day_subjects = subjects.get(day_number, subjects[1])
    
    # Choose best subject based on available data
    if customer_name and baby_name:
        return day_subjects['both']
    elif customer_name:
        return day_subjects['parent_only']
    elif baby_name:
        return day_subjects['baby_only']
    else:
        return day_subjects['neither']

def get_sequence_content(day_number, customer_name=None, baby_name=None):
    """
    Get email content for specific day with personalization
    """
    # Map day numbers to template files and personalized subjects
    templates = {
        1: {
            'file': 'day_1_welcome.html',
            'subject': generate_personalized_subject(1, customer_name, baby_name)
        },
        2: {
            'file': 'day_2_getting_started.html', 
            'subject': generate_personalized_subject(2, customer_name, baby_name)
        },
        3: {
            'file': 'day_3_common_challenges.html',
            'subject': generate_personalized_subject(3, customer_name, baby_name)
        },
        4: {
            'file': 'day_4_success_stories.html',
            'subject': generate_personalized_subject(4, customer_name, baby_name)
        },
        5: {
            'file': 'day_5_troubleshooting.html',
            'subject': generate_personalized_subject(5, customer_name, baby_name)
        },
        6: {
            'file': 'day_6_additional_resources.html',
            'subject': generate_personalized_subject(6, customer_name, baby_name)
        },
        7: {
            'file': 'day_7_feedback.html',
            'subject': generate_personalized_subject(7, customer_name, baby_name)
        }
    }
    
    template_info = templates.get(day_number, templates[1])
    
    # Load HTML template
    template_path = os.path.join(os.path.dirname(__file__), '..', 'email_templates', template_info['file'])
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Apply personalization to template content
        personalized_html = personalize_email_content(html_content, customer_name, baby_name)
        
        # Generate plain text version (simplified)
        text_content = f"""
Hi {customer_name or 'there'}!

This is Day {day_number} of your Napocalypse email series.

For the best experience, please view this email in HTML format.

If you can't see the HTML version, visit napocalypse.com for support.

Best,
The Napocalypse Team
        """
        
        return {
            'subject': template_info['subject'],
            'text_body': text_content.strip(),
            'html_body': personalized_html
        }
        
    except Exception as e:
        print(f"Error loading email template: {str(e)}")
        # Fallback content
        return {
            'subject': template_info['subject'],
            'text_body': f"Hi {customer_name or 'there'}!\n\nDay {day_number} content...",
            'html_body': f"<h2>Hi {customer_name or 'there'}!</h2><p>Day {day_number} content...</p>"
        }

def personalize_email_content(html_content, customer_name=None, baby_name=None):
    """
    Apply personalization to email template content
    """
    # Fallback names
    parent_name = customer_name or "there"
    child_name = baby_name or "your baby"
    
    # Common greeting replacements
    html_content = html_content.replace("Hi there!", f"Hi {parent_name}!")
    html_content = html_content.replace("Hey there!", f"Hey {parent_name}!")
    html_content = html_content.replace("Good morning!", f"Good morning, {parent_name}!")
    html_content = html_content.replace("Wow!", f"Wow, {parent_name}!")
    
    # Baby-specific replacements (only if baby name is provided)
    if baby_name:
        html_content = html_content.replace("your baby", child_name)
        html_content = html_content.replace("Your baby", child_name)
        html_content = html_content.replace("Baby's", f"{child_name}'s")
        html_content = html_content.replace("baby's", f"{child_name}'s")
        html_content = html_content.replace("the baby", child_name)
        html_content = html_content.replace("My baby", child_name)
        html_content = html_content.replace("my baby", child_name)
        # Add more specific patterns
        html_content = html_content.replace("sleep training", f"{child_name}'s sleep training")
        html_content = html_content.replace("first night", f"{child_name}'s first night")
    
    # Parent name in encouragement (only if parent name is provided)
    if customer_name:
        html_content = html_content.replace("You've got this!", f"You've got this, {customer_name}!")
        html_content = html_content.replace("You're doing great", f"You're doing great, {customer_name}")
        html_content = html_content.replace("Hang in there!", f"Hang in there, {customer_name}!")
        html_content = html_content.replace("You're ready!", f"You're ready, {customer_name}!")
    
    return html_content
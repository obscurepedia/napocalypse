"""
Email Service using AWS SES
Handles delivery emails and automated sequences
"""

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
    subject = "Your Personalized Baby Sleep Guide is Ready! 🌙"
    
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

def send_sequence_email(to_email, customer_name, day_number):
    """
    Send automated sequence email (Days 1-7)
    """
    from_email = Config.AWS_SES_FROM_EMAIL
    
    # Email content based on day
    email_content = get_sequence_content(day_number, customer_name)
    
    try:
        response = ses_client.send_email(
            Source=from_email,
            Destination={'ToAddresses': [to_email]},
            Message={
                'Subject': {'Data': email_content['subject']},
                'Body': {
                    'Text': {'Data': email_content['text']},
                    'Html': {'Data': email_content['html']}
                }
            }
        )
        
        print(f"Day {day_number} email sent to {to_email}. Message ID: {response['MessageId']}")
        return True
        
    except ClientError as e:
        print(f"Error sending sequence email: {e.response['Error']['Message']}")
        return False

def schedule_email_sequence(customer_id, order_id):
    """
    Schedule 7-day email sequence
    """
    try:
        for day in range(1, 8):
            scheduled_time = datetime.utcnow() + timedelta(days=day)
            
            email_seq = EmailSequence(
                customer_id=customer_id,
                order_id=order_id,
                day_number=day,
                email_type=f'day{day}',
                subject=get_sequence_content(day, '')['subject'],
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

def get_sequence_content(day_number, customer_name):
    """
    Get email content for specific day in sequence
    Loads from HTML template files
    """
    import os
    
    # Map day numbers to template files and subjects
    templates = {
        1: {
            'file': 'day_1_welcome.html',
            'subject': "🌙 Welcome to Napocalypse! Your Guide is Here"
        },
        2: {
            'file': 'day_2_getting_started.html',
            'subject': "✅ Day 2: Your First Night Checklist"
        },
        3: {
            'file': 'day_3_common_challenges.html',
            'subject': "🛠️ Day 3: Common Challenges & How to Fix Them"
        },
        4: {
            'file': 'day_4_success_stories.html',
            'subject': "⭐ Day 4: Real Success Stories (You Can Do This!)"
        },
        5: {
            'file': 'day_5_troubleshooting.html',
            'subject': "🔧 Day 5: Your 2AM Troubleshooting Guide"
        },
        6: {
            'file': 'day_6_additional_resources.html',
            'subject': "📚 Day 6: Expert Tips & Additional Resources"
        },
        7: {
            'file': 'day_7_feedback.html',
            'subject': "🎉 Day 7: You Made It! (Plus What's Next)"
        }
    }
    
    template_info = templates.get(day_number, templates[1])
    
    # Load HTML template
    template_path = os.path.join(os.path.dirname(__file__), '..', 'email_templates', template_info['file'])
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Replace placeholder with customer name if needed
        html_content = html_content.replace('{customer_name}', customer_name)
        
        # Generate plain text version (simplified)
        text_content = f"""
Hi {customer_name}!

This is Day {day_number} of your Napocalypse email series.

For the best experience, please view this email in HTML format.

If you can't see the HTML version, visit napocalypse.com for support.

Best,
The Napocalypse Team
        """
        
        return {
            'subject': template_info['subject'],
            'text': text_content.strip(),
            'html': html_content
        }
        
    except Exception as e:
        print(f"Error loading email template: {str(e)}")
        # Fallback content
        return {
            'subject': template_info['subject'],
            'text': f"Hi {customer_name}!\n\nDay {day_number} content...",
            'html': f"<h2>Hi {customer_name}!</h2><p>Day {day_number} content...</p>"
        }
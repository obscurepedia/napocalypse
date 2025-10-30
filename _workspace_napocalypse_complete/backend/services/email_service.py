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
    """
    content = {
        1: {
            'subject': "Day 1: Let's Start Your Baby's Sleep Transformation 🌟",
            'text': f"Hi {customer_name}!\n\nDay 1 implementation tips...",
            'html': f"<h2>Hi {customer_name}!</h2><p>Day 1 implementation tips...</p>"
        },
        2: {
            'subject': "Day 2: Age-Specific Sleep Tips You Need to Know",
            'text': f"Hi {customer_name}!\n\nDay 2 content...",
            'html': f"<h2>Hi {customer_name}!</h2><p>Day 2 content...</p>"
        },
        3: {
            'subject': "Day 3: Mastering Your Sleep Training Method",
            'text': f"Hi {customer_name}!\n\nDay 3 content...",
            'html': f"<h2>Hi {customer_name}!</h2><p>Day 3 content...</p>"
        },
        4: {
            'subject': "Day 4: Solving Your Specific Challenge",
            'text': f"Hi {customer_name}!\n\nDay 4 content...",
            'html': f"<h2>Hi {customer_name}!</h2><p>Day 4 content...</p>"
        },
        5: {
            'subject': "Day 5: Handling Setbacks & Staying Consistent",
            'text': f"Hi {customer_name}!\n\nDay 5 content...",
            'html': f"<h2>Hi {customer_name}!</h2><p>Day 5 content...</p>"
        },
        6: {
            'subject': "Day 6: Progress Check-In - How's It Going?",
            'text': f"Hi {customer_name}!\n\nDay 6 content...",
            'html': f"<h2>Hi {customer_name}!</h2><p>Day 6 content...</p>"
        },
        7: {
            'subject': "Day 7: You Did It! What's Next?",
            'text': f"Hi {customer_name}!\n\nDay 7 content with upsell...",
            'html': f"<h2>Hi {customer_name}!</h2><p>Day 7 content with upsell...</p>"
        }
    }
    
    return content.get(day_number, content[1])
"""
Email Service using AWS SES
Handles delivery emails and automated sequences
"""

import os
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
    from_email = Config.AWS_SES_FROM_EMAIL
    
    # Safe customer name handling
    safe_customer_name = customer_name if customer_name else "there"
    
    # New subject line for the Quick-Start Guide
    subject = f"🚀 Your Quick-Start Guide to Better Sleep is Here!"
    
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
                <p>This guide is your "instant gratification" to get you started immediately. Your comprehensive 14-day email coaching course begins tomorrow.</p>
                <ul>
                    <li>✓ <strong>Today:</strong> Read the Quick-Start Guide and try the "One Thing".</li>
                    <li>✓ <strong>Tomorrow:</strong> Look for the "Day 1" email in your inbox.</li>
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
    Send automated sequence email (Days 1-14) with full personalization
    
    Args:
        to_email: Recipient email
        customer_name: Customer name
        day_number: Day in sequence (1-14)
        order_id: Order ID for personalization
        customer_id: Customer ID (for upsell URL)
        modules: List of module names
        quiz_data: Quiz response data (for personalization)
        customer: Customer object (for full personalization)
    """
    from_email = Config.AWS_SES_FROM_EMAIL
    
    # Get personalization data if available
    personalization_vars = None
    if customer and quiz_data and modules:
        from services.personalization import get_personalization_data
        personalization_vars = get_personalization_data(customer, quiz_data, modules)
    
    # Email content based on day and personalization
    email_content = get_sequence_content(day_number, customer_name, personalization_vars, order_id)
    
    # Add upsell URL to emails if customer_id and modules provided
    if customer_id and modules:
        module_ids = ','.join(modules)
        upsell_url = f"https://napocalypse.com/upsell?customer={customer_id}&modules={module_ids}"
        
        # Replace upsell placeholder in content
        if 'html_body' in email_content:
            email_content['html_body'] = email_content['html_body'].replace(
                '{{upsell_url}}', 
                upsell_url
            )
        if 'text_body' in email_content:
            email_content['text_body'] = email_content['text_body'].replace(
                '{{upsell_url}}', 
                upsell_url
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

def send_advanced_playbook_module(delivery_id: int):
    """
    Send an Advanced Playbook module delivery email
    
    Args:
        delivery_id: AdvancedPlaybookDelivery record ID
    """
    from database import AdvancedPlaybookDelivery, Customer
    from services.module_selector import get_module_info
    from services.personalization import get_personalization_data
    import os
    
    delivery = AdvancedPlaybookDelivery.query.get(delivery_id)
    if not delivery:
        print(f"Delivery {delivery_id} not found")
        return False
    
    customer = Customer.query.get(delivery.customer_id)
    if not customer:
        print(f"Customer {delivery.customer_id} not found")
        return False
    
    # Get personalization data
    from database import QuizResponse, ModuleAssigned
    quiz = QuizResponse.query.filter_by(customer_id=customer.id).first()
    modules = [m.module_name for m in ModuleAssigned.query.filter_by(customer_id=customer.id).all()]
    
    personalization_vars = get_personalization_data(customer, quiz.to_dict() if quiz else {}, modules)
    
    # Determine which email template to use
    if delivery.module_number == 1:
        template_name = 'day_7_immediate_module_1.html'
    elif delivery.module_number == 2:
        template_name = 'day_14_module_2.html'
    elif delivery.module_number == 3:
        template_name = 'day_21_module_3.html'
    elif delivery.module_number == 4:
        template_name = 'day_28_module_4.html'
    elif delivery.module_number == 5:
        template_name = 'day_32_completion.html'
    else:
        print(f"Invalid module number: {delivery.module_number}")
        return False
    
    # Load email template
    template_path = os.path.join(os.path.dirname(__file__), 
                                 '../email_templates/advanced_delivery', 
                                 template_name)
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Personalize content
        html_content = html_content.replace('{customer_name}', personalization_vars.get('customer_name', 'there'))
        html_content = html_content.replace('{method}', personalization_vars.get('method', 'Sleep Training'))
        html_content = html_content.replace('{challenge}', personalization_vars.get('challenge', 'Sleep Challenge'))
        
        # Generate subject line
        if delivery.module_number == 1:
            subject = f"📚 Your Advanced {personalization_vars.get('method', 'Sleep Training')} Playbook - Module 1"
        elif delivery.module_number == 2:
            subject = f"📚 Week 2: Advanced {personalization_vars.get('challenge', 'Sleep')} Mastery"
        elif delivery.module_number == 3:
            subject = "📚 Week 3: Complete Nap Training Guide"
        elif delivery.module_number == 4:
            subject = "🎉 Week 4: Your Complete Library!"
        elif delivery.module_number == 5:
            subject = f"🎓 Congratulations, {personalization_vars.get('method', 'Sleep Training')} Expert!"
        
        # Generate PDF for modules 1-4
        pdf_path = None
        if delivery.module_number <= 4:
            from services.pdf_generator import generate_personalized_pdf
            pdf_path = generate_personalized_pdf(
                customer=customer,
                quiz_data=quiz.to_dict() if quiz else {},
                modules=[delivery.module_name],
                is_upsell=True  # Use FULL content
            )
        
        # Send email with PDF attachment
        if pdf_path and delivery.module_number <= 4:
            # Send with attachment
            send_email_with_attachment(
                to_email=customer.email,
                subject=subject,
                html_content=html_content,
                attachment_path=pdf_path
            )
        else:
            # Send without attachment (completion email)
            ses_client.send_email(
                Source=Config.AWS_SES_FROM_EMAIL,
                Destination={'ToAddresses': [customer.email]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {'Html': {'Data': html_content}}
                }
            )
        
        # Update delivery status
        delivery.status = 'delivered'
        delivery.delivered_date = datetime.utcnow()
        db.session.commit()
        
        print(f"Advanced Playbook module {delivery.module_number} delivered to {customer.email}")
        return True
        
    except Exception as e:
        print(f"Error sending Advanced Playbook module: {str(e)}")
        delivery.status = 'failed'
        db.session.commit()
        return False


def send_email_with_attachment(to_email: str, subject: str, html_content: str, attachment_path: str):
    """
    Send email with PDF attachment using AWS SES
    """
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.application import MIMEApplication
    import os
    
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = Config.AWS_SES_FROM_EMAIL
    msg['To'] = to_email
    
    # Add HTML body
    msg_body = MIMEMultipart('alternative')
    html_part = MIMEText(html_content, 'html', 'utf-8')
    msg_body.attach(html_part)
    msg.attach(msg_body)
    
    # Add PDF attachment
    with open(attachment_path, 'rb') as f:
        pdf_data = f.read()
    
    attachment = MIMEApplication(pdf_data)
    attachment.add_header('Content-Disposition', 'attachment', 
                         filename=os.path.basename(attachment_path))
    msg.attach(attachment)
    
    # Send email
    ses_client.send_raw_email(
        Source=Config.AWS_SES_FROM_EMAIL,
        Destinations=[to_email],
        RawMessage={'Data': msg.as_string()}
    )

def schedule_email_sequence(customer_id, order_id):
    """
    Schedule 14-day email sequence
    """
    try:
        # Get customer for email personalization
        from database import Customer
        customer = Customer.query.get(customer_id)
        
        for day in range(1, 15):
            scheduled_time = datetime.utcnow() + timedelta(days=day)
            
            # Get email content for this day
            email_content = get_sequence_content(
                day_number=day, 
                customer_name=customer.name if customer else None,
                personalization_vars=None,  # Could be enhanced with quiz data
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

import markdown2

def get_sequence_content(day_number, customer_name, personalization_vars=None, order_id=None):
    """
    Get email content for the new 14-day sequence.
    Loads from new_day_X.html templates and injects dynamic content.
    """
    import os

    template_file = f'new_day_{day_number}.html'
    template_path = os.path.join(os.path.dirname(__file__), '..', 'email_templates', template_file)

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Inject dynamic content for specific days
        if day_number == 5 and personalization_vars:
            method_type = personalization_vars.get('method_type', 'gentle')
            module_name = 'module_5_cio' if method_type == 'cio' else 'module_6_gentle'
            
            content_path = os.path.join(os.path.dirname(__file__), '../../content/modules', f'{module_name}_ESSENTIAL.md')
            
            with open(content_path, 'r', encoding='utf-8') as cf:
                markdown_instructions = cf.read()
            
            # Convert markdown to HTML
            html_instructions = markdown2.markdown(markdown_instructions, extras=['fenced-code-blocks', 'tables'])
            
            # Replace placeholder
            html_content = html_content.replace('{method_instructions}', html_instructions)

        # Replace simple placeholders
        html_content = html_content.replace('{customer_name}', customer_name or 'there')
        if personalization_vars:
            html_content = html_content.replace('{method}', personalization_vars.get('method', 'your chosen method'))
        else:
            html_content = html_content.replace('{method}', 'your chosen method')
        
        if order_id:
            html_content = html_content.replace('{{order_id}}', str(order_id))


        # Generate subject and text body (can be improved later)
        subjects = {
            1: "Day 1: Welcome to Your Sleep Transformation",
            2: "Day 2: The Perfect Sleep Environment",
            3: "Day 3: The Magic of a Bedtime Routine",
            4: "Day 4: Understanding Wake Windows",
            5: "Day 5: Your Sleep Training Method",
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
        print(f"Error loading or personalizing new email template for day {day_number}: {str(e)}")
        # Fallback content
        return {
            'subject': f"Day {day_number}: Your Napocalypse Update",
            'text_body': "There was an error loading the email content. Please contact support.",
            'html_body': f"<h2>Hi {customer_name or 'there'}!</h2><p>There was an error loading the content for Day {day_number}. Please contact our support team for assistance.</p>"
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

def replace_personalization_vars(html_content, customer_name, personalization_vars):
    """
    Replace all personalization placeholders in HTML content
    """
    # Always replace customer name (handle None case)
    safe_customer_name = customer_name if customer_name is not None else ""
    html_content = html_content.replace('{customer_name}', safe_customer_name)
    
    if personalization_vars:
        # Replace all personalization variables
        for key, value in personalization_vars.items():
            placeholder = '{' + key + '}'
            # Ensure value is not None
            safe_value = str(value) if value is not None else ""
            html_content = html_content.replace(placeholder, safe_value)
    
    return html_content

def get_personalized_subject(day_number, personalization_vars):
    """
    Get personalized subject line based on method and challenge
    """
    method = personalization_vars.get('method_short', 'Sleep Training')
    challenge = personalization_vars.get('challenge_short', 'Sleep')
    
    subjects = {
        1: "🌙 Welcome to Napocalypse! Your Guide is Here",
        2: "✅ Day 2: Your First Night Checklist",
        3: f"🛠️ Day 3: Common {method} Challenges & How to Fix Them",
        4: f"⭐ Day 4: Real {method} Success Story (Just Like You!)",
        5: "🔧 Day 5: Your 2AM Troubleshooting Guide",
        6: "📚 Day 6: Expert Tips & Additional Resources",
        7: f"🎉 Day 7: You Made It! (Plus Your {method} Mastery Offer)"
    }
    
    return subjects.get(day_number, f"Day {day_number}: Napocalypse Update")

def get_generic_subject(day_number):
    """
    Get generic subject line (fallback)
    """
    subjects = {
        1: "🌙 Welcome to Napocalypse! Your Guide is Here",
        2: "✅ Day 2: Your First Night Checklist",
        3: "🛠️ Day 3: Common Challenges & How to Fix Them",
        4: "⭐ Day 4: Real Success Stories (You Can Do This!)",
        5: "🔧 Day 5: Your 2AM Troubleshooting Guide",
        6: "📚 Day 6: Expert Tips & Additional Resources",
        7: "🎉 Day 7: You Made It! (Plus What's Next)"
    }
    return subjects.get(day_number, f"Day {day_number}: Napocalypse Update")

def generate_text_version(day_number, customer_name, personalization_vars):
    """
    Generate plain text version of email
    """
    method = personalization_vars.get('method', 'your method') if personalization_vars else 'your method'
    
    return f"""
Hi {customer_name}!

This is Day {day_number} of your Napocalypse email series.

You're using the {method} approach, and we're here to support you every step of the way.

For the best experience, please view this email in HTML format.

If you can't see the HTML version, visit napocalypse.com for support.

Best,
The Napocalypse Team
    """

def send_upsell_confirmation_email(customer, pdf_path, modules):
    """
    Send upsell confirmation email with FULL PDF attachment
    """
    from_email = Config.AWS_SES_FROM_EMAIL
    subject = "Your Complete Reference Library is Ready! 🎉"
    
    # Get module info
    from services.module_selector import get_module_info
    module_details = [get_module_info(m) for m in modules]
    module_list = '\n'.join([f"<li>{m['title']}</li>" for m in module_details])
    
    # HTML body
    html_body = f"""
    <html>
    <head></head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #27ae60;">🎉 Welcome to the Complete Library!</h2>
            
            <p>Hi {customer.name or 'there'}!</p>
            
            <p>Thank you for upgrading! Your <strong>Complete Reference Library</strong> is attached and ready to use.</p>
            
            <div style="background-color: #d5f4e6; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #27ae60;">
                <h3 style="margin-top: 0; color: #2c3e50;">What's New in Your Complete Library:</h3>
                <ul style="margin: 10px 0;">
                    <li>✓ <strong>5-7x more content</strong> with deep dives into every strategy</li>
                    <li>✓ <strong>Advanced troubleshooting</strong> for every possible challenge</li>
                    <li>✓ <strong>Progress tracking tools</strong> and comprehensive logs</li>
                    <li>✓ <strong>The science behind it</strong> - understand WHY each method works</li>
                    <li>✓ <strong>Expert tips & tricks</strong> from professional sleep consultants</li>
                    <li>✓ <strong>Bonus resources</strong> including printable schedules and checklists</li>
                </ul>
            </div>
            
            <h3 style="color: #2c3e50;">Your Complete Modules:</h3>
            <ul style="background-color: #f8f9fa; padding: 15px 15px 15px 35px; border-radius: 5px;">
                {module_list}
            </ul>
            
            <div style="background-color: #fff9e6; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #f39c12;">
                <h3 style="margin-top: 0; color: #2c3e50;">How to Use Your Complete Library:</h3>
                <ol style="margin: 10px 0;">
                    <li>Review the expanded content in each of your modules</li>
                    <li>Use the troubleshooting sections when you hit challenges</li>
                    <li>Reference the science sections to understand the "why"</li>
                    <li>Print the bonus tracking tools and schedules</li>
                    <li>Keep it handy for future sleep challenges</li>
                </ol>
            </div>
            
            <h3 style="color: #2c3e50;">Need Help?</h3>
            <p>Reply to this email anytime with questions. We're here to support you!</p>
            
            <div style="background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0; text-align: center;">
                <p style="margin: 0; font-size: 14px; color: #555;">
                    <strong>Remember:</strong> You have our 100% money-back guarantee.<br>
                    If this doesn't help you succeed, we'll refund every penny.
                </p>
            </div>
            
            <p>Here's to mastering your baby's sleep!</p>
            
            <p style="margin-top: 30px;">
                <strong>The Napocalypse Team</strong><br>
                <a href="mailto:support@napocalypse.com" style="color: #3498db;">support@napocalypse.com</a>
            </p>
        </div>
    </body>
    </html>
    """
    
    # Text body
    text_body = f"""
    Hi {customer.name or 'there'}!
    
    Thank you for upgrading! Your Complete Reference Library is attached and ready to use.
    
    What's New in Your Complete Library:
    - 5-7x more content with deep dives into every strategy
    - Advanced troubleshooting for every possible challenge
    - Progress tracking tools and comprehensive logs
    - The science behind it - understand WHY each method works
    - Expert tips & tricks from professional sleep consultants
    - Bonus resources including printable schedules and checklists
    
    Your Complete Modules:
    {chr(10).join([f"- {m['title']}" for m in module_details])}
    
    How to Use Your Complete Library:
    1. Review the expanded content in each of your modules
    2. Use the troubleshooting sections when you hit challenges
    3. Reference the science sections to understand the "why"
    4. Print the bonus tracking tools and schedules
    5. Keep it handy for future sleep challenges
    
    Need Help?
    Reply to this email anytime with questions. We're here to support you!
    
    Remember: You have our 100% money-back guarantee.
    If this doesn't help you succeed, we'll refund every penny.
    
    Here's to mastering your baby's sleep!
    
    The Napocalypse Team
    support@napocalypse.com
    """
    
    try:
        # Create message
        msg = MIMEMultipart('mixed')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = customer.email
        
        # Create message body
        msg_body = MIMEMultipart('alternative')
        text_part = MIMEText(text_body, 'plain', 'utf-8')
        html_part = MIMEText(html_body, 'html', 'utf-8')
        msg_body.attach(text_part)
        msg_body.attach(html_part)
        msg.attach(msg_body)
        
        # Attach PDF
        with open(pdf_path, 'rb') as f:
            pdf_attachment = MIMEApplication(f.read())
            pdf_attachment.add_header('Content-Disposition', 'attachment', 
                                    filename='Complete_Sleep_Guide.pdf')
            msg.attach(pdf_attachment)
        
        # Send email
        response = ses_client.send_raw_email(
            Source=from_email,
            Destinations=[customer.email],
            RawMessage={'Data': msg.as_string()}
        )
        
        print(f"Upsell confirmation email sent to {customer.email}")
        return response
        
    except ClientError as e:
        print(f"Error sending upsell confirmation email: {e.response['Error']['Message']}")
        raise
    except Exception as e:
        print(f"Error sending upsell confirmation email: {str(e)}")
        raise
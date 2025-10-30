"""
Scheduler for automated email sequences
Uses APScheduler to send scheduled emails
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from database import db, EmailSequence, Customer
from services.email_service import send_sequence_email

scheduler = BackgroundScheduler()

def init_scheduler(app):
    """
    Initialize scheduler with Flask app context
    """
    def send_pending_emails():
        """
        Check for pending emails and send them
        """
        with app.app_context():
            try:
                # Get pending emails that are due
                pending_emails = EmailSequence.query.filter(
                    EmailSequence.status == 'pending',
                    EmailSequence.scheduled_for <= datetime.utcnow()
                ).all()
                
                for email in pending_emails:
                    # Get customer
                    customer = Customer.query.get(email.customer_id)
                    
                    if customer:
                        # Send email
                        success = send_sequence_email(
                            to_email=customer.email,
                            customer_name=customer.name or 'there',
                            day_number=email.day_number
                        )
                        
                        if success:
                            email.status = 'sent'
                            email.sent_at = datetime.utcnow()
                        else:
                            email.status = 'failed'
                        
                        db.session.commit()
                
                if pending_emails:
                    print(f"Processed {len(pending_emails)} pending emails")
                    
            except Exception as e:
                print(f"Error in email scheduler: {str(e)}")
                db.session.rollback()
    
    # Schedule to run every hour
    scheduler.add_job(
        func=send_pending_emails,
        trigger=IntervalTrigger(hours=1),
        id='send_pending_emails',
        name='Send pending email sequences',
        replace_existing=True
    )
    
    scheduler.start()
    print("Email scheduler started")
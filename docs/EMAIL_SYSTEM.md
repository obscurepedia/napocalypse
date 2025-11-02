# Email System Documentation

## Overview
Napocalypse uses an automated email system to deliver personalized sleep guides and send a 7-day educational email sequence to customers.

## Components

### 1. Email Service (`backend/services/email_service.py`)
Handles all email sending via AWS SES:
- **Delivery Email**: Sends the personalized PDF guide immediately after purchase
- **Sequence Emails**: Sends automated follow-up emails on Days 1-7

### 2. Email Scheduler (`backend/scheduler.py`)
Uses APScheduler to automatically send scheduled emails:
- Runs every hour to check for pending emails
- Sends emails that are due based on their scheduled time
- Updates email status (pending → sent/failed)

### 3. Email Templates (`backend/email_templates/`)
Professional HTML email templates for each day:
- `day_1_welcome.html` - Welcome email with PDF delivery
- `day_2_getting_started.html` - First night checklist
- `day_3_common_challenges.html` - Common challenges & solutions
- `day_4_success_stories.html` - Real success stories
- `day_5_troubleshooting.html` - 2AM troubleshooting guide
- `day_6_additional_resources.html` - Expert tips & resources
- `day_7_feedback.html` - Feedback request & product roadmap

## How It Works

### Purchase Flow:
1. Customer completes quiz and pays via Stripe
2. Stripe webhook triggers order processing
3. System generates personalized PDF based on quiz responses
4. **Delivery email sent immediately** with PDF attached
5. **7-day email sequence scheduled** (Days 1-7)

### Email Sequence Schedule:
- **Day 0** (Immediate): Delivery email with PDF
- **Day 1**: Welcome & getting started tips
- **Day 2**: First night checklist
- **Day 3**: Common challenges & solutions
- **Day 4**: Success stories & encouragement
- **Day 5**: Troubleshooting guide
- **Day 6**: Additional resources & expert tips
- **Day 7**: Feedback request & product roadmap

### Scheduler Operation:
- Runs every hour (configurable in `scheduler.py`)
- Queries database for pending emails where `scheduled_for <= now()`
- Sends each pending email via AWS SES
- Updates email status and sent timestamp
- Handles failures gracefully (marks as 'failed' for manual review)

## Database Schema

### EmailSequence Table:
```sql
- id (primary key)
- customer_id (foreign key to customers)
- order_id (foreign key to orders)
- day_number (1-7)
- email_type (day1, day2, etc.)
- subject (email subject line)
- scheduled_for (datetime when email should be sent)
- sent_at (datetime when email was actually sent)
- status (pending/sent/failed)
```

## Configuration

### Required Environment Variables:
```
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_SES_FROM_EMAIL=support@napocalypse.com
```

### AWS SES Setup:
1. Verify your domain in AWS SES
2. Verify your sender email address
3. Request production access (to send to any email)
4. Configure DKIM for better deliverability

## Email Content Features

### All emails include:
- Professional HTML design with Napocalypse branding
- Mobile-responsive layout
- Plain text fallback
- Unsubscribe link (required by law)
- Links to Privacy Policy and Terms of Service
- Consistent footer with contact information

### Day-specific content:
- **Day 1**: Welcome message, what to expect
- **Day 2**: Actionable checklist before starting
- **Day 3**: Solutions to common problems
- **Day 4**: Motivational success stories
- **Day 5**: Emergency troubleshooting scenarios
- **Day 6**: Advanced tips and resources
- **Day 7**: Feedback request + upsell to future products

## Testing

### Test Email Delivery:
```python
from services.email_service import send_delivery_email

send_delivery_email(
    to_email="test@example.com",
    customer_name="Test User",
    pdf_path="/path/to/guide.pdf",
    modules=["Module 1", "Module 2"]
)
```

### Test Sequence Email:
```python
from services.email_service import send_sequence_email

send_sequence_email(
    to_email="test@example.com",
    customer_name="Test User",
    day_number=1
)
```

### Test Scheduler:
```python
from services.email_service import schedule_email_sequence

schedule_email_sequence(
    customer_id=1,
    order_id=1
)
```

## Monitoring

### Check Email Status:
```sql
-- View all pending emails
SELECT * FROM email_sequences WHERE status = 'pending';

-- View failed emails
SELECT * FROM email_sequences WHERE status = 'failed';

-- View emails sent today
SELECT * FROM email_sequences 
WHERE status = 'sent' 
AND DATE(sent_at) = CURRENT_DATE;
```

### Common Issues:

**Emails not sending:**
- Check AWS SES credentials in environment variables
- Verify sender email is verified in AWS SES
- Check if AWS SES is in sandbox mode (limits sending)
- Review scheduler logs for errors

**Emails going to spam:**
- Configure SPF, DKIM, and DMARC records
- Use verified domain for sender email
- Avoid spam trigger words in subject lines
- Include unsubscribe link (already included)

**Wrong content in emails:**
- Check template files in `backend/email_templates/`
- Verify `get_sequence_content()` is loading correct template
- Test with different day numbers

## Customization

### Modify Email Content:
1. Edit HTML files in `backend/email_templates/`
2. Maintain consistent styling and branding
3. Test emails before deploying changes
4. Keep unsubscribe links and legal footer

### Change Email Schedule:
Edit `schedule_email_sequence()` in `email_service.py`:
```python
# Current: Days 1-7
scheduled_time = datetime.utcnow() + timedelta(days=day)

# Example: Send every other day
scheduled_time = datetime.utcnow() + timedelta(days=day*2)
```

### Change Scheduler Frequency:
Edit `init_scheduler()` in `scheduler.py`:
```python
# Current: Every hour
trigger=IntervalTrigger(hours=1)

# Example: Every 30 minutes
trigger=IntervalTrigger(minutes=30)
```

## Best Practices

1. **Always test emails** before sending to customers
2. **Monitor failed emails** and investigate causes
3. **Track open rates** (requires additional setup)
4. **Respect unsubscribe requests** immediately
5. **Keep content valuable** - don't just sell
6. **Maintain consistent branding** across all emails
7. **Include clear CTAs** in each email
8. **Optimize for mobile** (already done in templates)

## Legal Compliance

### CAN-SPAM Act Requirements (US):
- ✅ Include physical address (in footer)
- ✅ Include unsubscribe link (in all emails)
- ✅ Honor unsubscribe requests within 10 days
- ✅ Use accurate subject lines
- ✅ Identify message as advertisement (Day 7 upsell)

### GDPR Requirements (EU):
- ✅ Get consent before sending marketing emails
- ✅ Provide easy unsubscribe option
- ✅ Include privacy policy link
- ✅ Allow data access/deletion requests

## Future Enhancements

### Potential Improvements:
1. **Email Analytics**: Track opens, clicks, conversions
2. **A/B Testing**: Test different subject lines and content
3. **Segmentation**: Different sequences based on quiz responses
4. **Behavioral Triggers**: Send emails based on user actions
5. **Re-engagement**: Win back customers who unsubscribe
6. **SMS Integration**: Send critical updates via text
7. **Push Notifications**: For mobile app (future)

## Support

For issues with the email system:
1. Check logs in `/var/log/` (production)
2. Review database for failed emails
3. Test AWS SES connection
4. Contact support@napocalypse.com

## Summary

The email system is fully automated and requires minimal maintenance once configured. It provides:
- Immediate PDF delivery after purchase
- 7 days of valuable educational content
- Professional, branded communication
- Automated scheduling and sending
- Legal compliance (CAN-SPAM, GDPR)
- Upsell opportunities (Day 7)

The system is designed to nurture customers, provide value, and build long-term relationships that lead to repeat purchases of future products.
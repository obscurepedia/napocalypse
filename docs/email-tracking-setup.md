# Email Open/Click Tracking - Current Status & Solution

## Current Situation

Your database has `opened` and `clicked` columns in the `email_sequences` table, but they're all `False` because **tracking is not implemented**.

---

## Why Tracking Isn't Working

AWS SES **does not automatically track** opens and clicks. You have two options:

### Option 1: SES Configuration Sets (Recommended)
- AWS SES can track opens/clicks if you configure it
- Sends tracking data to SNS, CloudWatch, or Kinesis
- Requires AWS configuration (no code changes)

### Option 2: Third-Party Service
- Use services like SendGrid, Postmark, or Mailgun
- They have built-in tracking dashboards
- Easier to set up but costs more

---

## Current Impact

**Good news:** This doesn't affect your business operations:
- ✅ Emails are being sent successfully
- ✅ Customers are receiving them
- ❌ You just can't measure open/click rates

**For now:** You can track engagement through:
- Quiz completion rates
- Purchase conversion rates
- Direct customer feedback

---

## How to Enable Tracking (Option 1: AWS SES)

### Step 1: Create Configuration Set in AWS

1. Go to **AWS SES Console** → **Configuration Sets**
2. Click **Create Configuration Set**
3. Name it: `napocalypse-email-tracking`

### Step 2: Add Event Destination

1. In your configuration set, click **Add Destination**
2. Select **SNS Topic** (simplest) or **CloudWatch**
3. Enable these event types:
   - **Open**
   - **Click**
   - **Bounce**
   - **Complaint**

### Step 3: Create SNS Topic (if using SNS)

1. Go to **AWS SNS** → **Create Topic**
2. Name: `ses-email-events`
3. Create subscription:
   - Protocol: **HTTPS**
   - Endpoint: `https://napocalypse.com/api/email/events` (you'll need to create this)

### Step 4: Update Backend Code

Add configuration set to email sending:

```python
# In email_service.py, update send_sequence_email()

response = ses_client.send_email(
    Source=from_email,
    Destination={'ToAddresses': [to_email]},
    Message={
        'Subject': {'Data': email_content['subject']},
        'Body': {
            'Html': {'Data': email_content['html_body']},
            'Text': {'Data': email_content.get('text_body', '')}
        }
    },
    ConfigurationSetName='napocalypse-email-tracking'  # ADD THIS
)
```

### Step 5: Create Webhook to Receive Events

Create `/api/email/events` endpoint to receive SNS notifications:

```python
@email_bp.route('/events', methods=['POST'])
def email_events():
    """Handle SES tracking events from SNS"""
    data = request.get_json()

    # Verify SNS signature (important for security)
    # ... SNS verification code ...

    event_type = data['eventType']
    message_id = data['mail']['messageId']

    if event_type == 'Open':
        # Update EmailSequence.opened = True
        pass
    elif event_type == 'Click':
        # Update EmailSequence.clicked = True
        pass

    return jsonify({'success': True}), 200
```

---

## Simpler Alternative: Don't Track

**Honestly?** For a small business, you might not need open/click tracking.

**Why it's optional:**
- You're measuring what matters: **purchases**
- Email deliverability is working fine
- Open rates can be misleading (Apple Privacy blocks most tracking)
- Click rates are low for educational content anyway

**Focus on:**
- Conversion rate (quiz → purchase)
- Customer feedback
- Support ticket volume
- Refund rate

---

## Recommendation

**For now:** Leave tracking disabled and focus on:
1. ✅ Fixing duplicate emails (done)
2. ✅ Ensuring emails are personalized and valuable
3. ✅ Tracking business metrics (purchases, refunds)

**Later (if needed):** Set up SES Configuration Sets when you have bandwidth.

---

## Cost of Tracking

| Option | Cost | Effort |
|--------|------|--------|
| No tracking | Free | None |
| SES + SNS | ~$0.50/month | Medium |
| SendGrid | $15-100/month | Low |
| Postmark | $15-100/month | Low |

---

## Files That Would Need Changes

If you implement tracking:

1. `backend/services/email_service.py` - Add ConfigurationSetName
2. `backend/routes/email_routes.py` - Add `/events` endpoint
3. `backend/config.py` - Add SES_CONFIGURATION_SET
4. AWS Console - Create Configuration Set + SNS Topic

**Effort:** 2-3 hours of work

---

## Bottom Line

**Duplicate emails = Critical** ✅ Fixed
**Email tracking = Nice to have** ⏸️ Skip for now

Focus on revenue-driving features first.

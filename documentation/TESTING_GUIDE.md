# Complete Testing Guide

## Pre-Deployment Testing Checklist

### 1. Environment Setup ✓
- [ ] All environment variables configured
- [ ] Database connection working
- [ ] AWS SES configured and verified
- [ ] Stripe keys configured
- [ ] PDF output directory exists

### 2. V2 System Testing

#### A. Template Engine Test
```python
# Test in Python console
from backend.services.template_engine import generate_personalized_guide

quiz_responses = {
    'baby_age': '7-12 months',
    'sleep_philosophy': 'comfortable with some crying',
    'biggest_challenge': 'frequent night wakings',
    'sleep_associations': 'nursing to sleep',
    'living_situation': 'own room',
    'parenting_setup': 'two parents',
    'work_schedule': 'both work',
    'specific_challenge': 'naps are short'
}

customer_info = {
    'customer_name': 'Test Parent',
    'customer_email': 'test@example.com',
    'baby_name': 'Baby'
}

guide = generate_personalized_guide(quiz_responses, customer_info)
print(f"Guide length: {len(guide)} characters")
print(f"Guide preview: {guide[:500]}")
```

**Expected Result:**
- Guide should be 8,000-12,000 characters
- Should start with "# Your Personalized Sleep Training Guide"
- Should contain personalized content with customer name
- Should have 4-6 main sections

#### B. PDF Generation Test
```python
from backend.services.pdf_generator import generate_personalized_pdf
from backend.database import Customer

# Create test customer
customer = Customer(
    id=999,
    name='Test Parent',
    email='test@example.com'
)

quiz_data = {
    'baby_age': '7-12 months',
    'sleep_philosophy': 'comfortable with some crying'
}

# Generate guide
guide_content = generate_personalized_guide(quiz_responses, customer_info)

# Generate PDF
pdf_path = generate_personalized_pdf(
    customer=customer,
    quiz_data=quiz_data,
    guide_content=guide_content,
    is_v2=True
)

print(f"PDF generated at: {pdf_path}")
```

**Expected Result:**
- PDF file created successfully
- File size: 200-500 KB
- Opens without errors
- Contains 10-15 pages
- Formatting looks professional
- No broken images or styles

### 3. Complete Flow Testing

#### Test Scenario 1: New Customer Purchase
1. **Navigate to landing page**
   - [ ] Page loads correctly
   - [ ] All images load
   - [ ] CTA buttons work

2. **Take quiz**
   - [ ] All 8 questions display
   - [ ] Progress bar works
   - [ ] Validation works
   - [ ] Submit button works

3. **Payment**
   - [ ] Stripe checkout opens
   - [ ] Test card works (4242 4242 4242 4242)
   - [ ] Redirects to success page

4. **Webhook processing**
   - [ ] Webhook received
   - [ ] Order status updated to 'completed'
   - [ ] Guide generated using V2 engine
   - [ ] PDF created successfully
   - [ ] Email sent with PDF attachment

5. **Email sequence**
   - [ ] Day 1 email sent immediately
   - [ ] Emails scheduled for days 2-7
   - [ ] Personalization works correctly

#### Test Scenario 2: Different Quiz Combinations

Test these combinations to ensure proper block selection:

**Test A: CIO + Feeding**
- baby_age: '4-6 months'
- sleep_philosophy: 'comfortable with some crying'
- sleep_associations: 'nursing to sleep'

Expected blocks: age_4_6_months, method_cio, challenge_feeding

**Test B: Gentle + Motion**
- baby_age: '7-12 months'
- sleep_philosophy: 'gentle, no-cry approach'
- sleep_associations: 'rocking to sleep'

Expected blocks: age_7_12_months, method_gentle, challenge_motion

**Test C: CIO + Naps + Room Sharing**
- baby_age: '7-12 months'
- sleep_philosophy: 'comfortable with some crying'
- biggest_challenge: 'short naps'
- living_situation: 'room sharing with parents'

Expected blocks: age_7_12_months, method_cio, challenge_naps, situation_room_sharing

### 4. PDF Quality Checks

Open generated PDFs and verify:
- [ ] Cover page looks professional
- [ ] Customer name appears correctly
- [ ] Table of contents is accurate
- [ ] All sections flow smoothly
- [ ] No awkward page breaks
- [ ] Headers and formatting consistent
- [ ] No "module" language (should say "guide")
- [ ] Footer appears on pages
- [ ] Total pages: 10-15 (not 40-80)
- [ ] **NO UPSELL CONTENT IN PDF**

### 5. Email Testing

#### Delivery Email
- [ ] Subject line correct
- [ ] PDF attached
- [ ] Customer name personalized
- [ ] Links work
- [ ] HTML renders correctly
- [ ] Plain text version exists

#### Sequence Emails (Days 2-7)
- [ ] Correct email sent each day
- [ ] Personalization works
- [ ] Blog post links work (Day 4)
- [ ] Upsell only appears in Day 7
- [ ] All CTAs work

### 6. Blog Testing
- [ ] /blog index page loads
- [ ] All 10 blog posts load
- [ ] Links between posts work
- [ ] SEO meta tags present
- [ ] Mobile responsive

### 7. Legal Pages
- [ ] /privacy loads correctly
- [ ] /terms loads correctly
- [ ] Footer links work

### 8. Error Handling

Test these error scenarios:
- [ ] Invalid quiz data
- [ ] Payment failure
- [ ] Webhook signature mismatch
- [ ] PDF generation failure
- [ ] Email sending failure

### 9. Performance Testing
- [ ] Quiz submission < 2 seconds
- [ ] PDF generation < 10 seconds
- [ ] Email delivery < 30 seconds
- [ ] Page load times < 3 seconds

### 10. Security Testing
- [ ] Webhook signature verified
- [ ] SQL injection protected
- [ ] XSS protected
- [ ] CSRF tokens present
- [ ] HTTPS enforced

## Test Data

### Test Credit Cards (Stripe)
- Success: 4242 4242 4242 4242
- Decline: 4000 0000 0000 0002
- Insufficient funds: 4000 0000 0000 9995

### Test Email
Use a real email you can access to verify email delivery.

## Success Criteria

### Must Pass Before Launch:
1. ✅ V2 template engine generates guides correctly
2. ✅ PDFs are 10-15 pages (not 40-80)
3. ✅ NO upsell in PDF
4. ✅ Email sequence works
5. ✅ Payment processing works
6. ✅ All pages load correctly
7. ✅ No console errors
8. ✅ Mobile responsive

### Nice to Have:
- Blog posts indexed by Google
- Analytics tracking
- A/B testing setup
- Customer feedback system

## Post-Launch Monitoring

### Week 1:
- Monitor refund rate (target: < 10%)
- Check email open rates (target: > 40%)
- Verify PDF generation success rate (target: 100%)
- Monitor customer support emails

### Week 2-4:
- Collect customer testimonials
- Track conversion rates
- Monitor blog traffic
- Optimize based on data
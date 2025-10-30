# Deployment Guide for Napocalypse

## Prerequisites

1. **Render.com Account** - Sign up at render.com
2. **Stripe Account** - Sign up at stripe.com
3. **AWS Account** - For SES email service
4. **Domain** - napocalypse.com (already owned)

## Step 1: Set Up AWS SES

### 1.1 Verify Domain
1. Go to AWS SES Console
2. Click "Verified identities" → "Create identity"
3. Choose "Domain" and enter: napocalypse.com
4. AWS will provide DNS records - add these to your domain registrar:
   - TXT record for verification
   - CNAME records for DKIM
   - MX record (optional)

### 1.2 Verify Email Address
1. Create identity for: support@napocalypse.com
2. Click verification link in email

### 1.3 Request Production Access
1. Go to "Account dashboard"
2. Click "Request production access"
3. Fill out form:
   - Use case: "Transactional emails for baby sleep guide business"
   - Website: napocalypse.com
   - Expected volume: 100 emails/day initially
4. Wait for approval (usually 24 hours)

### 1.4 Create IAM User
1. Go to IAM Console
2. Create user: "napocalypse-ses"
3. Attach policy: "AmazonSESFullAccess"
4. Create access key
5. Save Access Key ID and Secret Access Key

## Step 2: Set Up Stripe

### 2.1 Create Product
1. Go to Stripe Dashboard → Products
2. Click "Add product"
3. Name: "Personalized Baby Sleep Guide"
4. Price: $47.00 USD
5. Save and copy the Price ID (starts with `price_`)

### 2.2 Get API Keys
1. Go to Developers → API keys
2. Copy:
   - Publishable key (starts with `pk_`)
   - Secret key (starts with `sk_`)

### 2.3 Set Up Webhook
1. Go to Developers → Webhooks
2. Click "Add endpoint"
3. Endpoint URL: `https://your-app.onrender.com/webhook/stripe`
4. Select events:
   - `checkout.session.completed`
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
5. Copy Webhook signing secret (starts with `whsec_`)

## Step 3: Deploy to Render.com

### 3.1 Connect GitHub Repository
1. Go to Render Dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub account
4. Select the `napocalypse` repository

### 3.2 Configure Web Service
- **Name:** napocalypse
- **Region:** Oregon (or closest to your users)
- **Branch:** main
- **Build Command:** `cd backend && pip install -r requirements.txt`
- **Start Command:** `cd backend && gunicorn app:app`

### 3.3 Add Environment Variables
Click "Advanced" and add these environment variables:

```
DATABASE_URL=<will be auto-filled by Render>
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
AWS_SES_FROM_EMAIL=support@napocalypse.com
SECRET_KEY=<generate a random string>
FLASK_ENV=production
FRONTEND_URL=https://napocalypse.com
```

### 3.4 Create PostgreSQL Database
1. Click "New +" → "PostgreSQL"
2. Name: napocalypse-db
3. Plan: Starter ($7/month)
4. Create database

### 3.5 Link Database to Web Service
The `DATABASE_URL` will be automatically added to your web service.

### 3.6 Deploy
Click "Create Web Service" and wait for deployment to complete.

## Step 4: Initialize Database

### 4.1 Connect to Database
1. Go to your PostgreSQL database in Render
2. Click "Connect" → "External Connection"
3. Use the provided connection string

### 4.2 Run Schema
```bash
psql <connection_string> -f database/schema.sql
```

Or use Render's web shell:
1. Go to your database
2. Click "Connect" → "Web Shell"
3. Paste the contents of `database/schema.sql`

## Step 5: Configure Domain

### 5.1 Add Custom Domain in Render
1. Go to your web service
2. Click "Settings" → "Custom Domain"
3. Add: napocalypse.com
4. Render will provide DNS records

### 5.2 Update DNS
Add the provided records to your domain registrar:
- CNAME record pointing to Render

### 5.3 Enable HTTPS
Render automatically provisions SSL certificates via Let's Encrypt.

## Step 6: Test the System

### 6.1 Test Quiz Flow
1. Visit https://napocalypse.com
2. Click "Take the Quiz"
3. Complete all 8 questions
4. Enter test email
5. Verify redirect to Stripe Checkout

### 6.2 Test Payment (Use Stripe Test Mode First)
Test card: 4242 4242 4242 4242
- Any future expiry date
- Any 3-digit CVC
- Any ZIP code

### 6.3 Verify Email Delivery
1. Complete test purchase
2. Check email inbox for PDF
3. Verify PDF is personalized correctly

### 6.4 Test Webhook
1. Go to Stripe Dashboard → Webhooks
2. Click on your webhook
3. Click "Send test webhook"
4. Verify order is created in database

## Step 7: Go Live

### 7.1 Switch to Live Mode
1. Update Stripe keys to live mode (pk_live_, sk_live_)
2. Update webhook secret to live webhook
3. Redeploy on Render

### 7.2 Final Checks
- [ ] Domain is working (https://napocalypse.com)
- [ ] Quiz submits successfully
- [ ] Stripe checkout works
- [ ] Webhook receives events
- [ ] PDF generates correctly
- [ ] Email delivers successfully
- [ ] Database stores data correctly

## Monitoring & Maintenance

### Daily Checks
- Check Render logs for errors
- Monitor Stripe dashboard for payments
- Check AWS SES for email delivery rates

### Weekly Tasks
- Review customer feedback
- Check database backups
- Monitor email open rates

### Monthly Tasks
- Review AWS SES costs
- Review Stripe transaction fees
- Analyze conversion rates
- Update content if needed

## Troubleshooting

### PDF Not Generating
- Check Render logs for errors
- Verify WeasyPrint dependencies installed
- Check file permissions in generated_pdfs directory

### Emails Not Sending
- Verify AWS SES is in production mode (not sandbox)
- Check AWS SES sending limits
- Verify email address is verified
- Check Render logs for boto3 errors

### Webhook Not Working
- Verify webhook URL is correct
- Check webhook signing secret
- Review Stripe webhook logs
- Check Render logs for errors

### Database Connection Issues
- Verify DATABASE_URL is correct
- Check Render database status
- Review connection pool settings

## Support

For issues:
1. Check Render logs
2. Check Stripe webhook logs
3. Check AWS SES sending statistics
4. Email: support@napocalypse.com

## Costs Summary

**Monthly Operating Costs:**
- Render Web Service: $7/month
- Render PostgreSQL: $7/month
- AWS SES: ~$1/month (for 10,000 emails)
- Stripe: 2.9% + $0.30 per transaction
- **Total Fixed: ~$15/month**

**Per Sale:**
- Stripe fee: $1.66 per $47 sale
- Net per sale: $45.34
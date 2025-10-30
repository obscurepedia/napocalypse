# Napocalypse - Personalized Baby Sleep Guides

A professional, automated platform for delivering personalized baby sleep training guides based on quiz responses.

## Tech Stack

- **Frontend:** HTML/CSS/JavaScript
- **Backend:** Python/Flask
- **Database:** PostgreSQL
- **Payment:** Stripe
- **Email:** AWS SES
- **Hosting:** Render.com
- **PDF Generation:** WeasyPrint

## Project Structure

```
napocalypse/
├── backend/           # Flask application
├── frontend/          # HTML/CSS/JS files
├── content/           # Sleep guide modules
├── database/          # Database schema
├── docs/              # Documentation
└── tests/             # Test files
```

## Setup Instructions

### 1. Environment Variables

Create a `.env` file in the backend directory:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/napocalypse

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...

# AWS SES
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
AWS_SES_FROM_EMAIL=support@napocalypse.com

# App
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
FRONTEND_URL=https://napocalypse.com
```

### 2. Database Setup

```bash
# Connect to PostgreSQL and run:
psql -U your_user -d napocalypse -f database/schema.sql
```

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Run Locally

```bash
cd backend
python app.py
```

Visit `http://localhost:5000`

### 5. Deploy to Render.com

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Use the `render.yaml` configuration
4. Add environment variables in Render dashboard
5. Deploy!

## Features

- ✅ Interactive 8-question quiz
- ✅ Stripe payment integration
- ✅ Automated PDF generation (personalized based on quiz)
- ✅ AWS SES email delivery
- ✅ 7-day automated email sequence
- ✅ PostgreSQL database for customer data
- ✅ Webhook handling for payment events
- ✅ Responsive design
- ✅ 100% money-back guarantee handling

## Module Logic

The system selects 3-5 modules based on quiz responses:
- **Age-based:** 1 module (0-3mo, 4-6mo, 7-12mo, 13-24mo)
- **Method-based:** 1 module (CIO or Gentle)
- **Challenge-based:** 1 module (Feeding transition, etc.)
- **Situation-based:** 0-1 modules (Room sharing, etc.)

## API Endpoints

- `GET /` - Landing page
- `GET /quiz` - Quiz interface
- `POST /api/quiz/submit` - Submit quiz responses
- `POST /api/payment/create-checkout` - Create Stripe checkout
- `POST /webhook/stripe` - Stripe webhook handler
- `GET /success` - Post-purchase success page

## Email Sequences

- **Day 0:** Immediate delivery with PDF
- **Day 1:** Implementation tips
- **Day 2:** Age-specific guidance
- **Day 3:** Method focus
- **Day 4:** Challenge solutions
- **Day 5:** Handling setbacks
- **Day 6:** Progress check-in
- **Day 7:** Next steps + upsell

## License

Proprietary - All rights reserved

## Support

For questions: support@napocalypse.com
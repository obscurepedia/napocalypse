# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Napocalypse is a personalized baby sleep training guide platform. Customers complete an 8-question quiz, pay via Stripe, and receive a personalized PDF guide delivered via email, followed by a 7-day automated email sequence.

**Tech Stack:** Python/Flask backend, HTML/CSS/JS frontend, PostgreSQL database, Stripe payments, AWS SES emails, WeasyPrint for PDF generation, hosted on Render.com

## Development Commands

### Run Locally
```bash
cd backend
python app.py
# Runs on http://localhost:5000
```

### Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Database Setup
```bash
# Connect to PostgreSQL and run:
psql -U your_user -d napocalypse -f database/schema.sql
```

### Test Database Connection
```bash
curl http://localhost:5000/test-db
```

### Deploy to Render
The project uses `render.yaml` for deployment configuration. Push to GitHub `main` branch to trigger deployment.

## Architecture

### Content Generation Systems

The project has **two content generation systems** (V1 and V2):

**V1 System (Module-based):**
- Uses complete markdown files in `content/modules/`
- Each module has `_ESSENTIAL` (condensed) and `_FULL_CONTENT` (complete) versions
- `services/module_selector.py` selects 3-5 modules based on quiz responses
- `services/pdf_generator.py` combines modules into PDF

**V2 System (Block-based):**
- Uses smaller content blocks in `content_blocks/` organized by category (age, method, challenge, situation)
- `services/block_selector.py` selects 3-4 blocks for more concise guides (10-16 pages)
- `services/personalization_v2.py` replaces placeholders like `{customer_name}`, `{baby_age}`
- `services/template_engine.py` assembles blocks into final markdown

**Current Status:** The V2 system was added to create shorter, more focused guides. Check recent commits to understand which system is currently active.

### Request Flow

1. **Quiz Submission** (`/api/quiz/submit`):
   - Frontend: `frontend/quiz.html` + `frontend/js/quiz.js`
   - Backend: `routes/quiz_routes.py`
   - Saves customer and quiz response to database
   - Returns customer_id for payment

2. **Payment Checkout** (`/api/payment/create-checkout`):
   - Frontend: Redirects to Stripe Checkout
   - Backend: `routes/payment_routes.py`
   - Creates Order record with `status='pending'`
   - Returns Stripe checkout URL

3. **Webhook Handler** (`/webhook/stripe`):
   - Backend: `routes/webhook_routes.py`
   - Stripe calls this endpoint on successful payment
   - Generates personalized PDF based on quiz responses
   - Sends immediate delivery email with PDF attachment
   - Schedules 7-day email sequence

4. **Success Page** (`/success`):
   - Frontend: `frontend/success.html`
   - Collects personalization data (parent name, baby name)
   - Sends to `/api/personalize` endpoint in `app.py`
   - Re-sends email with personalized names

### Database Schema

**Key tables:**
- `customers` - Email, name, Stripe customer ID
- `quiz_responses` - 8 quiz questions (baby_age, sleep_philosophy, etc.)
- `orders` - Payment tracking, PDF URL, status
- `modules_assigned` - Which modules were included in each order
- `email_sequences` - Tracks scheduled emails (day_number, status, scheduled_for)
- `upsells` - Tracks upsell purchases for full content upgrades

**Important:** Orders link to customers. Email sequences link to both customers and orders.

### Email System

**Immediate Delivery:**
- `services/email_service.py::send_delivery_email()` sends PDF immediately after payment
- Uses AWS SES with boto3
- PDF attached as file

**7-Day Sequence:**
- `services/email_service.py::schedule_email_sequence()` creates 7 records in `email_sequences` table
- `scheduler.py` runs hourly via APScheduler
- Checks for `status='pending'` and `scheduled_for <= now()`
- Sends emails and updates status to `sent`
- Email templates in `backend/email_templates/`

**Email Content:**
- Day 1: Welcome + getting started
- Day 2: First night checklist
- Day 3: Common challenges
- Day 4: Success stories
- Day 5: Troubleshooting
- Day 6: Expert tips
- Day 7: Feedback + upsell

### PDF Generation

**Process:**
1. Select modules/blocks based on quiz responses
2. Load markdown content from `content/` or `content_blocks/`
3. Replace personalization placeholders
4. Convert markdown to HTML
5. Apply CSS styling
6. WeasyPrint renders HTML → PDF
7. Save to `backend/generated_pdfs/`
8. Store path in `orders.pdf_url`

**Key Files:**
- `services/pdf_generator.py` - Main PDF generation logic
- `backend/templates/` - HTML templates for PDF layout (if used)
- CSS styling embedded in PDF generator

**PDF Variants:**
- Essential version: Condensed content (~15-20 pages)
- Full version: Complete detailed content (~40-60 pages) - available as upsell

### Module Selection Logic

Located in `services/module_selector.py::select_modules()`:

1. **Age module (1):** Based on `baby_age` (0-3mo, 4-6mo, 7-12mo, 13-24mo)
2. **Method module (1):** Based on `sleep_philosophy` (CIO vs Gentle)
3. **Sleep association (0-1):** If customer selected feeding/rocking/pacifier dependency
4. **Challenge (0-1):** Based on `biggest_challenge` (naps, early morning, etc.)
5. **Situation (0-1):** If room sharing or apartment living

Total: 3-5 modules per guide

### Block Selection Logic (V2)

Located in `services/block_selector.py::select_blocks()`:

1. **Age block (1):** Condensed age-specific content
2. **Method block (1):** Combined overview + implementation for CIO or Gentle
3. **Primary challenge (1):** Feeding, motion, pacifier, naps, or early morning
4. **Situation (0-1):** Only if critical (room sharing, apartment)

Total: 3-4 blocks = 10-16 pages

## Configuration

**Environment Variables (`.env` in backend/):**
- `DATABASE_URL` - PostgreSQL connection string
- `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_ID`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `AWS_SES_FROM_EMAIL`
- `SECRET_KEY` - Flask session secret
- `FLASK_ENV` - `development` or `production`
- `FRONTEND_URL` - Base URL for frontend

**Configuration Logic:**
- `backend/config.py` loads all environment variables
- Validates required variables in production
- Includes database connection pool settings for reliability
- Creates PDF output directory on startup

## Important Patterns

### Database Sessions
- Always use `db.session.commit()` after modifications
- Use `db.session.rollback()` in exception handlers
- Use `db.session.flush()` when you need the ID before committing

### Stripe Webhooks
- Verify signature using `stripe.Webhook.construct_event()`
- Handle `checkout.session.completed` for successful payments
- Check `metadata.type` to distinguish regular vs upsell purchases
- Always return 200 status even if processing fails (to prevent retries)

### Email Reliability
- Email scheduler runs every hour (configurable in `scheduler.py`)
- Failed emails marked as `status='failed'` for manual review
- Uses APScheduler with Flask app context
- Check logs for boto3 errors if emails not sending

### PDF Generation
- WeasyPrint requires specific dependencies (Cairo, Pango)
- PDFs saved with timestamp in filename to avoid conflicts
- Uses absolute file paths for reliability
- Markdown converted to HTML before PDF rendering

### Personalization
- Customer name and baby name collected **after** payment on success page
- Stored in `customers.name` and `customers.baby_name`
- Used in email content and PDF generation
- Graceful fallback to "there" / "your little one" if not provided

## Common Tasks

### Adding a New Module
1. Create markdown file in `content/modules/` with both `_ESSENTIAL` and `_FULL_CONTENT` versions
2. Add module info to `services/module_selector.py::get_module_info()`
3. Add selection logic to `select_modules()` if needed

### Adding a New Content Block (V2)
1. Create markdown file in appropriate `content_blocks/` subdirectory
2. Use placeholders like `{customer_name}`, `{baby_age}`, `{method}`
3. Update `services/block_selector.py` with block ID and selection logic
4. Test personalization with various quiz combinations

### Modifying Email Sequence
1. Edit HTML templates in `backend/email_templates/`
2. Maintain consistent styling and branding
3. Keep unsubscribe link and legal footer
4. Test emails before deploying

### Changing Email Schedule
- Edit `schedule_email_sequence()` in `services/email_service.py`
- Modify `timedelta(days=day)` to change timing
- Edit `EMAIL_SEQUENCE_DAYS` in config.py if changing total days

### Debugging Webhook Issues
1. Check Stripe Dashboard → Webhooks for event logs
2. Review Render logs for processing errors
3. Verify `STRIPE_WEBHOOK_SECRET` matches Stripe dashboard
4. Test locally with Stripe CLI: `stripe listen --forward-to localhost:5000/webhook/stripe`

### Testing Payment Flow
1. Use Stripe test mode keys
2. Test card: `4242 4242 4242 4242`, any future date, any CVC
3. Check database for order creation
4. Verify PDF generation in `backend/generated_pdfs/`
5. Check email delivery (may need to verify recipient in AWS SES sandbox)

## File Structure Reference

```
napocalypse/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration management
│   ├── database.py            # SQLAlchemy models
│   ├── scheduler.py           # Email scheduler (APScheduler)
│   ├── routes/               # API endpoints
│   │   ├── quiz_routes.py
│   │   ├── payment_routes.py
│   │   ├── webhook_routes.py
│   │   ├── guide_routes.py
│   │   └── upsell.py
│   ├── services/             # Business logic
│   │   ├── module_selector.py      # V1 module selection
│   │   ├── block_selector.py       # V2 block selection
│   │   ├── pdf_generator.py        # PDF creation
│   │   ├── email_service.py        # Email sending & scheduling
│   │   ├── template_engine.py      # V2 template assembly
│   │   ├── personalization_v2.py   # V2 placeholder replacement
│   │   └── personalization.py      # V1 personalization
│   ├── email_templates/      # Email HTML templates
│   └── generated_pdfs/       # Output directory for PDFs
├── frontend/                  # Static files served by Flask
│   ├── index.html            # Home page
│   ├── quiz.html             # Quiz interface
│   ├── start.html            # Landing/sales page
│   ├── success.html          # Post-payment personalization
│   ├── success-details.html  # What happens next
│   ├── css/, js/, images/
│   └── blog/                 # Blog templates
├── content/                   # V1 complete module markdown files
│   ├── modules/
│   │   ├── module_1_newborn_ESSENTIAL.md
│   │   ├── module_1_newborn_FULL_CONTENT.md
│   │   └── ... (12 modules × 2 versions)
│   └── blog/                 # Blog post markdown
├── content_blocks/           # V2 smaller content blocks
│   ├── age/                  # Age-specific blocks
│   ├── method/               # CIO vs Gentle methods
│   ├── challenge/            # Specific sleep challenges
│   └── situation/            # Living situations
├── database/
│   ├── schema.sql            # Main database schema
│   └── migration_*.sql       # Database migrations
├── docs/
│   ├── DEPLOYMENT.md         # Detailed deployment guide
│   └── EMAIL_SYSTEM.md       # Email system documentation
├── render.yaml               # Render.com deployment config
└── README.md                 # Project overview
```

## Known Issues & Gotchas

- WeasyPrint installation can be tricky on some systems (requires system dependencies)
- AWS SES starts in sandbox mode - must request production access to send to any email
- Stripe webhooks need public URL - use ngrok or Stripe CLI for local testing
- Database connection pooling configured for Render.com's limitations
- Email scheduler initialized with Flask app context to access database
- Success page personalization happens **after** initial email (requires second email send)

## Documentation

- See `docs/DEPLOYMENT.md` for full deployment instructions
- See `docs/EMAIL_SYSTEM.md` for detailed email system documentation
- See README.md for project overview and setup

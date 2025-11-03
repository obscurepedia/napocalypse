-- Napocalypse Database Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Customers table
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quiz responses table
CREATE TABLE quiz_responses (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
    baby_age VARCHAR(50) NOT NULL,
    sleep_situation VARCHAR(100) NOT NULL,
    sleep_philosophy VARCHAR(100) NOT NULL,
    living_situation VARCHAR(100) NOT NULL,
    parenting_setup VARCHAR(100) NOT NULL,
    work_schedule VARCHAR(100) NOT NULL,
    biggest_challenge VARCHAR(100) NOT NULL,
    sleep_associations VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    stripe_checkout_session_id VARCHAR(255) UNIQUE,
    amount INTEGER NOT NULL, -- in cents
    currency VARCHAR(3) DEFAULT 'usd',
    status VARCHAR(50) DEFAULT 'pending', -- pending, completed, refunded
    pdf_generated BOOLEAN DEFAULT FALSE,
    pdf_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Modules assigned to each customer
CREATE TABLE modules_assigned (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    module_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Email sequences tracking
CREATE TABLE email_sequences (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    day_number INTEGER NOT NULL,
    email_type VARCHAR(50) NOT NULL, -- delivery, day1, day2, etc.
    subject VARCHAR(255),
    sent_at TIMESTAMP,
    opened BOOLEAN DEFAULT FALSE,
    clicked BOOLEAN DEFAULT FALSE,
    scheduled_for TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending' -- pending, sent, failed
);

-- Create indexes for better performance
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_stripe_id ON customers(stripe_customer_id);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_stripe_payment_intent ON orders(stripe_payment_intent_id);
CREATE INDEX idx_quiz_responses_customer_id ON quiz_responses(customer_id);
CREATE INDEX idx_email_sequences_customer_id ON email_sequences(customer_id);
CREATE INDEX idx_email_sequences_status ON email_sequences(status);
CREATE INDEX idx_email_sequences_scheduled ON email_sequences(scheduled_for);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add trigger to customers table
CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing (optional - remove in production)
-- INSERT INTO customers (email, name) VALUES ('test@example.com', 'Test User');

-- Upsells table
CREATE TABLE upsells (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
    original_order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    upsell_order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    modules_included TEXT NOT NULL, -- comma-separated list of module names
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    stripe_checkout_session_id VARCHAR(255) UNIQUE,
    amount INTEGER NOT NULL, -- in cents
    currency VARCHAR(3) DEFAULT 'usd',
    status VARCHAR(50) DEFAULT 'pending', -- pending, completed, refunded
    pdf_generated BOOLEAN DEFAULT FALSE,
    pdf_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_upsells_customer_id ON upsells(customer_id);
CREATE INDEX idx_upsells_status ON upsells(status);
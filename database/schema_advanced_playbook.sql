-- Advanced Playbook Drip Delivery Schema
-- Run this migration to add support for 4-week drip delivery

-- Add sequence_type to email_sequences table
ALTER TABLE email_sequences ADD COLUMN IF NOT EXISTS sequence_type VARCHAR(50) DEFAULT 'nurture';
COMMENT ON COLUMN email_sequences.sequence_type IS 'Type of sequence: nurture (Days 1-7) or advanced_delivery (Days 7-32)';

-- Create advanced_playbook_deliveries table
CREATE TABLE IF NOT EXISTS advanced_playbook_deliveries (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    upsell_order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    module_number INTEGER NOT NULL,
    module_name VARCHAR(100) NOT NULL,
    scheduled_date DATE NOT NULL,
    delivered_date TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_module_number CHECK (module_number BETWEEN 1 AND 5),
    CONSTRAINT check_status CHECK (status IN ('pending', 'delivered', 'failed'))
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_advanced_deliveries_customer ON advanced_playbook_deliveries(customer_id);
CREATE INDEX IF NOT EXISTS idx_advanced_deliveries_scheduled ON advanced_playbook_deliveries(scheduled_date, status);
CREATE INDEX IF NOT EXISTS idx_advanced_deliveries_order ON advanced_playbook_deliveries(upsell_order_id);

-- Add comments for documentation
COMMENT ON TABLE advanced_playbook_deliveries IS 'Tracks scheduled delivery of Advanced Playbook modules over 4 weeks';
COMMENT ON COLUMN advanced_playbook_deliveries.module_number IS 'Module number: 1-4 for modules, 5 for completion email';
COMMENT ON COLUMN advanced_playbook_deliveries.module_name IS 'Module identifier (e.g., module_5_cio, module_7_feeding, completion)';
COMMENT ON COLUMN advanced_playbook_deliveries.scheduled_date IS 'Date when module should be delivered';
COMMENT ON COLUMN advanced_playbook_deliveries.delivered_date IS 'Actual delivery timestamp';
COMMENT ON COLUMN advanced_playbook_deliveries.status IS 'Delivery status: pending, delivered, or failed';

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_advanced_playbook_deliveries_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for updated_at
DROP TRIGGER IF EXISTS trigger_update_advanced_playbook_deliveries_updated_at ON advanced_playbook_deliveries;
CREATE TRIGGER trigger_update_advanced_playbook_deliveries_updated_at
    BEFORE UPDATE ON advanced_playbook_deliveries
    FOR EACH ROW
    EXECUTE FUNCTION update_advanced_playbook_deliveries_updated_at();

-- Verification query
-- Run this after migration to verify tables were created
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name IN ('advanced_playbook_deliveries', 'email_sequences')
ORDER BY table_name, ordinal_position;
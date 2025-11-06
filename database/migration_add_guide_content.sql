-- Database Migration: Add guide_content column to orders table
-- Run this in your Render PostgreSQL database

ALTER TABLE orders ADD COLUMN guide_content TEXT;

COMMENT ON COLUMN orders.guide_content IS 'V2 personalized guide markdown content';
# Database Migration Guide for V2

## Overview
V2 adds a new `guide_content` field to the `orders` table to store the personalized guide markdown.

## Migration SQL

Run this SQL on your PostgreSQL database:

```sql
-- Add guide_content column to orders table
ALTER TABLE orders ADD COLUMN guide_content TEXT;

-- Add comment for documentation
COMMENT ON COLUMN orders.guide_content IS 'V2 personalized guide markdown content';
```

## Verification

After running the migration, verify it worked:

```sql
-- Check that column was added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'orders' AND column_name = 'guide_content';
```

Expected output:
```
 column_name   | data_type 
---------------+-----------
 guide_content | text
```

## Rollback (if needed)

If you need to rollback this migration:

```sql
ALTER TABLE orders DROP COLUMN guide_content;
```

## Notes

- This migration is backward compatible
- Existing orders will have NULL guide_content (they used the old module system)
- New orders will have guide_content populated by V2 template engine
- The modules_assigned table is still used for upsell tracking
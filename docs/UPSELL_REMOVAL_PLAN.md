# Upsell Feature Removal Plan

**Date:** 2025-11-16
**Status:** In Progress (Phase 1 partially complete)

## Executive Summary

This document outlines the complete plan to remove all upsell functionality from the Napocalypse codebase. The system will be simplified to support only the core flow: Quiz → Payment → Quick-Start PDF → 14-day email sequence.

---

## Current System Architecture

### What Customers Get Now:
1. **Initial Purchase ($47):**
   - Quick-Start Guide PDF (ESSENTIAL content)
   - 14-day email coaching sequence

2. **Upsell (BEING REMOVED):**
   - Complete Reference Library (FULL_CONTENT modules)
   - Additional detailed content

### Future System (After Removal):
1. **Single Purchase ($47):**
   - Quick-Start Guide PDF
   - 14-day email sequence
   - No upsell option

---

## Progress Status

### ✅ COMPLETED (Phase 1 - Partial)

#### Backend Code Changes:
1. **app.py**
   - ✅ Removed: `from routes.upsell import upsell_bp` (line 7)
   - ✅ Removed: `app.register_blueprint(upsell_bp)` (line 43)

2. **routes/webhook_routes.py**
   - ✅ Simplified webhook handler to remove upsell session type checking
   - ✅ Removed: Lines 42-49 (upsell webhook routing logic)

3. **services/email_service.py**
   - ✅ Removed: Upsell URL injection logic (lines 158-173)
   - ✅ Removed: `send_upsell_confirmation_email()` function (lines 352-498)

4. **routes/upsell.py**
   - ✅ Deleted entire file (433 lines)

---

## 🔄 REMAINING WORK

### Phase 1: Complete Backend Code Removal

#### 1. PDF Generator Simplification
**File:** `backend/services/pdf_generator.py`

**Current Issue:** The `is_upsell` parameter is used throughout to switch between ESSENTIAL and FULL_CONTENT versions.

**Changes Needed:**
- **Line 90:** Remove `is_upsell=False` parameter from `generate_personalized_pdf()` signature
- **Line 98:** Remove documentation about is_upsell parameter
- **Line 115:** Change `version = "FULL" if is_upsell else "ESSENTIAL"` to `version = "ESSENTIAL"`
- **Line 130:** Remove `is_upsell` parameter from `generate_html_content()` call
- **Line 192:** Remove `is_upsell=False` parameter from `generate_html_content()` signature
- **Line 214:** Remove conditional subtitle (always use standard version)
- **Line 266:** Remove `is_upsell` parameter from `generate_module_content()` call
- **Line 309:** Remove `is_upsell=False` parameter from `generate_module_content()` signature
- **Line 317:** Change `version = "FULL_CONTENT" if is_upsell else "ESSENTIAL"` to `version = "ESSENTIAL"`

**Alternative Approach (If You Want to Keep Full Content):**
If you decide later that you want customers to receive FULL_CONTENT instead:
- Simply change all `version = "ESSENTIAL"` to `version = "FULL_CONTENT"`
- Remove the parameter but keep the version selection logic

**Recommendation:** Keep the parameter removal separate from content version decision. For now, just default to ESSENTIAL.

#### 2. Guide Routes
**File:** `backend/routes/guide_routes.py`

**Changes Needed:**
- **Line 31:** Remove comment about is_upsell
- **Line 36:** Remove `is_upsell=True` parameter OR change to `is_upsell=False`

**Note:** This route allows users to download their full guide. Currently it uses `is_upsell=True` to give them FULL_CONTENT. You'll need to decide:
- Option A: Remove parameter (use ESSENTIAL)
- Option B: Keep using FULL content for guide downloads (customer paid, might as well give them everything)

---

### Phase 2: Database Changes

#### 1. Remove Upsell Model
**File:** `backend/database.py`

**Changes Needed:**
- **Lines 173-201:** Remove entire `Upsell` class definition

**Class to Remove:**
```python
class Upsell(db.Model):
    __tablename__ = 'upsells'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    original_order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    upsell_order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    modules_included = db.Column(db.Text)
    # ... etc
```

#### 2. Drop Database Table
**Production Database Migration:**

```sql
-- Backup existing data (optional)
CREATE TABLE upsells_backup AS SELECT * FROM upsells;

-- Drop the table
DROP TABLE IF EXISTS upsells;

-- Verify removal
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_name = 'upsells';
```

**Development (SQLite):**
```bash
# If using SQLite, easiest to just delete and recreate
rm backend/napocalypse.db
# Database will recreate without upsells table on next run
```

---

### Phase 3: Frontend Changes

#### 1. Delete Upsell Page
**File:** `frontend/upsell.html`
- ✅ Action: DELETE ENTIRE FILE (616 lines)

#### 2. Remove Upsell CTAs from Blog Posts
**11 Blog Post Files to Edit:**

1. `frontend/blog/sarah-cio-feeding-success.html`
2. `frontend/blog/sarah-cio-feeding-success-story.html`
3. `frontend/blog/rachel-gentle-feeding-success.html`
4. `frontend/blog/lisa-cio-naps-success.html`
5. `frontend/blog/tom-cio-early-morning-success.html`
6. `frontend/blog/mike-cio-motion-success.html`
7. `frontend/blog/mike-cio-rocking-success-story.html`
8. `frontend/blog/david-gentle-motion-success.html`
9. `frontend/blog/chris-gentle-naps-success.html`
10. `frontend/blog/amy-gentle-pacifier-success.html`
11. `frontend/blog/jessica-gentle-early-morning-success.html`

**In Each File, Remove:**
- CSS for `.upsell-box` class (typically lines ~199-228)
- HTML upsell box section (typically lines ~420-451)
- Links to `/upsell?story={name}`

**Example of what to remove:**
```html
<div class="upsell-box">
    <h3>Ready to Go Deeper?</h3>
    <p>The Essential Guide got Sarah started, but the Advanced Playbook answered every specific question...</p>
    <a href="/upsell?story=sarah" class="upsell-button">Get Advanced Playbook Now</a>
</div>
```

---

### Phase 4: Content Module Cleanup

#### Remove "When to Upgrade" Sections

**4 Files to Edit:**

1. **`content/modules/module_2_sleep_training_readiness_FULL_CONTENT.md`**
   - Lines 822-825: Remove upsell product mentions

2. **`content/modules/module_5_cry_it_out_FULL_CONTENT.md`**
   - Lines 764-767: Remove upsell section

3. **`content/modules/module_6_gentle_methods_FULL_CONTENT.md`**
   - Lines 565+: Remove upsell section

4. **`content/modules/module_7_feeding_to_sleep_FULL_CONTENT.md`**
   - Lines 799+: Remove upsell section

**Example of what to remove:**
```markdown
**When to Upgrade:**
- **Sleep Regression Guide** ($27) for 8-month regression
- **Nap Training Deep Dive** ($27) if naps remain challenging
- **Toddler Transitions** ($37) when baby approaches 12 months
```

---

### Phase 5: Verification & Testing

#### Import Verification
```bash
# Check for any remaining references
grep -r "upsell" backend/ --include="*.py"
grep -r "Upsell" backend/ --include="*.py"
grep -r "is_upsell" backend/ --include="*.py"
```

#### Functionality Testing
- [ ] App starts without errors: `python backend/app.py`
- [ ] Quiz submission works
- [ ] Payment flow works (quiz → Stripe → success)
- [ ] Webhook processes payments correctly
- [ ] Quick-Start Guide PDF generates
- [ ] Delivery email sends with PDF
- [ ] 14-day sequence schedules correctly
- [ ] Blog posts display correctly (no broken links)
- [ ] No 404 errors for removed routes
- [ ] Database queries don't reference upsells table

#### Database Verification
```sql
-- Ensure upsells table doesn't exist
SELECT * FROM information_schema.tables WHERE table_name = 'upsells';

-- Verify orders table still works
SELECT COUNT(*) FROM orders WHERE status = 'completed';
```

---

## Important Decisions Needed

### 1. Content Version Strategy

**Current State:** System uses ESSENTIAL content (condensed versions)

**Question:** Should customers get ESSENTIAL or FULL_CONTENT going forward?

**Options:**
- **Option A (Current):** Keep ESSENTIAL
  - Pros: Shorter PDFs (10-20 pages), easier to digest
  - Cons: Less comprehensive

- **Option B:** Switch to FULL_CONTENT
  - Pros: More comprehensive, customers get "everything"
  - Cons: Longer PDFs (40-60 pages), potentially overwhelming

**Recommendation:** Decide this separately from upsell removal. For now, keep ESSENTIAL.

### 2. Guide Download Route

**Current:** `/api/generate-full-guide` uses `is_upsell=True` (gives FULL content)

**Question:** Should the download route give ESSENTIAL or FULL content?

**Recommendation:**
- If keeping ESSENTIAL for initial PDF, still give FULL for download (customer already paid)
- OR keep both ESSENTIAL for consistency

---

## Files Summary

### Files to Delete (2):
1. ✅ `backend/routes/upsell.py` (DONE)
2. `frontend/upsell.html`

### Files to Edit (22+):
1. ✅ `backend/app.py` (DONE)
2. ✅ `backend/routes/webhook_routes.py` (DONE)
3. ✅ `backend/services/email_service.py` (DONE)
4. `backend/services/pdf_generator.py`
5. `backend/routes/guide_routes.py`
6. `backend/database.py`
7-17. 11 blog post HTML files
18-21. 4 module FULL_CONTENT.md files
22. Database migration script (new)

### Backend Python Files Affected:
- app.py ✅
- database.py (pending)
- routes/webhook_routes.py ✅
- routes/guide_routes.py (pending)
- routes/upsell.py ✅ (deleted)
- services/email_service.py ✅
- services/pdf_generator.py (pending)

---

## Risk Assessment

### ✅ LOW RISK (Safe to proceed):
- Core purchase flow is independent
- Email sequence is separate
- Webhook simplification is straightforward

### ⚠️ MEDIUM RISK (Test carefully):
- Blog post HTML editing (11 files)
- Database model removal
- PDF generator refactoring

### ⚠️ HIGH RISK (Requires careful testing):
- **pdf_generator.py** changes affect ALL PDF generation
  - Mitigation: Test thoroughly before/after
- **guide_routes.py** affects user's ability to download their guide
  - Mitigation: Ensure download still works

---

## Rollback Plan

If issues occur after deployment:

1. **Backend Code:** Restore from git
   ```bash
   git checkout HEAD~1 backend/
   ```

2. **Database:** Restore upsells table from backup
   ```sql
   CREATE TABLE upsells AS SELECT * FROM upsells_backup;
   ```

3. **Frontend:** Restore blog posts from git
   ```bash
   git checkout HEAD~1 frontend/blog/
   ```

---

## Next Steps

1. **Review this document** and decide on content strategy (ESSENTIAL vs FULL)
2. **Approve continuation** of removal process
3. **Complete Phase 1** (pdf_generator.py and guide_routes.py)
4. **Execute Phase 2** (database changes with backup)
5. **Execute Phase 3** (frontend/blog cleanup)
6. **Execute Phase 4** (content module cleanup)
7. **Execute Phase 5** (comprehensive testing)
8. **Deploy** to production (with rollback plan ready)

---

## Estimated Time Remaining

- Phase 1 (remaining): 1-2 hours
- Phase 2: 1 hour
- Phase 3: 2-3 hours
- Phase 4: 1 hour
- Phase 5: 2-3 hours
- **Total: 7-10 hours**

---

## Notes

- The 14-day email sequence templates (`new_day_1.html` through `new_day_14.html`) do NOT contain upsell references - they're clean
- Email templates may have `{{upsell_url}}` placeholders that will simply be left unreplaced (won't break emails)
- Some marketing copy mentions "Advanced Playbook" as a product name - these are OK to keep in docs
- The `is_upsell` parameter removal is mostly cosmetic - system already defaults to ESSENTIAL

---

## Questions for Review

1. **Content Strategy:** ESSENTIAL or FULL content for customers?
2. **Guide Download:** Should `/api/generate-full-guide` give FULL or ESSENTIAL?
3. **Timeline:** When should this be deployed to production?
4. **Testing:** Do you want to test on staging/dev environment first?
5. **Backup:** Do you need historical upsell data preserved?

---

**Last Updated:** 2025-11-16
**Next Review:** Pending user approval to continue

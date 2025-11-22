# Aggressive Cleanup Plan - Remove ALL Legacy Code

**Goal:** Keep ONLY the code needed for Quick-Start Guide + 14-day email sequence

**Philosophy:** Delete everything. Re-build features later when needed (instead of maintaining dead code)

---

## Current System (What We're Keeping)

### The Working Flow:
1. Customer completes quiz → Pays $47
2. Stripe webhook → Generate Quick-Start Guide PDF
3. Email PDF immediately to customer
4. Schedule 14-day email sequence (no PDFs)
5. Done!

### Quick-Start Guide Personalization:
- Already personalizes with `{customer_name}` placeholder
- Can easily add more personalization later (quiz data, baby age, etc.)
- Currently in: `content/quick_start_guide.md`

---

## Files to DELETE ENTIRELY

### 1. Backend Routes
- ✅ `backend/routes/upsell.py` (ALREADY DELETED)
- **DELETE:** `backend/routes/guide_routes.py` (unused download endpoint)

### 2. Frontend Pages
- **DELETE:** `frontend/upsell.html` (upsell landing page)

### 3. Database Models
- **REMOVE:** `Upsell` class from `backend/database.py` (lines 173-201)

---

## Files to HEAVILY EDIT (Remove Large Sections)

### 1. `backend/services/pdf_generator.py`

**Current:** 2,264 lines
**After Cleanup:** ~300 lines (87% reduction!)

**DELETE Lines 90-2174 (2,084 lines!):**
- `generate_personalized_pdf()` - entire function
- `generate_html_content()` - entire function
- `generate_module_content()` - entire function
- All module selection logic
- All ESSENTIAL vs FULL_CONTENT switching
- All is_upsell parameter handling
- All V1/V2 system code

**KEEP:**
- Lines 1-89: Imports, utilities, config
- Lines 2175-2264: `generate_quick_start_guide_pdf()` function
- Supporting CSS/HTML styling

**Result:** One simple function that loads a markdown file and generates a PDF

---

### 2. `backend/app.py`

**REMOVE:**
- ✅ `from routes.upsell import upsell_bp` (ALREADY DONE)
- ✅ `app.register_blueprint(upsell_bp)` (ALREADY DONE)
- **REMOVE:** `from routes import ... guide_bp`
- **REMOVE:** `app.register_blueprint(guide_bp)`

---

### 3. `backend/database.py`

**REMOVE:**
- Lines 173-201: Entire `Upsell` model class

**Database Migration:**
```sql
-- Backup (optional)
CREATE TABLE upsells_backup AS SELECT * FROM upsells;

-- Drop table
DROP TABLE IF EXISTS upsells;
```

---

### 4. Frontend Blog Posts (11 files)

**In each file, REMOVE:**
- `.upsell-box` CSS class (~30 lines)
- Upsell HTML box section (~30 lines)
- Links to `/upsell?story={name}`

**Files:**
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

---

### 5. Content Modules (4 files)

**REMOVE "When to Upgrade" sections:**
1. `content/modules/module_2_sleep_training_readiness_FULL_CONTENT.md` (lines ~822-825)
2. `content/modules/module_5_cry_it_out_FULL_CONTENT.md` (lines ~764-767)
3. `content/modules/module_6_gentle_methods_FULL_CONTENT.md` (lines ~565+)
4. `content/modules/module_7_feeding_to_sleep_FULL_CONTENT.md` (lines ~799+)

---

## Additional Cleanup Opportunities

### Legacy Content Files (Probably Unused)

**QUESTION: Are these module files even used anymore?**

If your system ONLY uses `content/quick_start_guide.md`, then you could DELETE:
- `content/modules/` entire directory (24 files)
  - All `*_ESSENTIAL.md` files
  - All `*_FULL_CONTENT.md` files
  - Module selection logic is already gone

**Verify first:**
```bash
# Check if modules directory is referenced anywhere
grep -r "content/modules" backend/
```

If no results (except pdf_generator.py which we're cleaning), **DELETE THE ENTIRE DIRECTORY**.

---

### Content Blocks (V2 System - Unused)

**Directory:** `content_blocks/`
- `age/` - 4 files
- `challenge/` - 5 files
- `method/` - 2 files
- `situation/` - 2 files

**Total:** 13 files for block-based system

**Status:** Partially implemented V2 system, never completed

**Recommendation:** **DELETE** entire `content_blocks/` directory if:
- Your system uses `quick_start_guide.md` only
- You're not planning to use block-based personalization

---

### Service Files (Check Usage)

**Files to investigate:**

1. **`backend/services/module_selector.py`**
   - Used by deleted `generate_personalized_pdf()`
   - If not used elsewhere: **DELETE**

2. **`backend/services/block_selector.py`**
   - For V2 block system (unused)
   - **DELETE**

3. **`backend/services/personalization.py` & `personalization_v2.py`**
   - For module/block personalization
   - If not used elsewhere: **DELETE**

4. **`backend/services/template_engine.py`**
   - For V2 system
   - **DELETE**

5. **`backend/services/transitions.py`**
   - Check usage
   - If unused: **DELETE**

---

## What We're KEEPING (The Essentials)

### Backend Core:
- ✅ `app.py` (simplified)
- ✅ `config.py`
- ✅ `database.py` (minus Upsell model)
- ✅ `scheduler.py`

### Backend Routes:
- ✅ `routes/quiz_routes.py` (quiz submission)
- ✅ `routes/payment_routes.py` (create Stripe checkout)
- ✅ `routes/webhook_routes.py` (handle successful payments)
- ❌ `routes/guide_routes.py` (DELETE - unused)
- ❌ `routes/upsell.py` (DELETED)

### Backend Services:
- ✅ `services/email_service.py` (delivery email + 14-day sequence)
- ✅ `services/pdf_generator.py` (HEAVILY TRIMMED - just Quick-Start function)
- ❌ `services/module_selector.py` (DELETE if unused)
- ❌ `services/block_selector.py` (DELETE)
- ❌ `services/personalization.py` (DELETE if unused)
- ❌ `services/personalization_v2.py` (DELETE)
- ❌ `services/template_engine.py` (DELETE)
- ❌ `services/advanced_playbook_service.py` (ALREADY DELETED)

### Database Tables:
- ✅ `customers`
- ✅ `quiz_responses`
- ✅ `orders`
- ✅ `modules_assigned` (might be unused now - verify)
- ✅ `email_sequences`
- ❌ `upsells` (DROP)

### Content:
- ✅ `content/quick_start_guide.md` (the ONE file that matters!)
- ✅ `content/blog/` (success stories)
- ❌ `content/modules/` (DELETE if unused - 24 files)
- ❌ `content_blocks/` (DELETE if unused - 13 files)

### Frontend:
- ✅ All core pages (index, quiz, success, etc.)
- ✅ Blog posts (cleaned of upsell CTAs)
- ❌ `upsell.html` (DELETE)

---

## Execution Order

### Phase 1: Backend Cleanup
1. Delete `backend/routes/guide_routes.py`
2. Remove guide_bp from `app.py`
3. Delete lines 90-2174 from `pdf_generator.py`
4. Remove Upsell model from `database.py`
5. Verify and delete unused service files

### Phase 2: Database
6. Drop `upsells` table
7. Check if `modules_assigned` table is still used (probably not)

### Phase 3: Content Cleanup
8. Verify `content/modules/` is unused → DELETE directory
9. Verify `content_blocks/` is unused → DELETE directory
10. Remove upgrade sections from remaining module files (if keeping them)

### Phase 4: Frontend
11. Delete `frontend/upsell.html`
12. Clean 11 blog posts (remove upsell CTAs)

### Phase 5: Verification
13. Test complete flow (quiz → payment → PDF → emails)
14. Check for broken imports
15. Verify no 404 errors

---

## Expected Results

### Files Deleted:
- 2 route files
- 1 frontend page
- 5 service files (module_selector, block_selector, 3 personalization files)
- 24 module files (if unused)
- 13 content block files (if unused)
- **Total: ~45 files deleted**

### Lines of Code Removed:
- pdf_generator.py: -2,084 lines
- database.py: -29 lines
- Service files: ~1,500 lines
- **Total: ~3,600+ lines removed**

### Code Reduction:
- **Before:** ~8,000 lines of Python code
- **After:** ~4,400 lines
- **Reduction:** 45% smaller codebase!

---

## Future Personalization (When Needed)

When you want to add quiz-based personalization to Quick-Start Guide:

**Simple Approach:**
1. Edit `content/quick_start_guide.md`
2. Add conditional sections with placeholders:
   ```markdown
   {if baby_age == "0-3 months"}
   Your newborn needs...
   {endif}

   {if sleep_philosophy == "gentle"}
   We'll use gentle methods...
   {endif}
   ```

3. Update `generate_quick_start_guide_pdf()` to:
   - Load quiz data
   - Replace placeholders with appropriate content
   - Keep it in ONE function, ONE file

**NO NEED FOR:**
- Module selection system
- Block-based system
- Separate ESSENTIAL/FULL versions
- Complex personalization service

**Start simple, add complexity only when proven necessary.**

---

## Risk Assessment

### ✅ VERY LOW RISK:
- Deleting unused route files
- Removing dead code from pdf_generator.py
- Deleting upsell.html

### ⚠️ LOW RISK:
- Deleting service files (verify usage first)
- Dropping upsells table
- Cleaning blog posts

### ⚠️ MEDIUM RISK:
- Deleting content/modules/ directory (verify not used)
- Removing Upsell model (check for foreign key constraints)

### Testing Required:
- Complete purchase flow
- PDF generation
- Email delivery
- 14-day sequence scheduling

---

## Verification Checklist

Before declaring success:

- [ ] App starts without errors
- [ ] Quiz submission works
- [ ] Payment creates order
- [ ] Webhook processes payment
- [ ] Quick-Start PDF generates correctly
- [ ] Delivery email sends with PDF
- [ ] 14-day sequence schedules
- [ ] No import errors in logs
- [ ] No broken frontend links
- [ ] No database constraint errors
- [ ] Blog posts display correctly

---

## Next Steps

**Ready to execute this aggressive cleanup?**

The order will be:
1. Verify what's actually used (modules, blocks, services)
2. Delete unused files
3. Trim pdf_generator.py to essentials
4. Clean database
5. Clean frontend
6. Test everything
7. Celebrate 45% code reduction! 🎉

---

**This is the lean, maintainable codebase you deserve!**

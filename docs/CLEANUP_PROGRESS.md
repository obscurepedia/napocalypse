# Upsell Removal - Progress Report

## ✅ COMPLETED

### Backend Files:
1. ✅ **app.py** - Removed upsell_bp import and registration
2. ✅ **routes/webhook_routes.py** - Simplified webhook logic (removed upsell session handling)
3. ✅ **services/email_service.py** - Removed upsell URL injection and send_upsell_confirmation_email()
4. ✅ **routes/upsell.py** - DELETED (433 lines)
5. ✅ **routes/guide_routes.py** - DELETED (entire file)
6. ✅ **database.py** - Removed Upsell model class (lines 173-201)

### Frontend Files:
7. ✅ **frontend/upsell.html** - DELETED

## 🔄 IN PROGRESS

### Blog Posts (11 files):
Need to remove from each:
- CSS: `.upsell-box`, `.upsell-benefits` styles (~27 lines each)
- HTML: `<div class="upsell-box">...</div>` section (~37 lines each)
- Link: `/upsell?story={name}`

**Files:**
1. frontend/blog/sarah-cio-feeding-success.html
2. frontend/blog/sarah-cio-feeding-success-story.html
3. frontend/blog/rachel-gentle-feeding-success.html
4. frontend/blog/lisa-cio-naps-success.html
5. frontend/blog/tom-cio-early-morning-success.html
6. frontend/blog/mike-cio-motion-success.html
7. frontend/blog/mike-cio-rocking-success-story.html
8. frontend/blog/david-gentle-motion-success.html
9. frontend/blog/chris-gentle-naps-success.html
10. frontend/blog/amy-gentle-pacifier-success.html
11. frontend/blog/jessica-gentle-early-morning-success.html

## ⏸️ PENDING

### Content Modules (4 files):
Remove "When to Upgrade" sections:
1. content/modules/module_2_sleep_training_readiness_FULL_CONTENT.md
2. content/modules/module_5_cry_it_out_FULL_CONTENT.md
3. content/modules/module_6_gentle_methods_FULL_CONTENT.md
4. content/modules/module_7_feeding_to_sleep_FULL_CONTENT.md

### Final Steps:
- Verification (search for remaining "upsell" references)
- Database migration (drop upsells table in production)
- Testing

## CODE REDUCTION

**Lines removed so far:** ~700+
- upsell.py: 433 lines
- guide_routes.py: 48 lines
- send_upsell_confirmation_email(): 147 lines
- Upsell model: 29 lines
- Upsell URL injection: 16 lines
- upsell.html: ~616 lines (not counted in backend)

**Estimated additional removal:**
- Blog posts: ~64 lines × 11 = 704 lines
- Content modules: ~20 lines × 4 = 80 lines

**Total reduction: ~1,500+ lines of code**

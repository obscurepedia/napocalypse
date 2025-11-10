# Deployment Checklist for V2 Condensed Blocks

## Quick Summary
✅ **Problem:** V2 was producing 57-page guides  
✅ **Solution:** Created condensed blocks that produce 16-20 page guides  
✅ **Status:** Ready to deploy  

---

## Files to Deploy (8 files total)

### 1. Method Blocks (2 files)
Copy to: `/path/to/deployed/content_blocks/method/`

- [ ] `method_gentle_combined.md` (1,258 words)
- [ ] `method_cio_combined.md` (1,394 words)

### 2. Age Blocks (4 files)
Copy to: `/path/to/deployed/content_blocks/age/`

- [ ] `age_4_6_months_condensed.md` (375 words)
- [ ] `age_7_12_months_condensed.md` (375 words)
- [ ] `age_13_18_months_condensed.md` (400 words)
- [ ] `age_19_24_months_condensed.md` (400 words)

### 3. Block Selector (1 file)
Copy to: `/path/to/deployed/backend/services/`

- [ ] `block_selector.py` (updated to use condensed blocks)

---

## Pre-Deployment Testing

### Test 1: Verify Block Selector
```bash
cd /path/to/deployed/backend/services
python block_selector.py
```

**Expected output:**
```
Test Case 1 - Deenah (Gentle, Motion, Room Sharing):
Blocks: ['age_7_12_months_condensed', 'method_gentle_combined', 'challenge_motion_dependency', 'situation_room_sharing']
Count: 4 blocks
Estimated pages: 20

Test Case 2 - CIO, Feeding, No Situation:
Blocks: ['age_4_6_months_condensed', 'method_cio_combined', 'challenge_feeding_to_sleep']
Count: 3 blocks
Estimated pages: 16

Test Case 3 - Toddler, Early Morning, Apartment (not included):
Blocks: ['age_19_24_months_condensed', 'method_cio_combined', 'challenge_early_morning_waking']
Count: 3 blocks
Estimated pages: 16
```

### Test 2: Generate Sample Guide
Use Deenah's quiz responses to generate a test guide:

```python
quiz_responses = {
    'baby_age': '7-12',
    'sleep_method': 'gentle',
    'main_challenge': 'rocking',
    'secondary_challenge': 'pacifier',
    'room_sharing': True
}

# Generate guide
template_engine = TemplateEngine()
guide = template_engine.generate_guide(customer_data, quiz_responses)

# Convert to PDF
pdf_generator = PDFGenerator()
pdf_path = pdf_generator.generate_v2_guide_pdf(guide, "Deenah", "Yoel")

# Check page count
# Should be approximately 20 pages
```

### Test 3: Verify Content Quality
- [ ] Read through generated guide
- [ ] Verify no contradictions between sections
- [ ] Verify smooth transitions between blocks
- [ ] Verify all personalization variables replaced
- [ ] Verify method is consistent throughout

---

## Deployment Steps

### Step 1: Backup Current System
```bash
# Backup current content blocks
cp -r /path/to/deployed/content_blocks /path/to/backup/content_blocks_$(date +%Y%m%d)

# Backup current block selector
cp /path/to/deployed/backend/services/block_selector.py /path/to/backup/block_selector_$(date +%Y%m%d).py
```

### Step 2: Deploy New Files
```bash
# Deploy method blocks
cp content_blocks/method/method_gentle_combined.md /path/to/deployed/content_blocks/method/
cp content_blocks/method/method_cio_combined.md /path/to/deployed/content_blocks/method/

# Deploy age blocks
cp content_blocks/age/age_4_6_months_condensed.md /path/to/deployed/content_blocks/age/
cp content_blocks/age/age_7_12_months_condensed.md /path/to/deployed/content_blocks/age/
cp content_blocks/age/age_13_18_months_condensed.md /path/to/deployed/content_blocks/age/
cp content_blocks/age/age_19_24_months_condensed.md /path/to/deployed/content_blocks/age/

# Deploy block selector
cp backend/services/block_selector.py /path/to/deployed/backend/services/
```

### Step 3: Restart Services
```bash
# Restart your application server
sudo systemctl restart napocalypse-app

# Or if using Docker
docker-compose restart
```

### Step 4: Verify Deployment
```bash
# Test block selector
cd /path/to/deployed/backend/services
python block_selector.py

# Check logs for errors
tail -f /path/to/logs/application.log
```

---

## Post-Deployment Monitoring

### First 24 Hours
- [ ] Monitor first 10 orders
- [ ] Verify PDF generation works
- [ ] Check page counts (should be 16-20 pages)
- [ ] Monitor support tickets for confusion
- [ ] Check for any error logs

### First Week
- [ ] Track refund rate (should be lower)
- [ ] Collect customer feedback
- [ ] Monitor support ticket volume
- [ ] Review customer satisfaction scores

### Metrics to Track
- **Page count:** Should be 16-20 pages (down from 57)
- **Refund rate:** Should decrease to 5-8% (from 10-15%)
- **Support tickets:** Should decrease by 30-40%
- **Customer satisfaction:** Should increase to 85-90%

---

## Rollback Plan (If Needed)

If there are critical issues:

```bash
# Restore backup files
cp -r /path/to/backup/content_blocks_YYYYMMDD/* /path/to/deployed/content_blocks/
cp /path/to/backup/block_selector_YYYYMMDD.py /path/to/deployed/backend/services/block_selector.py

# Restart services
sudo systemctl restart napocalypse-app

# Verify rollback
cd /path/to/deployed/backend/services
python block_selector.py
```

---

## Success Criteria

### Immediate (Day 1)
- ✅ All files deployed successfully
- ✅ Block selector test passes
- ✅ First guide generates successfully
- ✅ Page count is 16-20 pages
- ✅ No errors in logs

### Short-term (Week 1)
- ✅ 10+ guides generated successfully
- ✅ No customer complaints about page count
- ✅ No increase in support tickets
- ✅ Positive customer feedback

### Long-term (Month 1)
- ✅ Refund rate decreased to 5-8%
- ✅ Support tickets decreased by 30-40%
- ✅ Customer satisfaction increased to 85-90%
- ✅ Average review rating increased

---

## Troubleshooting

### Issue: Block selector can't find condensed files
**Solution:** Verify file names match exactly:
```bash
ls -la /path/to/deployed/content_blocks/age/
# Should see: age_7_12_months_condensed.md (not age_7_12_months.md)

ls -la /path/to/deployed/content_blocks/method/
# Should see: method_gentle_combined.md (not method_gentle_overview.md)
```

### Issue: Guide still too long
**Solution:** Check which blocks are being selected:
```python
selector = BlockSelector()
blocks = selector.select_blocks(quiz_responses)
print(f"Blocks: {blocks}")
print(f"Count: {len(blocks)}")
```

Should be 3-4 blocks, not 6.

### Issue: Content seems incomplete
**Solution:** The condensed blocks are intentionally shorter. They focus on essential information only. If customers need more detail, that's what the Advanced Playbook upsell is for.

---

## Contact & Support

If you encounter issues during deployment:
1. Check the logs first
2. Verify all files are in correct locations
3. Test block selector independently
4. Generate a test guide manually
5. Review this checklist again

---

## Final Checklist

Before marking deployment as complete:

- [ ] All 8 files deployed
- [ ] Block selector test passes
- [ ] Sample guide generated successfully
- [ ] Page count verified (16-20 pages)
- [ ] No errors in logs
- [ ] Backup created
- [ ] Rollback plan documented
- [ ] Monitoring in place
- [ ] Team notified of deployment

---

**Status:** Ready for deployment  
**Risk Level:** Low (can rollback easily)  
**Expected Impact:** 65% reduction in page count  
**Timeline:** 30 minutes to deploy and verify  

---

*Follow this checklist step-by-step to ensure smooth deployment.*
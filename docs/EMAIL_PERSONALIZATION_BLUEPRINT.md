# EMAIL PERSONALIZATION BLUEPRINT
## 14-Day Sleep Coaching Email Sequence - Deep Personalization Strategy

---

## 1. EXECUTIVE SUMMARY

### Vision
Transform the 14-day email sequence from generic content with occasional personalization into a deeply personalized experience where every email makes parents feel like it was written specifically for them. Every email should reference their unique combination of: baby's age, sleep struggles, chosen method, living situation, parenting setup, work schedule, specific challenge, and current sleep associations.

### The Promise Gap
**What we promise on the sales page:**
- "14-day email course customized for YOUR situation"
- "Personalized Daily Content - Your course adapts to the method you choose"
- "Solutions for YOUR Challenges"
- "Personalized to Your Child & Method"

**What we currently deliver:**
- Only 4 of 14 emails use content blocks (Days 4, 5, 8, 13)
- Day 13's situation-based content doesn't work (personalization.py doesn't set 'situation')
- 6 of 8 quiz data points are completely ignored
- Most emails only use `{customer_name}` and `{method}` as text replacement

### The Goal
Every single email should make parents think: "Wow, this was written specifically for me and my situation."

---

## 2. TONE GUIDE

Based on analysis of all 14 current email templates, the tone that must be maintained:

### Voice Characteristics
- **First-person conversational**: "I know you're..." not "Parents often feel..."
- **Direct and reassuring**: Addresses fears and doubts head-on
- **Empathetic without being pitying**: "I see you" not "Poor you"
- **Confident but not preachy**: Gives advice as a trusted friend, not a lecturer
- **Uses "you" heavily**: Makes it personal, not theoretical
- **Includes light humor**: Coffee jokes, ice cream references - keeps it human
- **Action-oriented**: Every email has a clear, simple task

### Phrases to Maintain
- "Here's what I need you to hear:"
- "You've got this"
- "Hit reply and tell me"
- "I read every response"
- "You're not failing"
- "Trust yourself"

### Phrases to Avoid
- "Many parents find that..."
- "Research shows..."
- "In general..."
- "Parents typically..."
- Generic advice that could apply to anyone

### Structure to Maintain
1. Personal greeting with name
2. Empathetic opening that acknowledges their feelings
3. Key insight or lesson
4. Actionable task in a styled box
5. What to expect next
6. Personal sign-off encouraging reply
7. Consistent footer with Isaac's signature

---

## 3. QUIZ DATA MAPPING

### All 8 Quiz Data Points

| Quiz Question | Database Field | Values | Current Usage | Target Usage |
|--------------|----------------|--------|---------------|--------------|
| Baby's age | `baby_age` | 0-3mo, 4-6mo, 7-12mo, 13-18mo, 19-24mo | Day 4 only | Every email |
| Biggest sleep struggle | `biggest_challenge` | wakes 1-2hr, wakes 3-5x, wakes 1-2x, 30min to sleep, early waking, naps disaster | Day 8 only | Most emails |
| Method preference | `method_preference` | CIO, gentle only, gradual, not sure | Days 5-6 only | Every email after Day 4 |
| Living situation | `living_situation` | apartment, house w/nursery, room sharing, sibling sharing | Day 13 (broken) | Days 2, 5, 9, 13 |
| Parenting setup | `parenting_setup` | two sharing, single, one does nights, grandparents | NEVER USED | Days 1, 5, 6, 9, 13 |
| Work schedule | `work_schedule` | stay-at-home, working, shift work, WFH | NEVER USED | Days 1, 3, 7, 8, 14 |
| #1 specific challenge | `specific_challenge` | no sleep w/o feeding, no sleep w/o rocking, wakes when put down, bedtime 1hr+, naps impossible, wakes too early | Indirectly via modules | Days 3, 8, 10, 11 |
| Current sleep association | `sleep_association` | nursing/bottle, rocking/bouncing, pacifier, cosleeping, multiple | NEVER USED | Days 3, 5, 10, 11 |

---

## 4. DAY-BY-DAY PERSONALIZATION BLUEPRINT

### DAY 1: Your Sleep Journey Starts Here

**Purpose/Goal**: Welcome, build confidence, first observation task

**Current State**: Only uses `{customer_name}`

**Quiz Data Points to Use**:
- Baby's age (set expectations)
- Parenting setup (acknowledge their support system)
- Work schedule (acknowledge time pressures)
- Biggest sleep struggle (validate their specific pain)

**Content Blocks Needed**:
- NEW: `intro_age_4_6_months.md`, `intro_age_7_12_months.md`, `intro_age_13_18_months.md`, `intro_age_19_24_months.md`
- NEW: `intro_parenting_single.md`, `intro_parenting_shared.md`, `intro_parenting_solo_nights.md`
- NEW: `intro_work_stay_home.md`, `intro_work_working.md`, `intro_work_shift.md`

**Personalization Examples**:

Instead of:
> "I know you're exhausted. I know you've tried 'everything' and nothing has worked."

Personalized version for single working parent with 7-month-old who wakes every 1-2 hours:
> "I know you're exhausted. Waking every 1-2 hours with a 7-month-old, and doing it alone while holding down a job - that's survival mode. I know you've tried 'everything' and nothing has worked."

**Conditional Sections**:
- IF `parenting_setup` = single: Add "And since you're doing nights alone, I've designed this to be manageable single-handedly."
- IF `work_schedule` = working: Add "I know you need results before Monday."
- IF `biggest_challenge` = wakes_every_1_2_hours: Reference this specifically in the opening

**Variables**:
```
{customer_name}
{baby_age_short} (e.g., "7-month-old")
{biggest_challenge_text} (e.g., "waking every 1-2 hours")
{parenting_setup_context}
{work_schedule_context}
{age_intro_block}
```

---

### DAY 2: The Perfect Sleep Environment

**Purpose/Goal**: Optimize sleep space - darkness and white noise

**Current State**: Only uses `{customer_name}`

**Quiz Data Points to Use**:
- Living situation (apartment = noise concerns, room sharing = logistics)
- Baby's age (room setup varies by age)
- Parenting setup (who implements)

**Content Blocks Needed**:
- NEW: `environment_apartment.md` (noise concerns, neighbor considerations)
- NEW: `environment_room_sharing.md` (how to dark/quiet a shared space)
- NEW: `environment_house.md` (nursery optimization)
- NEW: `environment_sibling_sharing.md` (managing two kids' needs)

**Personalization Examples**:

Instead of:
> "Go into your baby's room during the middle of the day. Close the door."

For apartment dweller who room-shares:
> "Since you're room-sharing in an apartment, this takes a bit more creativity. Go to your bedroom during the middle of the day. You'll want to create a dark zone around the crib area specifically - a room divider with blackout curtains works wonders. And the white noise will do double duty: helping your baby AND covering any apartment noise."

**Conditional Sections**:
- IF `living_situation` = apartment: Include neighbor noise mitigation
- IF `living_situation` = room_sharing: Include separation strategies
- IF `baby_age` >= 13mo: Include mention of checking for light-up toys they can activate

**Variables**:
```
{customer_name}
{living_situation_context}
{environment_block}
{age_specific_environment_note}
```

---

### DAY 3: The Magic of a Bedtime Routine

**Purpose/Goal**: Build simple, consistent 3-step routine

**Current State**: Only uses `{customer_name}`

**Quiz Data Points to Use**:
- Sleep association (feeding vs rocking vs pacifier changes routine order)
- Work schedule (affects routine timing/feasibility)
- Baby's age (routine complexity varies)
- Specific challenge (if bedtime takes 1hr+, address directly)

**Content Blocks Needed**:
- NEW: `routine_feeding_association.md` (how to include feeding without creating dependency)
- NEW: `routine_rocking_association.md` (alternative soothing in routine)
- NEW: `routine_pacifier_association.md` (when to offer pacifier in routine)
- NEW: `routine_working_parent.md` (quick routines for tired parents)
- NEW: `routine_age_baby.md` (4-12mo routine)
- NEW: `routine_age_toddler.md` (13mo+ routine with more steps)

**Personalization Examples**:

Instead of:
> "Feed & Cuddle - If feeding is part of your routine, keep it calm and quiet."

For parent whose baby currently feeds to sleep:
> "Since your baby currently needs nursing/bottle to fall asleep, we're going to be strategic here. Feed FIRST - before bath, before book, before anything else. This creates a buffer so they don't associate that full belly with falling asleep. Keep them awake during the feed if you can (lights a bit brighter, talk to them). Then proceed to bath and book."

For working parent:
> "I know you get home at 6 and bedtime is 7 - you don't have an hour for an elaborate routine. Good news: you don't need one. Here's a 15-minute version that's just as effective..."

**Conditional Sections**:
- IF `sleep_association` = nursing/bottle: Lead with feeding reorder strategy
- IF `specific_challenge` = bedtime_takes_over_hour: Add section on routine timing
- IF `work_schedule` = working OR shift_work: Include express routine option
- IF `baby_age` >= 13mo: Add brief toddler routine notes

**Variables**:
```
{customer_name}
{sleep_association_type}
{routine_feeding_strategy_block}
{routine_work_block}
{routine_age_block}
```

---

### DAY 4: Understanding Wake Windows

**Purpose/Goal**: Teach timing concept - the "secret" to easier sleep

**Current State**: Uses `{customer_name}`, `{method}`, and `{age_based_content}` block

**Quiz Data Points to Use**:
- Baby's age (PRIMARY - wake windows vary dramatically)
- Biggest sleep struggle (early morning = specific window advice)
- Specific challenge (naps impossible = wake window emphasis)
- Work schedule (timing around work)

**Content Blocks Currently Used**:
- `age_4_6_months.md`
- `age_7_12_months.md`
- `age_13_18_months.md`
- `age_19_24_months.md`

**Additional Content Blocks Needed**:
- NEW: `wake_window_early_morning.md` (how windows affect early waking)
- NEW: `wake_window_nap_disaster.md` (timing fixes for bad naps)
- NEW: `wake_window_working_parent.md` (managing windows around work schedule)

**Personalization Examples**:

Current age block is good, but add context around struggles:

For parent whose baby wakes too early with nap disasters:
> [After age block] "Since your biggest challenges are early morning waking AND nap disasters, I want you to pay special attention to that last wake window of the day. If it's too long, you get early morning wakes. If it's too short, bedtime is a battle. For your {baby_age_short}, aim for {last_wake_window} before bed."

**Conditional Sections**:
- IF `biggest_challenge` = early_morning_waking: Add last-wake-window emphasis
- IF `biggest_challenge` OR `specific_challenge` includes naps: Add nap timing emphasis
- IF `work_schedule` = shift_work: Add irregular schedule considerations

**Variables**:
```
{customer_name}
{method}
{baby_age_short}
{age_based_content} (existing block)
{wake_window_challenge_block}
{last_wake_window} (calculated from age)
```

---

### DAY 5: Your Sleep Training Method

**Purpose/Goal**: The big night - implement chosen method

**Current State**: Uses `{customer_name}`, `{method}`, and `{method_instructions}` block

**Quiz Data Points to Use**:
- Method preference (PRIMARY)
- Living situation (apartment = noise concerns, room sharing = logistics)
- Parenting setup (who's doing this, partner alignment)
- Sleep association (what they're replacing)
- Baby's age (expectations for crying duration)

**Content Blocks Currently Used**:
- `method_cio.md`
- `method_gentle.md`

**Additional Content Blocks Needed**:
- NEW: `method_cio_apartment.md` (CIO with noise concerns)
- NEW: `method_cio_room_sharing.md` (CIO while room sharing)
- NEW: `method_gentle_apartment.md` (Gentle with noise concerns)
- NEW: `method_gentle_room_sharing.md` (Gentle while room sharing)
- NEW: `method_single_parent.md` (doing it alone)
- NEW: `method_partner_alignment.md` (getting partner on board)
- NEW: `method_age_expectations_baby.md` (4-12mo what to expect)
- NEW: `method_age_expectations_toddler.md` (13mo+ what to expect)

**Personalization Examples**:

Instead of generic method instructions:

For single parent in apartment using CIO with a baby who feeds to sleep:
> "I know tonight feels scary. Doing CIO alone in an apartment adds extra pressure - you're worried about your baby AND about neighbors. Here's what I need you to hear: tonight is the hardest night for YOU, but your neighbors will barely notice (I promise).

> [Method instructions]

> Since your baby currently feeds to sleep, they're going to be confused when you put them down without it. That confusion = crying. But you're not taking away comfort - you're teaching them a new way to find it."

**Conditional Sections**:
- IF `living_situation` = apartment: Add apartment-specific confidence section
- IF `living_situation` = room_sharing: Add room sharing logistics
- IF `parenting_setup` = single: Add single-parent support section
- IF `parenting_setup` = two_sharing: Add partner alignment tips
- IF `sleep_association` != none: Reference what they're changing

**Variables**:
```
{customer_name}
{method}
{method_instructions} (existing block)
{living_situation_method_block}
{parenting_setup_method_block}
{sleep_association_change_text}
{age_expectation_block}
```

---

### DAY 6: Troubleshooting & Staying Strong

**Purpose/Goal**: Normalize hard nights, common challenges, stay consistent

**Current State**: Uses `{customer_name}` and `{method}`

**Quiz Data Points to Use**:
- Method preference (troubleshooting varies by method)
- Parenting setup (staying strong alone vs together)
- Biggest sleep struggle (address their specific likely challenge)
- Living situation (noise guilt for apartment dwellers)

**Content Blocks Needed**:
- NEW: `troubleshoot_cio.md` (CIO-specific issues)
- NEW: `troubleshoot_gentle.md` (Gentle-specific issues)
- NEW: `troubleshoot_single_parent.md` (staying strong alone)
- NEW: `troubleshoot_apartment.md` (noise guilt)
- NEW: `troubleshoot_early_morning.md` (specific to early wakers)
- NEW: `troubleshoot_frequent_waking.md` (specific to frequent wakers)

**Personalization Examples**:

Instead of:
> "The reality: It almost always feels longer than it actually is."

For single parent in apartment with baby who wakes every 1-2 hours:
> "I know last night was hard. Doing this alone, in an apartment, with a baby who was used to waking every 1-2 hours - that's a lot to handle. But you showed up.

> Here's what I need you to know: If your baby cried for 45 minutes, it probably felt like 3 hours. Set a timer tonight - knowing the actual time makes a huge difference. And your neighbors? They've survived one night. They can survive two more."

**Conditional Sections**:
- IF `parenting_setup` = single: Add solo-parent encouragement
- IF `living_situation` = apartment: Add neighbor reassurance
- IF `biggest_challenge` = early_morning_waking: Add specific early morning troubleshooting
- IF `method_type` = cio: Add CIO-specific troubleshooting
- IF `method_type` = gentle: Add Gentle-specific troubleshooting

**Variables**:
```
{customer_name}
{method}
{troubleshoot_method_block}
{troubleshoot_parenting_block}
{troubleshoot_situation_block}
{troubleshoot_challenge_block}
```

---

### DAY 7: Finding the Wins

**Purpose/Goal**: Celebrate progress, identify small wins, build confidence

**Current State**: Only uses `{customer_name}`

**Quiz Data Points to Use**:
- Baby's age (what wins to look for at different ages)
- Biggest sleep struggle (specific wins related to their struggle)
- Work schedule (wins for working parents = functional at work)

**Content Blocks Needed**:
- NEW: `wins_frequent_waker.md` (wins for 1-2hr wakers)
- NEW: `wins_early_morning.md` (wins for early wakers)
- NEW: `wins_nap_disaster.md` (wins for nap strugglers)
- NEW: `wins_bedtime_battle.md` (wins for bedtime strugglers)
- NEW: `wins_working_parent.md` (functional at work = win)

**Personalization Examples**:

Instead of generic win list:

For working parent whose baby was waking every 1-2 hours:
> "Here's what a win looks like for YOU this week:
> - Your baby slept for even ONE 3-hour stretch (that's double what you were getting!)
> - You got through a workday without feeling like a zombie
> - Your baby cried for 20 minutes instead of 45
> - You didn't cave at 2 AM when every cell in your body wanted to

> These aren't small things. Going from waking every 1-2 hours to ANY improvement is massive."

**Conditional Sections**:
- IF `biggest_challenge` = wakes_every_1_2_hours: Longer stretch wins
- IF `biggest_challenge` = early_morning_waking: Later wake time wins
- IF `biggest_challenge` = naps_disaster: Any nap over 30 min wins
- IF `work_schedule` = working: Include work-functioning wins

**Variables**:
```
{customer_name}
{wins_challenge_block}
{wins_work_block}
{baby_age_short}
```

---

### DAY 8: The Tricky World of Naps

**Purpose/Goal**: Nap training, crib hour, cat nap solutions

**Current State**: Uses `{customer_name}`, `{method}`, and `{challenge_based_content}` block

**Quiz Data Points to Use**:
- Specific challenge (PRIMARY - naps impossible gets deeper content)
- Baby's age (nap needs vary dramatically by age)
- Method preference (apply method to naps)
- Work schedule (nap timing around work)

**Content Blocks Currently Used**:
- `challenge_feeding.md`
- `challenge_motion.md`
- `challenge_pacifier.md`
- `challenge_naps.md`
- `challenge_early_morning.md`

**Additional Content Blocks Needed**:
- NEW: `naps_age_4_6_months.md` (3-4 naps, timing)
- NEW: `naps_age_7_12_months.md` (2-3 naps, transition)
- NEW: `naps_age_13_18_months.md` (1-2 naps, transition)
- NEW: `naps_working_parent.md` (naps while at work/daycare)

**Personalization Examples**:

Current challenge blocks are good but add age context:

For 8-month-old whose specific challenge is naps impossible:
> [Challenge block for naps]

> "At 8 months, your baby should be on 2 naps: a morning nap (usually 9-10 AM) and an afternoon nap (usually 1-2 PM). If you're still doing 3 short naps, that might actually be part of the problem - too many sleep opportunities = less sleep pressure per nap."

**Conditional Sections**:
- IF `specific_challenge` = naps_impossible: Use full naps challenge block
- IF `baby_age` = 4-6mo: Add 3-nap schedule guidance
- IF `baby_age` = 7-12mo: Add 2-nap transition guidance
- IF `baby_age` = 13-18mo: Add 1-nap transition guidance
- IF `work_schedule` = working: Add daycare/caregiver nap consistency

**Variables**:
```
{customer_name}
{method}
{challenge_based_content} (existing block)
{naps_age_block}
{naps_work_block}
{baby_age_short}
```

---

### DAY 9: The Dreaded Sleep Regression

**Purpose/Goal**: Prepare for regressions, hold the line, don't panic

**Current State**: Uses `{customer_name}` and `{method}`

**Quiz Data Points to Use**:
- Baby's age (upcoming regression timing)
- Living situation (regression in apartment = concerns)
- Parenting setup (regression alone = tough)

**Content Blocks Needed**:
- NEW: `regression_4_6_months.md` (4-month regression details)
- NEW: `regression_7_12_months.md` (8-10 month regression details)
- NEW: `regression_13_18_months.md` (12 & 18 month regression details)
- NEW: `regression_single_parent.md` (handling regression alone)
- NEW: `regression_apartment.md` (handling regression noise)

**Personalization Examples**:

Instead of generic regression list:

For single parent in apartment with 9-month-old:
> "At 9 months, you're right in the middle of one of the trickiest developmental periods - separation anxiety, crawling, and sometimes standing. All of that can temporarily disrupt sleep.

> Doing this alone in an apartment makes regressions feel extra scary. You're worried about going backward AND about noise. Here's what I need you to hear: regressions are temporary, usually 3-7 days. Your neighbors survived the first round. They'll survive this. And your baby hasn't forgotten how to sleep - they just need you to remind them that the rules still apply."

**Conditional Sections**:
- IF `baby_age` = 4-6mo: Focus on 4-month regression
- IF `baby_age` = 7-12mo: Focus on 8-10 month separation anxiety
- IF `baby_age` = 13-18mo: Focus on 12 & 18 month regressions
- IF `parenting_setup` = single: Add solo-parent regression support
- IF `living_situation` = apartment: Add noise reassurance

**Variables**:
```
{customer_name}
{method}
{regression_age_block}
{regression_parenting_block}
{regression_situation_block}
{baby_age_short}
```

---

### DAY 10: The Pacifier Problem

**Purpose/Goal**: Decide keep/drop pacifier, teach self-replacement or go cold turkey

**Current State**: Uses `{customer_name}` and `{method}`

**Quiz Data Points to Use**:
- Sleep association (PRIMARY - pacifier vs others)
- Baby's age (self-replacement requires 7+ months)
- Specific challenge (if pacifier dependency, this is their main email)

**Content Blocks Needed**:
- NEW: `pacifier_not_relevant.md` (for those without pacifier issue - short version)
- NEW: `pacifier_main_challenge.md` (for those with pacifier as main issue - detailed)
- Existing: Can leverage `challenge_pacifier.md`

**Personalization Examples**:

For parent whose sleep association is NOT pacifier:
> "Today's topic is pacifiers - and I know this might not be your main struggle since your baby's sleep association is nursing to sleep. But it's still worth a quick read because the concept applies: we're teaching your baby to self-soothe without external help, whether that's a pacifier, a bottle, or rocking."

For parent whose sleep association IS pacifier:
> "Today is YOUR day. You told me pacifier reinserting is driving you crazy, and I hear you. Playing binky-pong 8 times a night is exhausting and unsustainable. Let's fix it.

> [Full detailed pacifier content]"

**Conditional Sections**:
- IF `sleep_association` = pacifier: Full detailed email
- IF `sleep_association` != pacifier: Abbreviated version with relevance note
- IF `baby_age` < 7mo: Only cold turkey option (no motor skills)
- IF `baby_age` >= 7mo: Both options available

**Variables**:
```
{customer_name}
{method}
{sleep_association_type}
{pacifier_relevance_block}
{pacifier_age_options}
{baby_age_short}
```

---

### DAY 11: Breaking the Feed-to-Sleep Association

**Purpose/Goal**: Move feed in routine, separate eating from sleeping

**Current State**: Uses `{customer_name}` and `{method}`

**Quiz Data Points to Use**:
- Sleep association (PRIMARY - feeding to sleep vs others)
- Specific challenge (won't sleep without feeding)
- Baby's age (night feed needs vary)
- Parenting setup (breastfeeding logistics)

**Content Blocks Needed**:
- NEW: `feeding_not_relevant.md` (for those without feeding issue)
- NEW: `feeding_main_challenge.md` (detailed version)
- NEW: `feeding_night_needs_baby.md` (4-6mo may still need feeds)
- NEW: `feeding_night_needs_older.md` (7mo+ probably habit not need)
- Existing: Can leverage `challenge_feeding.md`

**Personalization Examples**:

For parent whose sleep association IS nursing/bottle:
> "I know what you're thinking: 'But my baby NEEDS to eat before bed.' And you're right. But there's a difference between feeding before bed and feeding TO sleep. Today we fix that.

> Since nursing to sleep has been your baby's primary way of falling asleep, this is a big change. They're going to be confused. They might protest more than they did on Day 5. That's normal. You're rewriting their sleep rules."

For parent whose association is rocking (not feeding):
> "Today's topic is feeding-to-sleep - and since your baby's main association is rocking, this might not be your primary battle. But the principle is the same: we're removing the last 'crutch' before sleep. Read through this in case you're also feeding close to bedtime, and apply the same logic to tomorrow's discussion of your specific challenge."

**Conditional Sections**:
- IF `sleep_association` = nursing/bottle: Full detailed email
- IF `specific_challenge` = won't_sleep_without_feeding: Full detailed email
- IF above not true: Abbreviated with principle explanation
- IF `baby_age` = 4-6mo: Add night feed may be needed note
- IF `baby_age` >= 7mo: Add night feed probably habit note

**Variables**:
```
{customer_name}
{method}
{sleep_association_type}
{feeding_relevance_block}
{feeding_night_need_block}
{baby_age_short}
```

---

### DAY 12: A Guide to Night Weaning

**Purpose/Goal**: Shift calories to day, eliminate unnecessary night feeds

**Current State**: Uses `{customer_name}` and `{method}`

**Quiz Data Points to Use**:
- Baby's age (night weaning readiness)
- Biggest sleep struggle (frequent waking might need this most)
- Parenting setup (who's doing night feeds)

**Content Blocks Needed**:
- NEW: `weaning_too_young.md` (for 4-6mo - may not be ready)
- NEW: `weaning_ready.md` (for 7mo+ - probably ready)
- NEW: `weaning_frequent_waker.md` (extra emphasis for this group)
- NEW: `weaning_single_parent.md` (doing it alone)

**Personalization Examples**:

For 5-month-old:
> "At 5 months, night weaning is a maybe. Some babies can make it through, others genuinely need calories. Check with your pediatrician before eliminating feeds. If they give you the green light, the gradual method works well at this age."

For 10-month-old who wakes every 1-2 hours:
> "At 10 months, here's the truth: your baby almost certainly doesn't NEED those feeds nutritionally. Their body has learned to expect calories at 11 PM, 1 AM, 3 AM, and 5 AM - so they wake up hungry, even though they could get all those calories during the day.

> Since you've been waking every 1-2 hours, this is likely a big part of why. Night weaning might be the final piece that gets you those long stretches."

**Conditional Sections**:
- IF `baby_age` = 4-6mo: Add check-with-pediatrician emphasis
- IF `baby_age` >= 7mo: Add probably-habit-not-need emphasis
- IF `biggest_challenge` = wakes_every_1_2_hours: Add this-is-your-key section
- IF `parenting_setup` = single: Add doing-it-alone support

**Variables**:
```
{customer_name}
{method}
{weaning_age_block}
{weaning_challenge_block}
{weaning_parenting_block}
{baby_age_short}
```

---

### DAY 13: Life Happens - Staying on Track

**Purpose/Goal**: Handle travel, illness, visitors without losing progress

**Current State**: Uses `{customer_name}`, `{method}`, and `{situation_based_content}` (broken)

**Quiz Data Points to Use**:
- Living situation (PRIMARY - apartment/room sharing specific advice)
- Parenting setup (grandparent involvement = visitor section)
- Work schedule (travel for work)
- Baby's age (illness frequency varies)

**Content Blocks Currently Exists But Not Working**:
- `situation_room_sharing.md`
- `situation_apartment.md`

**Additional Content Blocks Needed**:
- NEW: `disruption_grandparents.md` (managing well-meaning help)
- NEW: `disruption_work_travel.md` (travel for work)
- NEW: `disruption_siblings.md` (sibling room sharing)
- FIX: Backend needs to set 'situation' variable from quiz_data['living_situation']

**Personalization Examples**:

For parent who room shares with grandparents involved:
> "You've worked so hard to build this sleep foundation. Now let's keep it when life happens.

> [Room sharing situation block - already exists]

> And here's the one I know you need: grandparents. They mean well. They love your baby. They also want to rock that baby to sleep and undo everything you've worked for. Here's the script: 'We've worked really hard on teaching [baby] to sleep independently. I know it's hard to hear them fuss, but it's part of their learning. Please don't pick them up or rock them to sleep - they'll settle in a few minutes.' Firm but kind."

**Conditional Sections**:
- IF `living_situation` = room_sharing: Include room sharing block
- IF `living_situation` = apartment: Include apartment block
- IF `living_situation` = sibling_sharing: Include sibling block
- IF `parenting_setup` includes grandparents: Add grandparent section
- IF `work_schedule` = working AND travel likely: Add work travel section

**Variables**:
```
{customer_name}
{method}
{situation_based_content} (existing but needs fix)
{disruption_family_block}
{disruption_work_block}
```

---

### DAY 14: You Did It! What's Next?

**Purpose/Goal**: Celebrate, summarize transformation, ongoing support

**Current State**: Only uses `{customer_name}`

**Quiz Data Points to Use**:
- All 8 - Reference their complete journey
- Baby's age (upcoming developmental stages)
- Biggest sleep struggle (remind them what they solved)
- Work schedule (celebrate getting rest for work)
- Parenting setup (celebrate doing it together/alone)

**Content Blocks Needed**:
- NEW: `celebration_single_parent.md`
- NEW: `celebration_working_parent.md`
- NEW: `celebration_frequent_waker.md`
- NEW: `celebration_early_waker.md`
- NEW: `celebration_nap_disaster.md`
- NEW: `future_toddler.md` (for 13mo+ what's ahead)
- NEW: `future_baby.md` (for 4-12mo what's ahead)

**Personalization Examples**:

For single working parent who was waking every 1-2 hours with 8-month-old:
> "You made it.

> Fourteen days ago, you were waking every 1-2 hours with your 8-month-old, doing it completely alone, and trying to function at work. That's not tired - that's survival mode.

> And now look at you.

> You didn't just teach your baby to sleep. You did it alone, while working, without a partner to tap out to at 3 AM. You should be incredibly proud.

> What you've built will serve your baby through the 12-month regression, the toddler years, and beyond. You've given them a skill for life.

> [Continue with standard closing content]"

**Conditional Sections**:
- IF `parenting_setup` = single: Single-parent celebration
- IF `work_schedule` = working: Working-parent celebration
- IF `biggest_challenge` = specific: Reference what they overcame
- IF `baby_age` >= 13mo: Future toddler challenges
- IF `baby_age` < 13mo: Future baby stages

**Variables**:
```
{customer_name}
{baby_age_short}
{biggest_challenge_text}
{celebration_parenting_block}
{celebration_work_block}
{celebration_challenge_block}
{future_block}
```

---

## 5. NEW CONTENT BLOCKS REQUIRED

### Summary by Category

**Age-Specific Intro Blocks (Day 1)**: 4 blocks
- `intro_age_4_6_months.md`
- `intro_age_7_12_months.md`
- `intro_age_13_18_months.md`
- `intro_age_19_24_months.md`

**Parenting Setup Blocks**: 7 blocks
- `intro_parenting_single.md`
- `intro_parenting_shared.md`
- `intro_parenting_solo_nights.md`
- `method_single_parent.md`
- `method_partner_alignment.md`
- `troubleshoot_single_parent.md`
- `regression_single_parent.md`

**Work Schedule Blocks**: 6 blocks
- `intro_work_stay_home.md`
- `intro_work_working.md`
- `intro_work_shift.md`
- `routine_working_parent.md`
- `naps_working_parent.md`
- `wins_working_parent.md`

**Living Situation/Environment Blocks**: 9 blocks
- `environment_apartment.md`
- `environment_room_sharing.md`
- `environment_house.md`
- `environment_sibling_sharing.md`
- `method_cio_apartment.md`
- `method_cio_room_sharing.md`
- `method_gentle_apartment.md`
- `method_gentle_room_sharing.md`
- `regression_apartment.md`

**Routine/Association Blocks**: 6 blocks
- `routine_feeding_association.md`
- `routine_rocking_association.md`
- `routine_pacifier_association.md`
- `routine_age_baby.md`
- `routine_age_toddler.md`
- `method_age_expectations_baby.md`

**Nap-Specific Blocks**: 4 blocks
- `naps_age_4_6_months.md`
- `naps_age_7_12_months.md`
- `naps_age_13_18_months.md`
- `naps_working_parent.md`

**Regression Blocks**: 3 blocks
- `regression_4_6_months.md`
- `regression_7_12_months.md`
- `regression_13_18_months.md`

**Troubleshooting/Challenge Blocks**: 8 blocks
- `troubleshoot_cio.md`
- `troubleshoot_gentle.md`
- `troubleshoot_apartment.md`
- `troubleshoot_early_morning.md`
- `troubleshoot_frequent_waking.md`
- `wins_frequent_waker.md`
- `wins_early_morning.md`
- `wins_nap_disaster.md`

**Pacifier/Feeding Relevance Blocks**: 6 blocks
- `pacifier_not_relevant.md`
- `pacifier_main_challenge.md`
- `feeding_not_relevant.md`
- `feeding_main_challenge.md`
- `feeding_night_needs_baby.md`
- `feeding_night_needs_older.md`

**Weaning Blocks**: 4 blocks
- `weaning_too_young.md`
- `weaning_ready.md`
- `weaning_frequent_waker.md`
- `weaning_single_parent.md`

**Disruption Blocks**: 3 blocks
- `disruption_grandparents.md`
- `disruption_work_travel.md`
- `disruption_siblings.md`

**Celebration/Future Blocks**: 7 blocks
- `celebration_single_parent.md`
- `celebration_working_parent.md`
- `celebration_frequent_waker.md`
- `celebration_early_waker.md`
- `celebration_nap_disaster.md`
- `future_toddler.md`
- `future_baby.md`

### TOTAL NEW CONTENT BLOCKS: 67

---

## 6. PERSONALIZATION VARIABLE REFERENCE

### Complete Variable List

**Basic Customer Data**:
```python
{customer_name}          # From customer.name
{customer_id}            # From customer.id
{order_id}               # From order
```

**Age Variables**:
```python
{baby_age}               # Full text: "7-12 months"
{baby_age_short}         # Short: "7-12mo" or "8-month-old"
{baby_age_category}      # Category: "baby" (4-12mo) or "toddler" (13mo+)
{age_based_content}      # Existing age block for Day 4
{age_intro_block}        # New Day 1 age intro
{naps_age_block}         # Nap schedule by age
{regression_age_block}   # Upcoming regressions by age
{future_block}           # What's ahead by age
```

**Challenge Variables**:
```python
{biggest_challenge}           # Raw quiz value
{biggest_challenge_text}      # Readable: "waking every 1-2 hours"
{challenge_type}              # Type: "feeding", "motion", "pacifier", "naps", "early_morning"
{challenge_based_content}     # Existing challenge block for Day 8
{wins_challenge_block}        # Wins specific to their challenge
{weaning_challenge_block}     # Weaning emphasis for frequent wakers
{celebration_challenge_block} # Celebration specific to what they overcame
```

**Method Variables**:
```python
{method}                 # Full: "Cry-It-Out" or "Gentle/No-Cry"
{method_short}           # Short: "CIO" or "Gentle"
{method_type}            # Type: "cio" or "gentle"
{method_instructions}    # Existing method block for Day 5
{troubleshoot_method_block} # Method-specific troubleshooting
```

**Living Situation Variables**:
```python
{living_situation}           # Raw: "apartment", "room_sharing", etc.
{living_situation_context}   # Readable context sentence
{environment_block}          # Day 2 environment optimization
{situation_based_content}    # Existing situation block (Day 13 - needs fix)
{method_situation_block}     # Method adjustments for situation
{regression_situation_block} # Regression handling for situation
```

**Parenting Setup Variables**:
```python
{parenting_setup}            # Raw: "single", "two_sharing", etc.
{parenting_setup_context}    # Readable context sentence
{intro_parenting_block}      # Day 1 intro for their setup
{method_parenting_block}     # Method support for their setup
{troubleshoot_parenting_block} # Troubleshooting for their setup
{weaning_parenting_block}    # Weaning support for their setup
{celebration_parenting_block} # Celebration for their setup
```

**Work Schedule Variables**:
```python
{work_schedule}              # Raw: "working", "stay_at_home", etc.
{work_schedule_context}      # Readable context sentence
{intro_work_block}           # Day 1 intro for work situation
{routine_work_block}         # Routine adjustments for work
{naps_work_block}            # Nap management around work
{wins_work_block}            # Work-functioning wins
{celebration_work_block}     # Celebration for working parents
```

**Sleep Association Variables**:
```python
{sleep_association}          # Raw: "nursing_bottle", "rocking", "pacifier", etc.
{sleep_association_type}     # Readable: "nursing to sleep"
{routine_association_block}  # Routine order based on association
{sleep_association_change_text} # What they're changing
{pacifier_relevance_block}   # Day 10 relevance check
{feeding_relevance_block}    # Day 11 relevance check
```

---

## 7. BACKEND REQUIREMENTS

### Immediate Fixes Needed

**1. Fix Day 13 Situation Block** (personalization.py)

The `situation_based_content` variable is never set because `personalization.py` doesn't extract `living_situation` from quiz data.

Add to `get_personalization_data()`:
```python
# Add living situation
living_situation = quiz_data.get('living_situation', '')
situation_type = ''
if 'room' in living_situation.lower():
    situation_type = 'room_sharing'
elif 'apartment' in living_situation.lower():
    situation_type = 'apartment'
elif 'sibling' in living_situation.lower():
    situation_type = 'sibling_sharing'
else:
    situation_type = 'house'

return {
    # ... existing vars ...
    'living_situation': living_situation,
    'situation': situation_type,  # This was missing!
    # ... etc ...
}
```

**2. Add Missing Quiz Data to Personalization** (personalization.py)

Currently missing:
- `parenting_setup`
- `work_schedule`
- `sleep_association`
- `specific_challenge`

Add all of these to `get_personalization_data()` return dict.

**3. Expand get_sequence_content()** (email_service.py)

Current implementation only has conditional blocks for days 4, 5, 8, 13.

Need to expand to all 14 days with multiple block injection points per day.

Suggested structure:
```python
def get_sequence_content(day_number, customer_name, personalization_vars=None, order_id=None):
    # Load base template
    # ...

    # Day-specific personalization
    if day_number == 1:
        # Inject intro_age_block
        # Inject intro_parenting_block
        # Inject intro_work_block
        # Replace {biggest_challenge_text}
        pass
    elif day_number == 2:
        # Inject environment_block based on living_situation
        pass
    # ... etc for all 14 days
```

**4. Add New Placeholder Tags to Templates**

Each email template needs new placeholder tags for the new content blocks:
- `{intro_age_block}`
- `{intro_parenting_block}`
- `{environment_block}`
- `{routine_association_block}`
- etc.

**5. Create Content Block Loader Enhancement**

Current `_get_email_content_block()` only loads one block at a time.

Consider adding a batch loader or caching for performance since we'll be loading 3-5 blocks per email.

---

## 8. IMPLEMENTATION PRIORITY

### Phase 1: Foundation (Fix What's Broken)
1. Fix Day 13 situation variable
2. Add all missing quiz data to personalization.py
3. Create readable text converters for quiz values

### Phase 2: High-Impact Days (Most Transformation)
4. Day 1 - First impression, sets tone
5. Day 5 - The big night, needs confidence
6. Day 14 - Celebration, summarizes journey

### Phase 3: Challenge-Specific Days
7. Day 3 - Routine varies by association
8. Day 10 - Pacifier (make relevant or not)
9. Day 11 - Feeding (make relevant or not)

### Phase 4: Support Days
10. Day 6 - Troubleshooting
11. Day 7 - Finding wins
12. Day 9 - Regressions

### Phase 5: Environment & Context Days
13. Day 2 - Environment
14. Day 4 - Wake windows (already has blocks)
15. Day 8 - Naps (already has blocks)
16. Day 12 - Night weaning
17. Day 13 - Disruptions

---

## 9. HANDOFF NOTES FOR OTHER AGENTS

### For Email Sequence Agent
- Use this blueprint to rewrite all 14 email templates
- Maintain the tone guide exactly
- Each email should have multiple personalization insertion points
- Test with different persona combinations (single working parent in apartment vs two stay-at-home parents in house)

### For Blog & SEO Agent
- Topics from this sequence for blog content:
  - "Wake Windows by Age: The Complete Guide"
  - "Sleep Training in an Apartment: A Parent's Guide"
  - "Sleep Training as a Single Parent"
  - "When Night Feeds are Habit vs. Need"
  - "The Working Parent's Guide to Nap Training"

### For UX/UI Design Agent
- Email templates need styled boxes for each content block type
- Consider visual differentiation for:
  - Age-based content (developmental info)
  - Method instructions (action items)
  - Challenge-specific content (personal relevance)
  - Situation-based content (logistics)

### For Content Repurposer Agent
- Key hooks from this sequence:
  - "I see you." (Day 1 opening)
  - "The first night is the hardest for YOU, not your baby."
  - "Consistency is more important than perfection."
  - "Rough nights don't erase progress."
  - "You're not abandoning them. You're teaching them."

---

## 10. SUCCESS METRICS

After implementation, measure:

1. **Reply rate by day** - More personalized = more replies
2. **Email open rate progression** - Do they stay engaged all 14 days?
3. **Support ticket themes** - Do tickets mention feeling understood?
4. **Post-course feedback** - "Did the course feel personalized to you?"
5. **Completion rate** - Do more people finish all 14 days?

Target: Every customer should feel like the emails were written specifically for their situation, not like they're receiving generic content with their name inserted.

---

*Blueprint Version 1.0 - Created for Napocalypse Email Sequence Overhaul*
*To be used by Email Sequence Agent for template rewrites*

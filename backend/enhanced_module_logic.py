# Enhanced Module Selection Logic

def select_modules_enhanced(quiz_data):
    """Enhanced module selection with better coverage"""
    modules = []
    
    # 1. Age-based (ALWAYS - 1 module)
    age_map = {
        '0-3 months': 'module_1_newborn',
        '4-6 months': 'module_2_readiness', 
        '7-12 months': 'module_3_established',
        '13-18 months': 'module_4_toddler',
        '19-24 months': 'module_4_toddler'
    }
    baby_age = quiz_data.get('baby_age', '')
    modules.append(age_map.get(baby_age, 'module_2_readiness'))
    
    # 2. Method-based (ALWAYS - 1 module)
    sleep_philosophy = quiz_data.get('sleep_philosophy', '').lower()
    if 'comfortable' in sleep_philosophy or 'crying' in sleep_philosophy:
        modules.append('module_5_cio')
    else:
        modules.append('module_6_gentle')
    
    # 3. Challenge-based (PRIORITY - 1-2 modules)
    biggest_challenge = quiz_data.get('biggest_challenge', '').lower()
    sleep_associations = quiz_data.get('sleep_associations', '').lower()
    
    # Sleep association priority
    if 'nursing' in sleep_associations or 'bottle' in sleep_associations:
        modules.append('module_7_feeding')
    elif 'rocking' in sleep_associations or 'bouncing' in sleep_associations:
        modules.append('module_9_motion')  # NEW
    elif 'pacifier' in sleep_associations:
        modules.append('module_12_pacifier')  # NEW
    
    # Specific challenge modules
    if 'naps_impossible' in biggest_challenge:
        modules.append('module_10_naps')  # NEW
    elif 'wakes_too_early' in biggest_challenge:
        modules.append('module_11_early_wake')  # NEW
    elif 'bedtime_takes_over_hour' in biggest_challenge:
        # Could use existing gentle/CIO modules with bedtime focus
        pass
    
    # 4. Living situation (CONDITIONAL - 1 module)
    living_situation = quiz_data.get('living_situation', '').lower()
    if any(x in living_situation for x in ['apartment', 'room_sharing', 'shared', 'siblings']):
        modules.append('module_8_room_sharing')
    
    # Remove duplicates while preserving order
    modules = list(dict.fromkeys(modules))
    return modules
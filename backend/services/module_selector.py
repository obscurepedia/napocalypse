"""
Module Selection Logic
Based on quiz responses, determine which modules to include in the personalized guide
"""

def select_modules(quiz_data):
    """
    Select 3-5 modules based on quiz responses
    
    Args:
        quiz_data (dict): Quiz response data
        
    Returns:
        list: List of module names to include
    """
    modules = []
    
    # 1. Age-based module (ALWAYS INCLUDED - 1 module)
    age_map = {
        '0-3 months': 'module_1_newborn',
        '4-6 months': 'module_2_readiness',
        '7-12 months': 'module_3_established',
        '13-18 months': 'module_4_toddler',
        '19-24 months': 'module_4_toddler'
    }
    
    baby_age = quiz_data.get('baby_age', '')
    if baby_age in age_map:
        modules.append(age_map[baby_age])
    else:
        # Default to readiness if age not found
        modules.append('module_2_readiness')
    
    # 2. Method-based module (ALWAYS INCLUDED - 1 module)
    sleep_philosophy = quiz_data.get('sleep_philosophy', '')
    
    if 'comfortable' in sleep_philosophy.lower() or 'crying' in sleep_philosophy.lower():
        modules.append('module_5_cio')
    elif 'gentle' in sleep_philosophy.lower() or 'no-cry' in sleep_philosophy.lower():
        modules.append('module_6_gentle')
    elif 'gradual' in sleep_philosophy.lower():
        modules.append('module_6_gentle')
    else:
        # Default to gentle if not sure
        modules.append('module_6_gentle')
    
    # 3. Sleep Association module (CONDITIONAL - 1 module)
    sleep_associations = quiz_data.get('sleep_associations', '').lower()
    
    # Priority order: feeding > motion/rocking > pacifier
    if 'nursing' in sleep_associations or 'bottle' in sleep_associations:
        modules.append('module_7_feeding')
    elif 'rocking' in sleep_associations or 'bouncing' in sleep_associations or 'motion' in sleep_associations:
        modules.append('module_9_motion_rocking')
    elif 'pacifier' in sleep_associations:
        modules.append('module_12_pacifier')
    
    # 4. Challenge-based module (CONDITIONAL - 1 module)
    biggest_challenge = quiz_data.get('biggest_challenge', '').lower()
    specific_challenge = quiz_data.get('specific_challenge', '').lower()
    
    # Check for specific challenges
    if 'nap' in biggest_challenge or 'nap' in specific_challenge:
        if 'module_10_nap_training' not in modules:
            modules.append('module_10_nap_training')
    elif 'early morning' in biggest_challenge or 'early' in specific_challenge or 'wakes before 6' in specific_challenge:
        if 'module_11_early_morning' not in modules:
            modules.append('module_11_early_morning')
    
    # 5. Situation-based module (CONDITIONAL - 1 module)
    living_situation = quiz_data.get('living_situation', '').lower()
    
    if ('apartment' in living_situation or 
        'room sharing' in living_situation or 
        'shared' in living_situation or
        'siblings' in living_situation):
        modules.append('module_8_room_sharing')
    
    # Remove duplicates while preserving order
    modules = list(dict.fromkeys(modules))
    
    return modules

def get_module_info(module_name):
    """
    Get human-readable information about a module
    
    Args:
        module_name (str): Module identifier
        
    Returns:
        dict: Module information
    """
    module_info = {
        'module_1_newborn': {
            'title': 'Newborn Sleep Foundations (0-3 Months)',
            'description': 'Understanding newborn sleep and building healthy foundations'
        },
        'module_2_readiness': {
            'title': 'Sleep Training Readiness (4-6 Months)',
            'description': 'Preparing for sleep training at the ideal age'
        },
        'module_3_established': {
            'title': 'Established Sleeper (7-12 Months)',
            'description': 'Fixing sleep issues for older babies'
        },
        'module_4_toddler': {
            'title': 'Toddler Sleep Transitions (13-24 Months)',
            'description': 'Handling toddler sleep challenges and boundaries'
        },
        'module_5_cio': {
            'title': 'Cry-It-Out Implementation Guide',
            'description': 'Fast, effective sleep training method'
        },
        'module_6_gentle': {
            'title': 'Gentle/No-Cry Methods',
            'description': 'Gradual, gentle approach to sleep training'
        },
        'module_7_feeding': {
            'title': 'Breaking the Feed-to-Sleep Association',
            'description': 'Separating feeding from sleeping'
        },
        'module_8_room_sharing': {
            'title': 'Room Sharing Strategies',
            'description': 'Sleep training while sharing a room'
        },
        'module_9_motion_rocking': {
            'title': 'Breaking Motion/Rocking Dependency',
            'description': 'Weaning from rocking, bouncing, and motion sleep'
        },
        'module_10_nap_training': {
            'title': 'Nap Training Mastery',
            'description': 'Fixing short naps and establishing great daytime sleep'
        },
        'module_11_early_morning': {
            'title': 'Early Morning Wake Solutions',
            'description': 'Solving 4-6am wake-ups and extending sleep'
        },
        'module_12_pacifier': {
            'title': 'Pacifier Weaning Guide',
            'description': 'Breaking pacifier dependency for better sleep'
        }
    }
    
    return module_info.get(module_name, {
        'title': module_name,
        'description': 'Sleep training module'
    })
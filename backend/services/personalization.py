"""
Email Personalization Service
Detects customer's method, challenge, and generates personalization variables
"""

def get_personalization_data(customer, quiz_data, modules):
    """
    Generate personalization variables for email templates
    
    Args:
        customer: Customer object
        quiz_data: Quiz response data
        modules: List of module names assigned to customer
        
    Returns:
        dict: Personalization variables
    """
    from .module_selector import get_module_info
    
    # Detect method
    method_info = detect_method(modules)
    
    # Detect primary challenge
    challenge_info = detect_challenge(modules, quiz_data)
    
    # Get module details
    module_details = [get_module_info(m) for m in modules]
    
    return {
        'customer_name': customer.name or 'there',
        'customer_id': customer.id,
        'baby_age': quiz_data.get('baby_age', ''),
        'baby_age_short': get_age_short(quiz_data.get('baby_age', '')),
        'method': method_info['method'],
        'method_short': method_info['method_short'],
        'method_type': method_info['method_type'],
        'challenge': challenge_info['challenge'],
        'challenge_type': challenge_info['challenge_type'],
        'challenge_short': challenge_info['challenge_short'],
        'modules': modules,
        'module_titles': [m['title'] for m in module_details],
        'module_list': ', '.join([m['title'] for m in module_details])
    }

def detect_method(modules):
    """
    Detect which method customer is using based on modules
    
    Returns:
        dict: Method information
    """
    if 'module_5_cio' in modules:
        return {
            'method': 'Cry-It-Out',
            'method_short': 'CIO',
            'method_type': 'cio'
        }
    elif 'module_6_gentle' in modules:
        return {
            'method': 'Gentle/No-Cry',
            'method_short': 'Gentle',
            'method_type': 'gentle'
        }
    else:
        # Default to gentle if not specified
        return {
            'method': 'Gentle/No-Cry',
            'method_short': 'Gentle',
            'method_type': 'gentle'
        }

def detect_challenge(modules, quiz_data):
    """
    Detect primary challenge based on modules and quiz data
    
    Returns:
        dict: Challenge information
    """
    # Check modules first
    if 'module_7_feeding' in modules:
        return {
            'challenge': 'feeding to sleep',
            'challenge_type': 'feeding',
            'challenge_short': 'Feeding'
        }
    elif 'module_9_motion_rocking' in modules:
        return {
            'challenge': 'motion/rocking dependency',
            'challenge_type': 'motion',
            'challenge_short': 'Motion/Rocking'
        }
    elif 'module_12_pacifier' in modules:
        return {
            'challenge': 'pacifier dependency',
            'challenge_type': 'pacifier',
            'challenge_short': 'Pacifier'
        }
    elif 'module_10_nap_training' in modules:
        return {
            'challenge': 'nap training',
            'challenge_type': 'naps',
            'challenge_short': 'Naps'
        }
    elif 'module_11_early_morning' in modules:
        return {
            'challenge': 'early morning wakes',
            'challenge_type': 'early_morning',
            'challenge_short': 'Early Morning'
        }
    else:
        # Fallback to quiz data
        biggest_challenge = quiz_data.get('biggest_challenge', '').lower()
        
        if 'nap' in biggest_challenge:
            return {
                'challenge': 'nap training',
                'challenge_type': 'naps',
                'challenge_short': 'Naps'
            }
        elif 'early' in biggest_challenge or 'morning' in biggest_challenge:
            return {
                'challenge': 'early morning wakes',
                'challenge_type': 'early_morning',
                'challenge_short': 'Early Morning'
            }
        else:
            # Generic fallback
            return {
                'challenge': 'sleep challenges',
                'challenge_type': 'general',
                'challenge_short': 'Sleep'
            }

def get_age_short(baby_age):
    """
    Convert full age string to short version
    
    Args:
        baby_age: Full age string (e.g., "4-6 months")
        
    Returns:
        str: Short version (e.g., "4-6mo")
    """
    return baby_age.replace(' months', 'mo').replace(' month', 'mo')

def get_email_variant(day_number, method_type, challenge_type):
    """
    Determine which email template variant to use
    
    Args:
        day_number: Day in sequence (1-7)
        method_type: 'cio' or 'gentle'
        challenge_type: 'feeding', 'motion', 'pacifier', 'naps', 'early_morning', 'general'
        
    Returns:
        str: Template filename
    """
    # Days 1, 2, 5, 6 are generic
    if day_number in [1, 2, 5, 6]:
        return f'day_{day_number}_generic.html'
    
    # Day 3: Method-specific
    if day_number == 3:
        return f'day_3_{method_type}.html'
    
    # Day 4: Method + Challenge specific
    if day_number == 4:
        return f'day_4_{method_type}_{challenge_type}.html'
    
    # Day 7: Method-specific
    if day_number == 7:
        return f'day_7_{method_type}.html'
    
    # Fallback
    return f'day_{day_number}_generic.html'

def get_success_story_name(method_type, challenge_type):
    """
    Get the name for success story based on method and challenge
    
    Returns:
        str: Parent name for success story
    """
    stories = {
        'cio_feeding': 'Sarah',
        'cio_motion': 'Mike',
        'cio_pacifier': 'Emma',
        'cio_naps': 'Lisa',
        'cio_early_morning': 'Tom',
        'gentle_feeding': 'Rachel',
        'gentle_motion': 'David',
        'gentle_pacifier': 'Amy',
        'gentle_naps': 'Chris',
        'gentle_early_morning': 'Jessica'
    }
    
    key = f'{method_type}_{challenge_type}'
    return stories.get(key, 'Sarah')

def get_upsell_url(customer_id, modules):
    """
    Generate personalized upsell URL
    
    Args:
        customer_id: Customer ID
        modules: List of module names
        
    Returns:
        str: Upsell URL
    """
    module_ids = ','.join(modules)
    return f"https://napocalypse.com/upsell?customer={customer_id}&modules={module_ids}"
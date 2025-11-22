"""
Email Personalization Service
Extracts all 8 quiz data points and generates personalization variables
for the full 14-day email sequence with 67+ content blocks.
"""

def get_personalization_data(customer, quiz_data, modules):
    """
    Generate comprehensive personalization variables for email templates.

    Extracts all 8 quiz data points:
    - baby_age
    - biggest_challenge
    - method_preference / sleep_philosophy
    - living_situation
    - parenting_setup
    - work_schedule
    - specific_challenge
    - sleep_association

    Args:
        customer: Customer object
        quiz_data: Quiz response data
        modules: List of module names assigned to customer

    Returns:
        dict: Complete personalization variables for all 14 days
    """
    from .module_selector import get_module_info

    # Detect method from modules or quiz data
    method_info = detect_method(modules, quiz_data)

    # Detect primary challenge from modules and quiz
    challenge_info = detect_challenge(modules, quiz_data)

    # Extract all quiz data points
    baby_age = quiz_data.get('baby_age', '')
    baby_age_short = get_age_short(baby_age)
    baby_age_category = get_age_category(baby_age)

    # Extract parenting setup
    parenting_setup_raw = quiz_data.get('parenting_setup', '')
    parenting_setup = normalize_parenting_setup(parenting_setup_raw)
    parenting_setup_context = get_parenting_context(parenting_setup)

    # Extract work schedule
    work_schedule_raw = quiz_data.get('work_schedule', '')
    work_schedule = normalize_work_schedule(work_schedule_raw)
    work_schedule_context = get_work_context(work_schedule)

    # Extract living situation
    living_situation_raw = quiz_data.get('living_situation', '')
    living_situation = normalize_living_situation(living_situation_raw)
    situation_type = get_situation_type(living_situation)
    living_situation_context = get_living_situation_context(living_situation)

    # Extract sleep association (database field is 'sleep_associations' with 's')
    sleep_association_raw = quiz_data.get('sleep_associations', quiz_data.get('sleep_association', ''))
    sleep_association = normalize_sleep_association(sleep_association_raw)
    sleep_association_type = get_sleep_association_type(sleep_association)
    sleep_association_text = get_sleep_association_text(sleep_association)

    # Extract specific challenge
    specific_challenge_raw = quiz_data.get('specific_challenge', '')
    specific_challenge = normalize_specific_challenge(specific_challenge_raw)

    # Extract biggest struggle
    biggest_struggle_raw = quiz_data.get('biggest_challenge', '')
    biggest_struggle = normalize_biggest_struggle(biggest_struggle_raw)
    biggest_challenge_text = get_biggest_challenge_text(biggest_struggle)

    # Get module details
    module_details = [get_module_info(m) for m in modules]

    return {
        # Basic customer data
        'customer_name': customer.name or 'there',
        'customer_id': customer.id,

        # Age variables
        'baby_age': baby_age,
        'baby_age_short': baby_age_short,
        'baby_age_category': baby_age_category,  # 'baby' or 'toddler'

        # Method variables
        'method': method_info['method'],
        'method_short': method_info['method_short'],
        'method_type': method_info['method_type'],

        # Challenge variables
        'challenge': challenge_info['challenge'],
        'challenge_type': challenge_info['challenge_type'],
        'challenge_short': challenge_info['challenge_short'],

        # Parenting setup variables
        'parenting_setup': parenting_setup,
        'parenting_setup_context': parenting_setup_context,

        # Work schedule variables
        'work_schedule': work_schedule,
        'work_schedule_context': work_schedule_context,

        # Living situation variables
        'living_situation': living_situation,
        'situation': situation_type,  # This was missing - fixes Day 13!
        'living_situation_context': living_situation_context,

        # Sleep association variables
        'sleep_association': sleep_association,
        'sleep_association_type': sleep_association_type,
        'sleep_association_text': sleep_association_text,

        # Specific challenge
        'specific_challenge': specific_challenge,

        # Biggest struggle
        'biggest_struggle': biggest_struggle,
        'biggest_challenge_text': biggest_challenge_text,

        # Module info
        'modules': modules,
        'module_titles': [m['title'] for m in module_details],
        'module_list': ', '.join([m['title'] for m in module_details])
    }


def detect_method(modules, quiz_data=None):
    """
    Detect which method customer is using based on modules or quiz data.

    Args:
        modules: List of module names
        quiz_data: Quiz response data (optional, used as fallback)

    Returns:
        dict: Method information with method, method_short, method_type
    """
    # First check modules
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

    # Fallback to quiz data sleep_philosophy
    if quiz_data:
        philosophy = quiz_data.get('sleep_philosophy', '').lower()
        if 'cio' in philosophy or 'cry' in philosophy or 'extinction' in philosophy:
            return {
                'method': 'Cry-It-Out',
                'method_short': 'CIO',
                'method_type': 'cio'
            }
        elif 'gentle' in philosophy or 'no cry' in philosophy or 'gradual' in philosophy:
            return {
                'method': 'Gentle/No-Cry',
                'method_short': 'Gentle',
                'method_type': 'gentle'
            }
        elif 'not sure' in philosophy or 'unsure' in philosophy or 'help me' in philosophy:
            return {
                'method': 'Gentle (Recommended Start)',
                'method_short': 'Gentle',
                'method_type': 'not_sure'
            }

    # Default to gentle if not specified
    return {
        'method': 'Gentle/No-Cry',
        'method_short': 'Gentle',
        'method_type': 'gentle'
    }


def detect_challenge(modules, quiz_data):
    """
    Detect primary challenge based on modules and quiz data.

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
        elif 'frequent' in biggest_challenge or '1-2' in biggest_challenge or 'every' in biggest_challenge:
            return {
                'challenge': 'frequent night wakings',
                'challenge_type': 'frequent_waking',
                'challenge_short': 'Frequent Waking'
            }
        elif 'bedtime' in biggest_challenge or 'long' in biggest_challenge or 'hour' in biggest_challenge:
            return {
                'challenge': 'bedtime battles',
                'challenge_type': 'bedtime_battle',
                'challenge_short': 'Bedtime'
            }
        else:
            # Generic fallback
            return {
                'challenge': 'sleep challenges',
                'challenge_type': 'general',
                'challenge_short': 'Sleep'
            }


def get_age_short(baby_age):
    """Convert full age string to short version."""
    if not baby_age:
        return 'your baby'

    # Handle various formats
    age_lower = baby_age.lower()

    if '0-3' in age_lower or '0 to 3' in age_lower:
        return '0-3 month old'
    elif '4-6' in age_lower or '4 to 6' in age_lower:
        return '4-6 month old'
    elif '7-12' in age_lower or '7 to 12' in age_lower:
        return '7-12 month old'
    elif '13-18' in age_lower or '13 to 18' in age_lower:
        return '13-18 month old'
    elif '19-24' in age_lower or '19 to 24' in age_lower:
        return '19-24 month old'
    elif '2' in age_lower and ('year' in age_lower or 'plus' in age_lower):
        return '2+ year old'
    else:
        return baby_age.replace(' months', ' month old').replace(' month', ' month old')


def get_age_category(baby_age):
    """
    Determine if baby is in 'baby' or 'toddler' category.

    Returns:
        str: 'baby' for 4-12 months, 'toddler' for 13+ months
    """
    if not baby_age:
        return 'baby'

    age_lower = baby_age.lower()

    if '13' in age_lower or '14' in age_lower or '15' in age_lower or \
       '16' in age_lower or '17' in age_lower or '18' in age_lower or \
       '19' in age_lower or '20' in age_lower or '21' in age_lower or \
       '22' in age_lower or '23' in age_lower or '24' in age_lower or \
       'toddler' in age_lower or '2 year' in age_lower or '2+' in age_lower:
        return 'toddler'
    else:
        return 'baby'


def normalize_parenting_setup(raw_value):
    """
    Normalize parenting setup to standard values.

    Returns:
        str: 'single', 'two_sharing', 'solo_nights', 'grandparents'
    """
    if not raw_value:
        return 'two_sharing'

    val = raw_value.lower()

    if 'single' in val or 'alone' in val or 'solo' in val:
        return 'single'
    elif 'one' in val and ('night' in val or 'does' in val):
        return 'solo_nights'
    elif 'grand' in val:
        return 'grandparents'
    else:
        return 'two_sharing'


def get_parenting_context(parenting_setup):
    """Get human-readable context for parenting setup."""
    contexts = {
        'single': "doing this solo",
        'two_sharing': "doing this together",
        'solo_nights': "handling nights on your own",
        'grandparents': "with grandparents involved"
    }
    return contexts.get(parenting_setup, '')


def normalize_work_schedule(raw_value):
    """
    Normalize work schedule to standard values.

    Returns:
        str: 'stay_home', 'working', 'shift_work', 'wfh'
    """
    if not raw_value:
        return 'working'

    val = raw_value.lower()

    # Check shift work first (highest priority)
    if 'shift' in val:
        return 'shift_work'
    # Check work from home
    elif 'wfh' in val or ('work' in val and 'home' in val):
        return 'wfh'
    # Check stay at home (using parentheses for correct precedence)
    elif 'stay' in val or ('home' in val and 'work' not in val):
        return 'stay_home'
    else:
        return 'working'


def get_work_context(work_schedule):
    """Get human-readable context for work schedule."""
    contexts = {
        'stay_home': "you're home during the day",
        'working': "you need to function at work",
        'shift_work': "your schedule varies",
        'wfh': "you work from home"
    }
    return contexts.get(work_schedule, '')


def normalize_living_situation(raw_value):
    """
    Normalize living situation to standard values.

    Returns:
        str: 'house', 'apartment', 'room_sharing', 'sibling_sharing'
    """
    if not raw_value:
        return 'house'

    val = raw_value.lower()

    if 'room' in val and ('share' in val or 'sharing' in val):
        return 'room_sharing'
    elif 'sibling' in val or ('share' in val and 'room' in val):
        return 'sibling_sharing'
    elif 'apartment' in val or 'condo' in val or 'flat' in val:
        return 'apartment'
    else:
        return 'house'


def get_situation_type(living_situation):
    """
    Get situation type for content block selection.
    This is the key fix for Day 13!
    """
    return living_situation


def get_living_situation_context(living_situation):
    """Get human-readable context for living situation."""
    contexts = {
        'house': "you have a dedicated nursery",
        'apartment': "you're in an apartment",
        'room_sharing': "you're room sharing with your baby",
        'sibling_sharing': "siblings are sharing a room"
    }
    return contexts.get(living_situation, '')


def normalize_sleep_association(raw_value):
    """
    Normalize sleep association to standard values.

    Returns:
        str: 'nursing', 'rocking', 'pacifier', 'cosleeping', 'multiple', 'none'
    """
    if not raw_value:
        return 'none'

    val = raw_value.lower()

    if 'nurs' in val or 'bottle' in val or 'feed' in val:
        return 'nursing'
    elif 'rock' in val or 'bounc' in val or 'motion' in val:
        return 'rocking'
    elif 'pacifier' in val or 'binky' in val or 'dummy' in val:
        return 'pacifier'
    elif 'cosleep' in val or 'co-sleep' in val or 'bed' in val:
        return 'cosleeping'
    elif 'multiple' in val or 'several' in val or ',' in val:
        return 'multiple'
    else:
        return 'none'


def get_sleep_association_type(sleep_association):
    """Get readable type name for sleep association."""
    types = {
        'nursing': 'nursing/bottle',
        'rocking': 'rocking/bouncing',
        'pacifier': 'pacifier',
        'cosleeping': 'co-sleeping',
        'multiple': 'multiple associations',
        'none': 'none'
    }
    return types.get(sleep_association, 'none')


def get_sleep_association_text(sleep_association):
    """Get action text for sleep association (for Day 5 context)."""
    texts = {
        'nursing': 'needs nursing or a bottle to fall asleep',
        'rocking': 'needs to be rocked or bounced to fall asleep',
        'pacifier': 'needs a pacifier to fall asleep',
        'cosleeping': 'needs to sleep right next to you',
        'multiple': 'relies on multiple sleep crutches',
        'none': ''
    }
    return texts.get(sleep_association, '')


def normalize_specific_challenge(raw_value):
    """
    Normalize specific challenge to standard values.

    Returns:
        str: 'feeding', 'rocking', 'put_down', 'long_bedtime', 'naps', 'early_waking', 'pacifier'
    """
    if not raw_value:
        return ''

    val = raw_value.lower()

    if 'feed' in val or 'nurs' in val or 'bottle' in val:
        return 'feeding'
    elif 'rock' in val or 'motion' in val or 'bounc' in val or 'hold' in val:
        return 'rocking'
    elif 'put' in val and 'down' in val:
        return 'put_down'
    elif 'pacifier' in val or 'paci' in val or 'dummy' in val:
        return 'pacifier'
    elif 'bedtime' in val or 'hour' in val or 'long' in val:
        return 'long_bedtime'
    elif 'nap' in val:
        return 'naps'
    elif 'early' in val or 'morning' in val:
        return 'early_waking'
    else:
        return ''


def normalize_biggest_struggle(raw_value):
    """
    Normalize biggest struggle to standard values.

    Returns:
        str: 'frequent_waking', 'bedtime_battles', 'early_morning', 'naps'
    """
    if not raw_value:
        return 'frequent_waking'

    val = raw_value.lower()

    if '1-2' in val or 'every' in val or 'frequent' in val or 'multiple' in val:
        return 'frequent_waking'
    elif 'early' in val or 'morning' in val:
        return 'early_morning'
    elif 'nap' in val:
        return 'naps'
    elif 'bedtime' in val or 'long' in val or 'hour' in val or 'battle' in val:
        return 'bedtime_battles'
    elif '3-5' in val or 'several' in val:
        return 'frequent_waking'
    else:
        return 'frequent_waking'


def get_biggest_challenge_text(biggest_struggle):
    """Get human-readable text for biggest struggle."""
    texts = {
        'frequent_waking': 'waking every 1-2 hours',
        'bedtime_battles': 'bedtime taking forever',
        'early_morning': 'those brutal early morning wake-ups',
        'naps': 'naps being a disaster'
    }
    return texts.get(biggest_struggle, 'struggling with sleep')


def get_email_variant(day_number, method_type, challenge_type):
    """
    Determine which email template variant to use.
    Note: This is legacy code - new system uses new_day_X.html templates.

    Args:
        day_number: Day in sequence (1-14)
        method_type: 'cio' or 'gentle'
        challenge_type: Challenge type string

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
    Get the name for success story based on method and challenge.

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

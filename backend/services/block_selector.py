"""
Block Selector Service

This service determines which content blocks to include in a personalized guide
based on the customer's quiz responses.

Logic:
- 1 age-based block (always included)
- 1 method block (CIO or Gentle)
- 1-2 challenge blocks (based on specific challenges)
- 0-1 situation blocks (if applicable)

Total: 3-5 blocks per customer = 10-15 pages
"""

from typing import List, Dict, Any


class BlockSelector:
    """Selects appropriate content blocks based on quiz responses."""
    
    # Block definitions
    AGE_BLOCKS = {
        '0-3': 'age_0_3_months',
        '4-6': 'age_4_6_months', 
        '7-12': 'age_7_12_months',
        '13-18': 'age_13_18_months',
        '19-24': 'age_19_24_months'
    }
    
    METHOD_BLOCKS = {
        'cio': ['method_cio_overview', 'method_cio_implementation'],
        'gentle': ['method_gentle_overview', 'method_gentle_implementation']
    }
    
    CHALLENGE_BLOCKS = {
        'feeding': 'challenge_feeding_to_sleep',
        'motion': 'challenge_motion_dependency',
        'pacifier': 'challenge_pacifier_dependency',
        'naps': 'challenge_nap_training',
        'early_morning': 'challenge_early_morning_waking'
    }
    
    SITUATION_BLOCKS = {
        'room_sharing': 'situation_room_sharing',
        'apartment': 'situation_apartment_living'
    }
    
    def __init__(self):
        """Initialize the block selector."""
        pass
    
    def select_blocks(self, quiz_responses: Dict[str, Any]) -> List[str]:
        """
        Select content blocks based on quiz responses.
        
        Args:
            quiz_responses: Dictionary containing quiz answers
            
        Returns:
            List of block identifiers to include in the guide
            
        Example quiz_responses:
        {
            'baby_age': '7-12',
            'sleep_method': 'cio',
            'main_challenge': 'feeding',
            'secondary_challenge': 'naps',
            'living_situation': 'apartment',
            'room_sharing': True
        }
        """
        selected_blocks = []
        
        # 1. Age-based block (always included)
        age_block = self._select_age_block(quiz_responses)
        if age_block:
            selected_blocks.append(age_block)
        
        # 2. Method blocks (always included - 2 blocks)
        method_blocks = self._select_method_blocks(quiz_responses)
        selected_blocks.extend(method_blocks)
        
        # 3. Challenge blocks (1-2 blocks)
        challenge_blocks = self._select_challenge_blocks(quiz_responses)
        selected_blocks.extend(challenge_blocks)
        
        # 4. Situation blocks (0-1 blocks)
        situation_blocks = self._select_situation_blocks(quiz_responses)
        selected_blocks.extend(situation_blocks)
        
        return selected_blocks
    
    def _select_age_block(self, quiz_responses: Dict[str, Any]) -> str:
        """Select the appropriate age-based block."""
        baby_age = quiz_responses.get('baby_age', '7-12')
        return self.AGE_BLOCKS.get(baby_age, 'age_7_12_months')
    
    def _select_method_blocks(self, quiz_responses: Dict[str, Any]) -> List[str]:
        """Select the appropriate method blocks (overview + implementation)."""
        sleep_method = quiz_responses.get('sleep_method', 'cio')
        
        # Map quiz responses to method type
        method_mapping = {
            'cry_it_out': 'cio',
            'cio': 'cio',
            'ferber': 'cio',
            'gentle': 'gentle',
            'chair': 'gentle',
            'gradual': 'gentle',
            'no_cry': 'gentle'
        }
        
        method_type = method_mapping.get(sleep_method.lower(), 'cio')
        return self.METHOD_BLOCKS[method_type]
    
    def _select_challenge_blocks(self, quiz_responses: Dict[str, Any]) -> List[str]:
        """Select 1-2 challenge blocks based on main and secondary challenges."""
        challenge_blocks = []
        
        # Main challenge (always included if specified)
        main_challenge = quiz_responses.get('main_challenge', '')
        if main_challenge:
            main_block = self._map_challenge_to_block(main_challenge)
            if main_block:
                challenge_blocks.append(main_block)
        
        # Secondary challenge (included if different from main)
        secondary_challenge = quiz_responses.get('secondary_challenge', '')
        if secondary_challenge and secondary_challenge != main_challenge:
            secondary_block = self._map_challenge_to_block(secondary_challenge)
            if secondary_block and secondary_block not in challenge_blocks:
                challenge_blocks.append(secondary_block)
        
        # If no challenges specified, default to nap training
        if not challenge_blocks:
            challenge_blocks.append(self.CHALLENGE_BLOCKS['naps'])
        
        return challenge_blocks
    
    def _map_challenge_to_block(self, challenge: str) -> str:
        """Map quiz challenge response to block identifier."""
        challenge_mapping = {
            # Direct mappings from V2 mapping
            'feeding_to_sleep': 'feeding',
            'rocking': 'motion',
            'pacifier': 'pacifier', 
            'naps': 'naps',
            'early_morning': 'early_morning',
            
            # Legacy mappings (keep for compatibility)
            'feed_to_sleep': 'feeding',
            'nursing_to_sleep': 'feeding',
            'bottle_to_sleep': 'feeding',
            'bouncing': 'motion',
            'motion': 'motion',
            'stroller': 'motion',
            'car': 'motion',
            'paci': 'pacifier',
            'binky': 'pacifier',
            'short_naps': 'naps',
            'nap_training': 'naps',
            'early_waking': 'early_morning',
            'waking_early': 'early_morning',
            
            # Additional common challenges
            'bedtime_routine': 'naps',  # Map bedtime issues to naps block for now
            'night_wakings': 'naps',    # Map night wakings to naps block for now
        }
        
        challenge_key = challenge_mapping.get(challenge.lower(), challenge.lower())
        return self.CHALLENGE_BLOCKS.get(challenge_key)
    
    def _select_situation_blocks(self, quiz_responses: Dict[str, Any]) -> List[str]:
        """Select 0-1 situation blocks based on living situation."""
        situation_blocks = []
        
        # Check for room sharing
        room_sharing = quiz_responses.get('room_sharing', False)
        if room_sharing or quiz_responses.get('living_situation') == 'room_sharing':
            situation_blocks.append(self.SITUATION_BLOCKS['room_sharing'])
        
        # Check for apartment living
        living_situation = quiz_responses.get('living_situation', '')
        if 'apartment' in living_situation.lower() or quiz_responses.get('apartment_living', False):
            # Only add if not already including room sharing (avoid too many blocks)
            if not situation_blocks:
                situation_blocks.append(self.SITUATION_BLOCKS['apartment'])
        
        return situation_blocks
    
    def get_block_count(self, quiz_responses: Dict[str, Any]) -> int:
        """Get the total number of blocks that will be included."""
        blocks = self.select_blocks(quiz_responses)
        return len(blocks)
    
    def get_estimated_pages(self, quiz_responses: Dict[str, Any]) -> int:
        """
        Estimate the number of pages in the final guide.
        
        Each block is approximately 2-3 pages when formatted.
        """
        block_count = self.get_block_count(quiz_responses)
        # Each block averages 2.5 pages
        return int(block_count * 2.5)


# Example usage and testing
if __name__ == "__main__":
    selector = BlockSelector()
    
    # Test case 1: CIO with feeding challenge, apartment living
    test_quiz_1 = {
        'baby_age': '7-12',
        'sleep_method': 'cio',
        'main_challenge': 'feeding_to_sleep',
        'secondary_challenge': 'naps',
        'living_situation': 'apartment',
        'room_sharing': False
    }
    
    blocks_1 = selector.select_blocks(test_quiz_1)
    print("Test Case 1 - CIO, Feeding, Apartment:")
    print(f"Blocks: {blocks_1}")
    print(f"Count: {len(blocks_1)} blocks")
    print(f"Estimated pages: {selector.get_estimated_pages(test_quiz_1)}")
    print()
    
    # Test case 2: Gentle with motion dependency, room sharing
    test_quiz_2 = {
        'baby_age': '4-6',
        'sleep_method': 'gentle',
        'main_challenge': 'rocking',
        'secondary_challenge': 'pacifier',
        'living_situation': 'house',
        'room_sharing': True
    }
    
    blocks_2 = selector.select_blocks(test_quiz_2)
    print("Test Case 2 - Gentle, Motion, Room Sharing:")
    print(f"Blocks: {blocks_2}")
    print(f"Count: {len(blocks_2)} blocks")
    print(f"Estimated pages: {selector.get_estimated_pages(test_quiz_2)}")
    print()
    
    # Test case 3: Toddler with early morning waking
    test_quiz_3 = {
        'baby_age': '19-24',
        'sleep_method': 'cio',
        'main_challenge': 'early_waking',
        'secondary_challenge': '',
        'living_situation': 'house',
        'room_sharing': False
    }
    
    blocks_3 = selector.select_blocks(test_quiz_3)
    print("Test Case 3 - Toddler, Early Morning:")
    print(f"Blocks: {blocks_3}")
    print(f"Count: {len(blocks_3)} blocks")
    print(f"Estimated pages: {selector.get_estimated_pages(test_quiz_3)}")
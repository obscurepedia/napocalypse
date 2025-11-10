"""
Block Selector Service

This service determines which content blocks to include in a personalized guide
based on the customer's quiz responses.

Logic:
- 1 age-based block (condensed version)
- 1 method block (combined overview + implementation)
- 1 challenge block (primary only, not secondary)
- 0-1 situation blocks (only if critical)

Total: 3-4 blocks per customer = 10-16 pages
"""

from typing import List, Dict, Any


class BlockSelector:
    """Selects appropriate content blocks based on quiz responses."""
    
    # Block definitions (using condensed versions)
    AGE_BLOCKS = {
        '4-6': 'age_4_6_months_condensed',
        '7-12': 'age_7_12_months_condensed',
        '13-18': 'age_13_18_months_condensed',
        '19-24': 'age_19_24_months_condensed'
    }
    
    METHOD_BLOCKS = {
        'cio': 'method_cio_combined',      # Single combined block
        'gentle': 'method_gentle_combined'  # Single combined block
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
            List of block identifiers to include in the guide (3-4 blocks)
            
        Example quiz_responses:
        {
            'baby_age': '7-12',
            'sleep_method': 'gentle',
            'main_challenge': 'motion',
            'secondary_challenge': 'pacifier',  # IGNORED
            'living_situation': 'apartment',
            'room_sharing': True
        }
        """
        selected_blocks = []
        
        # 1. Age-based block (always included - condensed version)
        age_block = self._select_age_block(quiz_responses)
        if age_block:
            selected_blocks.append(age_block)
        
        # 2. Method block (always included - single combined block)
        method_block = self._select_method_block(quiz_responses)
        selected_blocks.append(method_block)
        
        # 3. Challenge block (PRIMARY ONLY - not secondary)
        challenge_block = self._select_primary_challenge_block(quiz_responses)
        if challenge_block:
            selected_blocks.append(challenge_block)
        
        # 4. Situation block (only if critical)
        situation_block = self._select_situation_block_if_critical(quiz_responses)
        if situation_block:
            selected_blocks.append(situation_block)
        
        return selected_blocks  # 3-4 blocks total
    
    def _select_age_block(self, quiz_responses: Dict[str, Any]) -> str:
        """Select the appropriate age-based block (condensed version)."""
        baby_age = quiz_responses.get('baby_age', '7-12')
        return self.AGE_BLOCKS.get(baby_age, 'age_7_12_months_condensed')
    
    def _select_method_block(self, quiz_responses: Dict[str, Any]) -> str:
        """Select the appropriate method block (single combined block)."""
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
    
    def _select_primary_challenge_block(self, quiz_responses: Dict[str, Any]) -> str:
        """Select ONLY the primary challenge block (ignore secondary)."""
        main_challenge = quiz_responses.get('main_challenge', '')
        if main_challenge:
            return self._map_challenge_to_block(main_challenge)
        
        # If no main challenge specified, default to nap training
        return self.CHALLENGE_BLOCKS['naps']
    
    def _map_challenge_to_block(self, challenge: str) -> str:
        """Map quiz challenge response to block identifier."""
        challenge_mapping = {
            'feeding_to_sleep': 'feeding',
            'feed_to_sleep': 'feeding',
            'nursing_to_sleep': 'feeding',
            'bottle_to_sleep': 'feeding',
            'rocking': 'motion',
            'bouncing': 'motion',
            'motion': 'motion',
            'stroller': 'motion',
            'car': 'motion',
            'pacifier': 'pacifier',
            'paci': 'pacifier',
            'binky': 'pacifier',
            'naps': 'naps',
            'short_naps': 'naps',
            'nap_training': 'naps',
            'early_morning': 'early_morning',
            'early_waking': 'early_morning',
            'waking_early': 'early_morning'
        }
        
        challenge_key = challenge_mapping.get(challenge.lower(), challenge.lower())
        return self.CHALLENGE_BLOCKS.get(challenge_key, self.CHALLENGE_BLOCKS['naps'])
    
    def _select_situation_block_if_critical(self, quiz_responses: Dict[str, Any]) -> str:
        """Select situation block ONLY if it's critical to success."""
        # Only include if room sharing (most critical situation)
        room_sharing = quiz_responses.get('room_sharing', False)
        living_situation = quiz_responses.get('living_situation', '')
        
        if room_sharing or 'room_sharing' in living_situation.lower():
            return self.SITUATION_BLOCKS['room_sharing']
        
        # Skip apartment living block to keep guide shorter
        # (Most apartment tips are covered in method blocks)
        return None
    
    def get_block_count(self, quiz_responses: Dict[str, Any]) -> int:
        """Get the total number of blocks that will be included."""
        blocks = self.select_blocks(quiz_responses)
        return len(blocks)
    
    def get_estimated_pages(self, quiz_responses: Dict[str, Any]) -> int:
        """
        Estimate the number of pages in the final guide.
        
        Each block is approximately:
        - Age (condensed): 1.5 pages
        - Method (combined): 5-6 pages
        - Challenge: 8-10 pages
        - Situation: 4-5 pages
        
        Total: 10-16 pages for 3-4 blocks
        """
        blocks = self.select_blocks(quiz_responses)
        
        # Estimate pages per block type
        total_pages = 0
        for block in blocks:
            if 'age' in block:
                total_pages += 1.5
            elif 'method' in block:
                total_pages += 5.5
            elif 'challenge' in block:
                total_pages += 9
            elif 'situation' in block:
                total_pages += 4.5
        
        return int(total_pages)


# Example usage and testing
if __name__ == "__main__":
    selector = BlockSelector()
    
    # Test case 1: Deenah's case (Gentle, Motion, Room Sharing)
    test_quiz_1 = {
        'baby_age': '7-12',
        'sleep_method': 'gentle',
        'main_challenge': 'rocking',
        'secondary_challenge': 'pacifier',  # IGNORED
        'living_situation': 'house',
        'room_sharing': True
    }
    
    blocks_1 = selector.select_blocks(test_quiz_1)
    print("Test Case 1 - Deenah (Gentle, Motion, Room Sharing):")
    print(f"Blocks: {blocks_1}")
    print(f"Count: {len(blocks_1)} blocks")
    print(f"Estimated pages: {selector.get_estimated_pages(test_quiz_1)}")
    print()
    
    # Test case 2: CIO with feeding challenge, no situation
    test_quiz_2 = {
        'baby_age': '4-6',
        'sleep_method': 'cio',
        'main_challenge': 'feeding_to_sleep',
        'secondary_challenge': 'naps',  # IGNORED
        'living_situation': 'house',
        'room_sharing': False
    }
    
    blocks_2 = selector.select_blocks(test_quiz_2)
    print("Test Case 2 - CIO, Feeding, No Situation:")
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
        'living_situation': 'apartment',  # NOT included (not critical)
        'room_sharing': False
    }
    
    blocks_3 = selector.select_blocks(test_quiz_3)
    print("Test Case 3 - Toddler, Early Morning, Apartment (not included):")
    print(f"Blocks: {blocks_3}")
    print(f"Count: {len(blocks_3)} blocks")
    print(f"Estimated pages: {selector.get_estimated_pages(test_quiz_3)}")
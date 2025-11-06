"""
Personalization Service

This service handles personalization of content blocks by replacing
placeholders with customer-specific information.

Personalization includes:
- Customer name
- Baby's age
- Specific method chosen
- Challenges being addressed
- Living situation details
"""

from typing import Dict, Any
import re


class PersonalizationService:
    """Handles personalization of content blocks."""
    
    def __init__(self):
        """Initialize the personalization service."""
        pass
    
    def personalize_content(self, content: str, context: Dict[str, Any]) -> str:
        """
        Replace placeholders in content with personalized information.
        
        Args:
            content: The content block text (markdown)
            context: Dictionary containing personalization data
            
        Returns:
            Personalized content with placeholders replaced
        """
        # Create personalization variables
        variables = self._create_variables(context)
        
        # Replace placeholders
        personalized = content
        for placeholder, value in variables.items():
            # Replace {placeholder} format
            personalized = personalized.replace(f'{{{placeholder}}}', value)
            
            # Also replace {{placeholder}} format (double braces)
            personalized = personalized.replace(f'{{{{{placeholder}}}}}', value)
        
        return personalized
    
    def _create_variables(self, context: Dict[str, Any]) -> Dict[str, str]:
        """
        Create personalization variables from context.
        
        Args:
            context: Customer information from quiz and database
            
        Returns:
            Dictionary of placeholder -> value mappings
        """
        # Extract basic info
        customer_name = context.get('customer_name', '')
        baby_age = context.get('baby_age', '7-12')
        sleep_method = context.get('sleep_method', 'cio')
        main_challenge = context.get('main_challenge', '')
        
        # Create display-friendly versions
        baby_age_display = self._format_baby_age(baby_age)
        method_display = self._format_method(sleep_method)
        challenge_display = self._format_challenge(main_challenge)
        
        # Build variables dictionary
        variables = {
            # Basic info
            'customer_name': customer_name,
            'baby_age': baby_age,
            'baby_age_display': baby_age_display,
            'sleep_method': sleep_method,
            'method': method_display,
            'method_display': method_display,
            'main_challenge': main_challenge,
            'challenge': challenge_display,
            'challenge_display': challenge_display,
            
            # Possessive forms
            'customer_name_possessive': f"{customer_name}'s" if customer_name else "your",
            
            # Conditional text
            'greeting': f"Hi {customer_name}!" if customer_name else "Hello!",
            'personal_address': customer_name if customer_name else "you",
        }
        
        return variables
    
    def _format_baby_age(self, age_code: str) -> str:
        """Convert age code to display format."""
        age_mapping = {
            '4-6': '4-6 month',
            '7-12': '7-12 month',
            '13-18': '13-18 month',
            '19-24': '19-24 month'
        }
        return age_mapping.get(age_code, age_code)
    
    def _format_method(self, method_code: str) -> str:
        """Convert method code to display format."""
        method_mapping = {
            'cio': 'Cry-It-Out',
            'cry_it_out': 'Cry-It-Out',
            'ferber': 'Graduated Extinction (Ferber)',
            'gentle': 'Gentle Sleep Training',
            'chair': 'Chair Method',
            'gradual': 'Gradual Approach'
        }
        return method_mapping.get(method_code.lower(), method_code)
    
    def _format_challenge(self, challenge_code: str) -> str:
        """Convert challenge code to display format."""
        challenge_mapping = {
            'feeding': 'feeding to sleep',
            'feeding_to_sleep': 'feeding to sleep',
            'motion': 'motion dependency',
            'rocking': 'rocking to sleep',
            'bouncing': 'bouncing to sleep',
            'pacifier': 'pacifier dependency',
            'naps': 'short naps',
            'nap_training': 'nap challenges',
            'early_morning': 'early morning waking',
            'early_waking': 'early morning waking'
        }
        return challenge_mapping.get(challenge_code.lower(), challenge_code)
    
    def create_context_from_quiz(self, quiz_responses: Dict[str, Any], 
                                 customer_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a complete personalization context from quiz responses and customer info.
        
        Args:
            quiz_responses: Answers from the quiz
            customer_info: Additional customer information (name, email, etc.)
            
        Returns:
            Complete context dictionary for personalization
        """
        context = {}
        
        # Add customer info
        if customer_info:
            context['customer_name'] = customer_info.get('name', '')
            context['customer_email'] = customer_info.get('email', '')
        
        # Add quiz responses
        context.update(quiz_responses)
        
        # Add computed fields
        context['baby_age_display'] = self._format_baby_age(quiz_responses.get('baby_age', '7-12'))
        context['method_display'] = self._format_method(quiz_responses.get('sleep_method', 'cio'))
        context['main_challenge_display'] = self._format_challenge(quiz_responses.get('main_challenge', ''))
        
        return context
    
    def add_table_of_contents_markers(self, content: str) -> str:
        """
        Add markers for table of contents generation.
        
        Finds all H1 and H2 headers and adds TOC markers.
        
        Args:
            content: Markdown content
            
        Returns:
            Content with TOC markers added
        """
        # This will be used by the template engine to generate TOC
        # For now, just return content as-is
        return content
    
    def format_for_pdf(self, content: str) -> str:
        """
        Format content for PDF generation.
        
        Makes adjustments for better PDF rendering:
        - Adjusts heading levels
        - Adds page break hints
        - Formats lists and tables
        
        Args:
            content: Markdown content
            
        Returns:
            PDF-optimized content
        """
        # Add page break before major sections (H1 headers)
        content = re.sub(r'\n# ', r'\n\n<div class="page-break"></div>\n\n# ', content)
        
        # Ensure proper spacing around headers
        content = re.sub(r'\n(#{1,6} )', r'\n\n\1', content)
        
        # Ensure proper spacing around lists
        content = re.sub(r'\n(\* |\d+\. )', r'\n\n\1', content)
        
        return content


# Example usage
if __name__ == "__main__":
    service = PersonalizationService()
    
    # Test context creation
    quiz_responses = {
        'baby_age': '7-12',
        'sleep_method': 'cio',
        'main_challenge': 'feeding_to_sleep',
        'secondary_challenge': 'naps',
        'living_situation': 'apartment',
        'room_sharing': False
    }
    
    customer_info = {
        'name': 'Sarah',
        'email': 'sarah@example.com'
    }
    
    context = service.create_context_from_quiz(quiz_responses, customer_info)
    
    print("=== Personalization Context ===")
    for key, value in context.items():
        print(f"{key}: {value}")
    
    # Test content personalization
    sample_content = """
# Sleep Training Guide for {customer_name}

Welcome, {customer_name}! This guide is customized for your {baby_age_display} old baby.

## Your Situation

You've chosen the {method_display} method to address {challenge_display}.

## Getting Started

{greeting} Let's begin your journey to better sleep.

Your {baby_age_display} old is ready for sleep training, and the {method} approach
will work well for addressing {challenge}.

Good luck, {personal_address}!
"""
    
    personalized = service.personalize_content(sample_content, context)
    
    print("\n=== Original Content ===")
    print(sample_content)
    
    print("\n=== Personalized Content ===")
    print(personalized)
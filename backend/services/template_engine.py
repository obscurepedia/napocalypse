"""
Template Engine Service - V2 Integration

This is the core service that assembles personalized sleep training guides
from modular content blocks.

Process:
1. Select appropriate blocks based on quiz responses
2. Load content from markdown files
3. Add transitions between blocks
4. Personalize content with customer information
5. Generate table of contents
6. Format for PDF generation
7. Return complete guide as markdown
"""

import os
from typing import List, Dict, Any
from pathlib import Path


class TemplateEngine:
    """Assembles personalized sleep training guides from content blocks."""
    
    def __init__(self, content_blocks_dir: str = None):
        """
        Initialize the template engine.
        
        Args:
            content_blocks_dir: Path to content_blocks directory
                               (defaults to ../../content_blocks relative to this file)
        """
        if content_blocks_dir is None:
            # Default to content_blocks directory in napocalypse root
            current_dir = Path(__file__).parent.parent.parent
            content_blocks_dir = current_dir / 'content_blocks'
        
        self.content_blocks_dir = Path(content_blocks_dir)
        
        # Import V2 services
        from .block_selector import BlockSelector
        from .transitions import TransitionGenerator
        from .personalization_v2 import PersonalizationService
        
        self.block_selector = BlockSelector()
        self.transition_generator = TransitionGenerator()
        self.personalization_service = PersonalizationService()
    
    def generate_guide(self, quiz_responses: Dict[str, Any], 
                      customer_info: Dict[str, Any] = None) -> str:
        """
        Generate a complete personalized sleep training guide.
        
        Args:
            quiz_responses: Customer's quiz answers
            customer_info: Additional customer information (name, email, etc.)
            
        Returns:
            Complete guide as markdown string
        """
        # 1. Create personalization context
        context = self.personalization_service.create_context_from_quiz(
            quiz_responses, customer_info
        )
        
        # 2. Select appropriate content blocks
        selected_blocks = self.block_selector.select_blocks(quiz_responses)
        
        # 3. Load and assemble content
        guide_content = self._assemble_guide(selected_blocks, context)
        
        # 4. Add introduction and conclusion
        guide_content = self._add_wrapper(guide_content, context)
        
        # 5. Generate table of contents
        guide_content = self._add_table_of_contents(guide_content)
        
        return guide_content
    
    def _assemble_guide(self, block_ids: List[str], context: Dict[str, Any]) -> str:
        """
        Assemble content blocks with transitions.
        
        Args:
            block_ids: List of block identifiers to include
            context: Personalization context
            
        Returns:
            Assembled content with transitions
        """
        assembled_content = []
        
        for i, block_id in enumerate(block_ids):
            # Load block content
            block_content = self._load_block(block_id)
            
            if block_content:
                # Personalize the content
                personalized_content = self.personalization_service.personalize_content(
                    block_content, context
                )
                
                # Add the content
                assembled_content.append(personalized_content)
                
                # Add transition to next block (if not last block)
                if i < len(block_ids) - 1:
                    next_block_id = block_ids[i + 1]
                    transition = self.transition_generator.get_transition(
                        block_id, next_block_id, context
                    )
                    assembled_content.append(transition)
        
        return '\n\n'.join(assembled_content)
    
    def _load_block(self, block_id: str) -> str:
        """
        Load content from a block file.
        
        Args:
            block_id: Block identifier (e.g., 'age_7_12_months')
            
        Returns:
            Block content as string, or empty string if not found
        """
        # Determine subdirectory based on block type
        if block_id.startswith('age_'):
            subdir = 'age'
        elif block_id.startswith('method_'):
            subdir = 'method'
        elif block_id.startswith('challenge_'):
            subdir = 'challenge'
        elif block_id.startswith('situation_'):
            subdir = 'situation'
        else:
            print(f"Warning: Unknown block type for {block_id}")
            return ''
        
        # Construct file path
        file_path = self.content_blocks_dir / subdir / f"{block_id}.md"
        
        # Load content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except FileNotFoundError:
            print(f"Warning: Block file not found: {file_path}")
            return ''
        except Exception as e:
            print(f"Error loading block {block_id}: {str(e)}")
            return ''
    
    def _add_wrapper(self, content: str, context: Dict[str, Any]) -> str:
        """
        Add introduction and conclusion to guide.
        
        Args:
            content: Main guide content
            context: Personalization context
            
        Returns:
            Complete guide with intro and conclusion
        """
        baby_name = context.get('baby_name', 'your baby')
        customer_name = context.get('customer_name', 'there')
        baby_age = context.get('baby_age', 'your baby\'s age')
        method = context.get('method', 'sleep training')
        
        intro = f"""# Your Personalized Sleep Training Guide

Welcome {customer_name}!

This guide has been specifically created for {baby_name} based on your quiz responses. Everything you need to succeed is right here in these focused pages.

## Your Situation

- **Baby's Age:** {baby_age}
- **Your Approach:** {method}
- **What You'll Learn:** A complete, step-by-step plan customized for your family

## How to Use This Guide

1. **Read it through once** - Get the complete picture before starting
2. **Follow the action plan** - Each section has clear next steps
3. **Stay consistent** - Results typically come within 3-7 days
4. **Trust the process** - You've got everything you need right here

Let's get started!

---

"""
        
        conclusion = f"""

---

## You're Ready to Succeed!

You now have everything you need to transform {baby_name}'s sleep. This guide is focused, actionable, and personalized specifically for your situation.

### What Happens Next

Over the next 7 days, you'll receive daily emails with:
- Implementation tips specific to your approach
- Troubleshooting advice for common challenges
- Encouragement and support
- Progress tracking guidance

### Remember

- **Be consistent** - The method works when you stick with it
- **Trust yourself** - You know your baby best
- **Stay patient** - Results typically come within 3-7 days
- **We're here** - Reply to any email if you need help

### 100% Money-Back Guarantee

If you don't see improvement within 14 days, we'll refund every penny. No questions asked.

---

**You've got this!**

The Napocalypse Team  
support@napocalypse.com
"""
        
        return intro + content + conclusion
    
    def _add_table_of_contents(self, content: str) -> str:
        """
        Generate and add table of contents.
        
        Args:
            content: Guide content
            
        Returns:
            Content with TOC added
        """
        # Extract headers (lines starting with ##)
        lines = content.split('\n')
        headers = []
        
        for line in lines:
            if line.startswith('## ') and not line.startswith('## Your Situation'):
                header_text = line.replace('## ', '').strip()
                headers.append(header_text)
        
        if not headers:
            return content
        
        # Build TOC
        toc = "\n## What's Inside This Guide\n\n"
        for i, header in enumerate(headers, 1):
            toc += f"{i}. {header}\n"
        toc += "\n---\n"
        
        # Insert TOC after introduction (after first ---) 
        parts = content.split('---', 1)
        if len(parts) == 2:
            return parts[0] + '---' + toc + parts[1]
        else:
            return content


def generate_personalized_guide(quiz_responses: Dict[str, Any], 
                                customer_info: Dict[str, Any] = None) -> str:
    """
    Convenience function to generate a personalized guide.
    
    Args:
        quiz_responses: Customer's quiz answers
        customer_info: Additional customer information
        
    Returns:
        Complete guide as markdown string
    """
    engine = TemplateEngine()
    return engine.generate_guide(quiz_responses, customer_info)
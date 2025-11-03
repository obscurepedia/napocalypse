import os
import re

def extract_key_actionable_content(full_content, module_name):
    """
    Extract the most essential, actionable content from full modules
    Keeps content focused and practical - about 2-3 pages per module
    """
    # Split content into sections
    lines = full_content.split('\n')
    
    # Look for key action sections and practical steps
    key_sections = []
    current_section = []
    include_section = False
    
    for line in lines:
        # Start capturing when we hit actionable content
        if any(keyword in line.lower() for keyword in [
            'step-by-step', 'action plan', 'how to', 'implementation', 
            'complete guide', 'practical', 'solutions', 'method', 'strategy'
        ]):
            include_section = True
            
        # Stop capturing for overly detailed sections
        if any(keyword in line.lower() for keyword in [
            'troubleshooting', 'detailed explanation', 'research shows',
            'additional resources', 'appendix'
        ]):
            include_section = False
            
        if include_section and line.strip():
            current_section.append(line)
            
        # Section breaks
        if line.startswith('# ') and current_section:
            if len(current_section) > 5:  # Only include substantial sections
                key_sections.extend(current_section)
                key_sections.append('')  # Add spacing
            current_section = []
    
    # Add any remaining content
    if current_section and len(current_section) > 5:
        key_sections.extend(current_section)
    
    # If extraction didn't work well, fall back to first portion of content
    if len(key_sections) < 20:
        # Take first 40% of content
        total_lines = len(lines)
        key_sections = lines[:int(total_lines * 0.4)]
    
    # Ensure we have title and some content
    result = []
    if lines and lines[0].startswith('#'):
        result.append(lines[0])  # Keep title
        result.append('')
    
    # Add condensed actionable content
    result.extend(key_sections[:100])  # Limit to ~100 lines max per module
    
    return '\n'.join(result)

# Test with actual module
module_path = 'content/modules/module_1_newborn_FULL_CONTENT.md'
with open(module_path, 'r', encoding='utf-8') as f:
    full_content = f.read()

condensed = extract_key_actionable_content(full_content, 'module_1_newborn')

print(f"ORIGINAL: {len(full_content)} characters, {len(full_content.split(chr(10)))} lines")
print(f"CONDENSED: {len(condensed)} characters, {len(condensed.split(chr(10)))} lines")
print(f"Reduction: {((len(full_content) - len(condensed)) / len(full_content) * 100):.1f}%")
print(f"\nEstimated pages for condensed version: {len(condensed) // 2500}")
print(f"\nFirst 500 characters of condensed:")
print(condensed[:500] + "...")
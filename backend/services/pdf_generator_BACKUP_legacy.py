"""
# -*- coding: utf-8 -*-
PDF Generation Service
Combines selected modules into a personalized PDF guide
"""

import os
import re
from datetime import datetime
from config import Config
from .module_selector import get_module_info

# Try to import markdown2 for v2 system
try:
    import markdown2
    MARKDOWN2_AVAILABLE = True
except ImportError:
    print("Warning: markdown2 not available - V2 template system requires it")
    MARKDOWN2_AVAILABLE = False
    markdown2 = None

# Try to import WeasyPrint, fallback if not available
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError, TypeError) as e:
    print(f"Warning: WeasyPrint not available - {e}")
    WEASYPRINT_AVAILABLE = False
    HTML = None
    CSS = None

def format_quiz_value(field_name, value):
    """
    Convert raw quiz form values to user-friendly text
    """
    if not value or value == 'N/A':
        return 'Not specified'
    
    # Map form values to readable text
    value_mappings = {
        # Baby age
        '0-3_months': '0-3 months',
        '4-6_months': '4-6 months', 
        '7-12_months': '7-12 months',
        '13-24_months': '13-24 months (toddler)',
        '2_plus_years': '2+ years',
        
        # Sleep challenges
        'frequent_night_waking': 'Frequent night waking',
        'difficulty_falling_asleep': 'Difficulty falling asleep',
        'early_morning_wake': 'Early morning wake-ups',
        'short_naps': 'Short naps',
        'wakes_when_putting_down': 'Wakes when putting down',
        'needs_help_to_sleep': 'Needs help to fall asleep',
        'bedtime_battles': 'Bedtime battles',
        'room_sharing_issues': 'Room sharing difficulties',
        
        # Sleep philosophy
        'gentle_methods': 'Gentle, no-cry methods',
        'cry_it_out': 'Cry-it-out approach',
        'flexible_approach': 'Flexible approach',
        'whatever_works': 'Whatever works best',
        
        # Living situation
        'own_room': 'Baby has own room',
        'room_sharing_parents': 'Room sharing with parents',
        'room_sharing_siblings': 'Room sharing with siblings',
        'apartment_thin_walls': 'Apartment with thin walls',
        'open_plan_living': 'Open plan living space'
    }
    
    return value_mappings.get(value, value.replace('_', ' ').title())

def get_personalized_subtitle(customer):
    """
    Generate personalized subtitle based on available customer data
    """
    parent_name = customer.name
    baby_name = customer.baby_name
    
    if parent_name and baby_name:
        return f"{parent_name} and baby {baby_name}"
    elif parent_name:
        return f"{parent_name} and your little one"
    elif baby_name:
        return f"you and baby {baby_name}"
    else:
        return "your family"

def generate_personalized_pdf(customer, quiz_data, modules=None, is_upsell=False, guide_content=None, is_v2=False):
    """
    Generate personalized PDF guide
    
    Args:
        customer: Customer object
        quiz_data (dict): Quiz response data
        modules (list): List of module names to include (for v1 system)
        is_upsell (bool): If True, use FULL content; if False, use ESSENTIAL (for v1 system)
        guide_content (str): Markdown content from V2 template engine (if is_v2=True)
        is_v2 (bool): If True, use guide_content; if False, use old module system
        
    Returns:
        str: Path to generated PDF
    """
    # Check if WeasyPrint is available
    if not WEASYPRINT_AVAILABLE:
        raise RuntimeError("PDF generation not available: WeasyPrint dependencies not installed")
    
    # Create filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if is_v2:
        version = "PERSONALIZED"
    else:
        version = "FULL" if is_upsell else "ESSENTIAL"
    
    filename = f"sleep_guide_{version}_{customer.id}_{timestamp}.pdf"
    output_path = os.path.join(Config.PDF_OUTPUT_DIR, filename)
    
    # Ensure output directory exists
    os.makedirs(Config.PDF_OUTPUT_DIR, exist_ok=True)
    
    # Generate HTML content
    if is_v2 and guide_content:
        html_content = generate_html_from_markdown(customer, quiz_data, guide_content)
    else:
        # Fallback to old system
        if not modules:
            modules = []
        html_content = generate_html_content(customer, quiz_data, modules, is_upsell)
    
    # Generate PDF
    HTML(string=html_content).write_pdf(
        output_path,
        stylesheets=[CSS(string=get_pdf_styles())]
    )
    
    return output_path

def generate_html_from_markdown(customer, quiz_data, guide_markdown):
    """
    Convert V2 guide markdown to HTML for PDF generation
    
    Args:
        customer: Customer object
        quiz_data: Quiz response data
        guide_markdown: Complete guide as markdown
        
    Returns:
        HTML string ready for PDF conversion
    """
    if not MARKDOWN2_AVAILABLE:
        raise RuntimeError("V2 PDF generation not available: markdown2 package not installed")
    
    # Convert markdown to HTML
    html_body = markdown2.markdown(
        guide_markdown,
        extras=['fenced-code-blocks', 'tables', 'break-on-newline']
    )
    
    # Wrap in complete HTML document
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Your Personalized Baby Sleep Guide</title>
    </head>
    <body>
        <div class="guide-content">
            {html_body}
        </div>
        
        <!-- Footer on last page -->
        <div class="footer-page">
            <hr style="border: none; border-top: 2px solid #ddd; margin: 30px 0;">
            <div style="text-align: center; color: #666; font-size: 10pt;">
                <p>&copy; {datetime.now().year} Napocalypse. All rights reserved.</p>
                <p>support@napocalypse.com | napocalypse.com</p>
                <p style="margin-top: 20px; font-size: 9pt;">
                    This guide is for informational purposes only and does not constitute medical advice.<br>
                    Always consult with your pediatrician before making changes to your baby's sleep routine.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def generate_html_content(customer, quiz_data, modules, is_upsell=False):
    """
    Generate HTML content for PDF
    """
    # Get module information
    module_details = [get_module_info(m) for m in modules]
    
    # Build HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Your Personalized Baby Sleep Guide</title>
    </head>
    <body>
        <!-- Cover Page -->
        <div class="cover-page">
            <div class="logo-header">
                <img src="file://{os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend/images/napocalypse.png'))}" alt="Napocalypse Logo" class="pdf-logo">
            </div>
            <h1>Your Personalized Baby Sleep Guide</h1>
            {f'<p class="subtitle">Complete Reference Library</p>' if is_upsell else ''}
            <p class="subtitle">Customized for {get_personalized_subtitle(customer)}</p>
            <p class="date">Generated: {datetime.now().strftime('%B %d, %Y')}</p>
            
            <div class="footer">
                <p>&copy; {datetime.now().year} Napocalypse. All rights reserved.</p>
                <p>support@napocalypse.com</p>
            </div>
        </div>
        
        <!-- Introduction Page -->
        <div class="page-break"></div>
        <div class="intro-page">
            <h1>Welcome to Your Sleep Journey{', ' + customer.name if customer.name else ''}!</h1>
            
            <p>Congratulations on taking the first step toward better sleep for your entire family!</p>
            
            <p>This guide has been personalized specifically for you{' and ' + customer.baby_name if customer.baby_name else ''} based on your quiz responses:</p>
            
            <div class="quiz-summary">
                <h3>Your Situation:</h3>
                <ul>
                    <li><strong>{customer.baby_name + "'s" if customer.baby_name else "Baby's"} Age:</strong> {format_quiz_value('baby_age', quiz_data.get('baby_age', 'N/A'))}</li>
                    <li><strong>Sleep Challenge:</strong> {format_quiz_value('biggest_challenge', quiz_data.get('biggest_challenge', 'N/A'))}</li>
                    <li><strong>Your Approach:</strong> {format_quiz_value('sleep_philosophy', quiz_data.get('sleep_philosophy', 'N/A'))}</li>
                    <li><strong>Living Situation:</strong> {format_quiz_value('living_situation', quiz_data.get('living_situation', 'N/A'))}</li>
                </ul>
            </div>
            
            <h3>What's Inside:</h3>
            <p>Your guide contains {len(modules)} carefully selected modules that address your specific needs:</p>
            
            <ol>
                {''.join([f'<li><strong>{m["title"]}</strong><br>{m["description"]}</li>' for m in module_details])}
            </ol>
            
            <h3>How to Use This Guide:</h3>
            <ol>
                <li>Read through all modules to understand the complete approach</li>
                <li>Start with the preparation steps in your first module</li>
                <li>Follow the action plans step-by-step</li>
                <li>Track your progress using the provided checklists</li>
                <li>Stay consistent - results typically come within 3-14 days</li>
            </ol>
            
            <div class="encouragement-box">
                <h3>You've Got This{', ' + customer.name if customer.name else ''}!</h3>
                <p>Better sleep for {customer.baby_name if customer.baby_name else 'your baby'} is just days away. Trust the process, stay consistent, and remember: you're teaching {customer.baby_name if customer.baby_name else 'your little one'} a valuable life skill that will benefit your entire family.</p>
            </div>
        </div>
        
        <!-- Module Content -->
        {generate_module_content(modules, is_upsell)}
        
        <!-- Conclusion Page -->
        <div class="page-break"></div>
        <div class="conclusion-page">
            <h1>Next Steps & Support</h1>
            
            <h2>What Happens Now?</h2>
            <p>Over the next 7 days, you'll receive daily emails with:</p>
            <ul>
                <li>Implementation tips specific to your situation</li>
                <li>Troubleshooting advice</li>
                <li>Encouragement and support</li>
                <li>Progress tracking guidance</li>
            </ul>
            
            <h2>Need More Help?</h2>
            <p>If you have questions or need additional support:</p>
            <ul>
                <li>Reply to any of our emails</li>
                <li>Visit napocalypse.com for resources</li>
                <li>Check out our additional guides for specific challenges</li>
            </ul>
            
            <h2>100% Money-Back Guarantee</h2>
            <p>If you don't see improvement in your baby's sleep within 14 days, we'll refund every penny. No questions asked.</p>
            
            <h2>Share Your Success!</h2>
            <p>Once your baby is sleeping better, we'd love to hear about it! Email us at support@napocalypse.com with your success story.</p>
            
            <div class="final-message">
                <h3>You're Ready!</h3>
                <p>Everything you need is in this guide. Trust yourself, trust your baby, and trust the process.</p>
                <p>Here's to better sleep for your entire family!</p>
                <p><strong>The Napocalypse Team</strong></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def generate_module_content(modules, is_upsell=False):
    """
    Load and combine module content based on version (Essential vs Full)
    """
    content_dir = os.path.join(os.path.dirname(__file__), '../../content/modules')
    combined_content = ""
    
    # Use FULL or ESSENTIAL version based on is_upsell flag
    version = "FULL_CONTENT" if is_upsell else "ESSENTIAL"
    
    for module_name in modules:
        module_file = f"{module_name}_{version}.md"
        module_path = os.path.join(content_dir, module_file)
        
        if os.path.exists(module_path):
            try:
                with open(module_path, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()
                # Convert markdown to HTML
                html_content = convert_markdown_to_html(markdown_content)
                combined_content += f'<div class="page-break"></div><div class="module-content">{html_content}</div>'
            except Exception as e:
                print(f"Error loading module {module_name}: {str(e)}")
                combined_content += f'<div class="page-break"></div><div class="module-content"><h1>Error loading {module_name}</h1><p>Content temporarily unavailable.</p></div>'
        else:
            print(f"Module file not found: {module_file}")
            combined_content += f'<div class="page-break"></div><div class="module-content"><h1>{module_name}</h1><p>Module content will be added here.</p></div>'
    
    return combined_content


def convert_markdown_to_html(markdown_text):
    """
    Convert markdown content to HTML for PDF generation
    """
    if not markdown_text:
        return ""
    
    html = markdown_text
    
    # Convert headers (order matters - start with h3, then h2, then h1)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)  
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Convert bold and italic text
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # Handle numbered lists first
    lines = html.split('\n')
    in_numbered_list = False
    processed_lines = []
    
    for line in lines:
        # Check if this is a numbered list item
        if re.match(r'^\d+\.\s+', line):
            if not in_numbered_list:
                processed_lines.append('<ol>')
                in_numbered_list = True
            # Convert to list item
            content = re.sub(r'^\d+\.\s+', '', line)
            processed_lines.append(f'<li>{content}</li>')
        else:
            if in_numbered_list:
                processed_lines.append('</ol>')
                in_numbered_list = False
            processed_lines.append(line)
    
    # Close any open numbered list
    if in_numbered_list:
        processed_lines.append('</ol>')
    
    html = '\n'.join(processed_lines)
    
    # Handle bullet point lists
    lines = html.split('\n')
    in_bullet_list = False
    processed_lines = []
    
    for line in lines:
        # Check if this is a bullet list item
        if re.match(r'^-\s+', line):
            if not in_bullet_list:
                processed_lines.append('<ul>')
                in_bullet_list = True
            # Convert to list item
            content = re.sub(r'^-\s+', '', line)
            processed_lines.append(f'<li>{content}</li>')
        else:
            if in_bullet_list:
                processed_lines.append('</ul>')
                in_bullet_list = False
            processed_lines.append(line)
    
    # Close any open bullet list
    if in_bullet_list:
        processed_lines.append('</ul>')
    
    html = '\n'.join(processed_lines)
    
    # Split into paragraphs on double newlines, but avoid breaking existing HTML
    lines = html.split('\n\n')
    processed_lines = []
    
    for line in lines:
        line = line.strip()
        if line:
            # If it's already HTML (starts with < or contains HTML tags), leave it as is
            if (line.startswith('<') or '</h' in line or '</ul>' in line or 
                '</ol>' in line or '<li>' in line or '<ul>' in line or '<ol>' in line):
                processed_lines.append(line)
            else:
                # Skip empty lines and wrap content in paragraph tags
                if line.strip():
                    processed_lines.append(f'<p>{line}</p>')
    
    html = '\n\n'.join(processed_lines)
    
    # Clean up extra whitespace and empty paragraphs
    html = re.sub(r'<p>\s*</p>', '', html)
    html = re.sub(r'\n{3,}', '\n\n', html)
    
    return html

def get_module_summary(module_name):
    """
    Get comprehensive content for each module (4-6 pages of substantial content per module)
    """
    summaries = {
        'module_1_newborn': """
            <h1>Newborn Sleep Foundations (0-3 Months)</h1>
            
            <div class="key-points">
                <h2>Understanding Your Newborn's Sleep:</h2>
                <p>Your newborn's sleep patterns are completely different from older babies. They sleep 14-17 hours per day but in 2-4 hour chunks because their tiny stomachs need frequent feeding.</p>
                
                <h3>What's Normal:</h3>
                <ul>
                    <li><strong>No day/night rhythm</strong> until 6-12 weeks (their circadian rhythm isn't developed)</li>
                    <li><strong>Frequent waking</strong> every 2-4 hours is biologically necessary</li>
                    <li><strong>Short naps</strong> of 30-45 minutes are typical</li>
                    <li><strong>Cluster feeding</strong> in the evenings is normal and doesn't mean low milk supply</li>
                    <li><strong>Sleep regressions</strong> around 6 weeks and 3 months are developmental leaps</li>
                </ul>
            </div>
            
            <h2>Your Complete Action Plan:</h2>
            
            <div class="action-steps">
                <h3>Step 1: Optimize the Sleep Environment</h3>
                <h4>Room Setup:</h4>
                <ul>
                    <li><strong>Temperature:</strong> 68-72°F (baby should feel cool to touch, not warm)</li>
                    <li><strong>Lighting:</strong> Blackout curtains for naps, dim red light for night feeds</li>
                    <li><strong>Sound:</strong> Consistent white noise at 50-60 decibels (like a shower running)</li>
                    <li><strong>Air quality:</strong> Well-ventilated room, consider air purifier if needed</li>
                </ul>
                
                <h4>Safe Sleep Checklist:</h4>
                <ul>
                    <li>✓ Firm sleep surface (mattress should not indent when baby lies down)</li>
                    <li>✓ Fitted sheet only (no loose bedding, bumpers, or toys)</li>
                    <li>✓ Baby on back for every sleep</li>
                    <li>✓ Sleep space in your room for first 6 months (but not in your bed)</li>
                </ul>
                
                <h3>Step 2: Establish Gentle Routines</h3>
                <h4>Bedtime Routine (Start Around 2-3 Weeks):</h4>
                <ol>
                    <li><strong>Bath time</strong> (2-3 times per week, warm water, 5-10 minutes)</li>
                    <li><strong>Fresh diaper and pajamas</strong> (this signals "sleep time")</li>
                    <li><strong>Feeding</strong> (breast or bottle in calm, dimly lit environment)</li>
                    <li><strong>Gentle burping</strong> (take your time, this prevents wake-ups from gas)</li>
                    <li><strong>Swaddling</strong> (arms down, snug but not tight around hips)</li>
                    <li><strong>5 minutes of calming</strong> (gentle shushing, rocking, or holding)</li>
                    <li><strong>Into sleep space</strong> while drowsy but awake (if possible)</li>
                </ol>
                
                <h4>Day vs. Night Distinction:</h4>
                <ul>
                    <li><strong>Daytime feeds:</strong> Bright lights, normal household noise, interaction and talking</li>
                    <li><strong>Nighttime feeds:</strong> Dim lighting, minimal talking, calm and boring</li>
                    <li><strong>Morning routine:</strong> Open curtains, bright light, cheerful voice</li>
                </ul>
                
                <h3>Step 3: Master Newborn Sleep Techniques</h3>
                
                <h4>The 5 S's for Soothing:</h4>
                <ol>
                    <li><strong>Swaddling:</strong> Recreates womb-like feeling, prevents startle reflex
                        <ul>
                            <li>Use muslin or specialized swaddle products</li>
                            <li>Arms down and straight, but loose around hips</li>
                            <li>If baby rolls or breaks free, transition to sleep sack</li>
                        </ul>
                    </li>
                    <li><strong>Side/Stomach position:</strong> For soothing only (always place on back to sleep)
                        <ul>
                            <li>Hold baby on side or stomach while calming</li>
                            <li>Rock gently or do "baby calisthenics" (gentle leg movements)</li>
                        </ul>
                    </li>
                    <li><strong>Shushing:</strong> Loud white noise or "shush" sounds
                        <ul>
                            <li>Volume should match baby's cry level</li>
                            <li>Constant, not rhythmic</li>
                            <li>Hair dryer, vacuum, or white noise app work well</li>
                        </ul>
                    </li>
                    <li><strong>Swinging:</strong> Gentle, continuous motion
                        <ul>
                            <li>Small, jiggly movements (not big swings)</li>
                            <li>Bouncy seat, rocking chair, or gentle bounce on exercise ball</li>
                            <li>Stop motion gradually once baby calms</li>
                        </ul>
                    </li>
                    <li><strong>Sucking:</strong> Pacifier or clean finger
                        <ul>
                            <li>Wait until breastfeeding is established (3-4 weeks)</li>
                            <li>Use pacifier for sleep, remove once baby falls asleep</li>
                            <li>Don't force if baby rejects it</li>
                        </ul>
                    </li>
                </ol>
                
                <h3>Step 4: Feeding for Better Sleep</h3>
                
                <h4>Timing Strategies:</h4>
                <ul>
                    <li><strong>Full feeds:</strong> Keep baby awake during feeds to ensure they get full nutrition</li>
                    <li><strong>Dream feeds:</strong> Around 10-11pm, feed sleeping baby to extend night sleep</li>
                    <li><strong>Cluster feeding:</strong> Allow frequent evening feeds (5-11pm) - this is normal and helpful</li>
                    <li><strong>Growth spurts:</strong> Around 2 weeks, 6 weeks, 3 months - expect increased feeding and fussiness</li>
                </ul>
                
                <h4>Signs Baby is Getting Enough:</h4>
                <ul>
                    <li>✓ Wet diapers: 6+ per day after day 6</li>
                    <li>✓ Weight gain: Back to birth weight by 2 weeks, then 4-7oz per week</li>
                    <li>✓ Alert periods: Baby has some wakeful, content periods</li>
                    <li>✓ Regular stooling: At least 1 per day (breastfed babies may go days between)</li>
                </ul>
                
                <h3>Step 5: Common Challenges & Solutions</h3>
                
                <h4>Baby Won't Sleep Unless Held:</h4>
                <ul>
                    <li><strong>Gradual transition:</strong> Hold for 10 minutes, then place down</li>
                    <li><strong>Warm the sleep surface:</strong> Use heating pad to warm bassinet, remove before placing baby</li>
                    <li><strong>Maintain contact:</strong> Keep hand on chest for a few minutes after putting down</li>
                    <li><strong>Swaddle tightly:</strong> Recreates feeling of being held</li>
                </ul>
                
                <h4>Frequent Night Wakings:</h4>
                <ul>
                    <li><strong>Rule out hunger:</strong> If baby calms with feeding, they're likely hungry</li>
                    <li><strong>Check diaper:</strong> Some babies wake when wet/soiled</li>
                    <li><strong>Room temperature:</strong> Too hot or cold can cause frequent waking</li>
                    <li><strong>Overtiredness:</strong> Watch for early sleep cues, put down sooner</li>
                </ul>
                
                <h4>Short Naps (30-45 minutes):</h4>
                <ul>
                    <li><strong>Normal for newborns:</strong> Sleep cycles are 45 minutes, they often wake between cycles</li>
                    <li><strong>Help them reconnect:</strong> Try gentle shushing or patting when they stir</li>
                    <li><strong>Motion naps:</strong> Stroller, car seat, or carrier naps often last longer</li>
                    <li><strong>Contact naps:</strong> One nap per day on parent's chest is fine and often longer</li>
                </ul>
                
                <h3>Step 6: Week-by-Week Expectations</h3>
                
                <h4>Weeks 0-2: Survival Mode</h4>
                <ul>
                    <li>Focus on feeding, bonding, and recovery</li>
                    <li>Sleep when baby sleeps</li>
                    <li>Accept help with household tasks</li>
                    <li>Start simple bedtime routine by week 2</li>
                </ul>
                
                <h4>Weeks 2-6: Finding Rhythm</h4>
                <ul>
                    <li>Begin to differentiate day and night</li>
                    <li>Establish consistent bedtime routine</li>
                    <li>Watch for early sleep cues</li>
                    <li>Expect 6-week growth spurt and increased fussiness</li>
                </ul>
                
                <h4>Weeks 6-12: Building Patterns</h4>
                <ul>
                    <li>Sleep stretches may begin to lengthen</li>
                    <li>More predictable wake windows emerge</li>
                    <li>Social smiles and increased alertness</li>
                    <li>Prepare for 3-4 month sleep regression</li>
                </ul>
            </div>
            
            <div class="next-steps">
                <h2>Preparing for Sleep Training (Around 4-6 Months):</h2>
                <h3>Signs of Readiness:</h3>
                <ul>
                    <li>Can stay awake for 1.5-2 hours between sleeps</li>
                    <li>Shows more predictable nap patterns</li>
                    <li>Can sleep for 6+ hour stretches occasionally</li>
                    <li>Weighs at least 12-14 pounds</li>
                    <li>No longer needs night feeds for nutrition (check with pediatrician)</li>
                </ul>
                
                <h3>What You've Built:</h3>
                <p>By following this foundation phase, you've established healthy sleep associations, 
                consistent routines, and an optimal sleep environment. These elements will make 
                formal sleep training much easier and more successful when your baby is developmentally ready.</p>
            </div>
        """,
        
        'module_6_gentle': """
            <h1>Gentle Sleep Training Methods</h1>
            
            <div class="key-points">
                <h2>Why Choose Gentle Methods:</h2>
                <p>Gentle sleep training respects your baby's emotional needs while still teaching independent sleep skills. 
                These methods work especially well for sensitive babies, anxious parents, or families who want to minimize crying.</p>
                
                <h3>Perfect for You If:</h3>
                <ul>
                    <li>You prefer a gradual approach with minimal crying</li>
                    <li>Your baby is highly sensitive or gets very upset with traditional methods</li>
                    <li>You want to maintain a strong attachment while building independence</li>
                    <li>You're willing to invest 2-4 weeks for gradual progress</li>
                    <li>You live in close quarters where crying would disturb others</li>
                </ul>
            </div>
            
            <h2>Complete Gentle Training System:</h2>
            
            <div class="action-steps">
                <h3>Method 1: The Chair Method (Gradual Retreat)</h3>
                
                <h4>How It Works:</h4>
                <p>You gradually move your presence away from your baby's sleep space over 2-3 weeks, 
                allowing them to slowly adjust to sleeping independently.</p>
                
                <h4>Week 1: Beside the Crib</h4>
                <ul>
                    <li><strong>Days 1-3:</strong> Place chair right next to crib where baby can see you</li>
                    <li><strong>Bedtime routine:</strong> Complete normal routine, then sit in chair</li>
                    <li><strong>When baby cries:</strong> Offer quiet verbal comfort ("Shhh, it's okay, time for sleep")</li>
                    <li><strong>Physical comfort:</strong> You can reach through crib bars to briefly pat or stroke</li>
                    <li><strong>Stay calm:</strong> Read a book, look at your phone, but avoid eye contact or stimulating baby</li>
                    <li><strong>Don't pick up:</strong> Unless baby is truly distressed (not just fussing)</li>
                </ul>
                
                <h4>Week 2: Moving Away</h4>
                <ul>
                    <li><strong>Days 4-6:</strong> Move chair halfway to the door</li>
                    <li><strong>Days 7-9:</strong> Move chair to the doorway</li>
                    <li><strong>Comfort from distance:</strong> Use only verbal comfort, no touching</li>
                    <li><strong>Reduced interaction:</strong> Speak less frequently, let baby work through minor fussing</li>
                </ul>
                
                <h4>Week 3: Independence</h4>
                <ul>
                    <li><strong>Days 10-12:</strong> Chair outside the room, door cracked open</li>
                    <li><strong>Days 13+:</strong> No chair, check-in only if baby is very upset</li>
                    <li><strong>Final step:</strong> Complete bedtime routine and leave room</li>
                </ul>
                
                <h4>Chair Method Troubleshooting:</h4>
                <ul>
                    <li><strong>Baby won't settle:</strong> Move back to previous chair position for 2-3 more days</li>
                    <li><strong>Regression:</strong> Stay at current position until baby adjusts</li>
                    <li><strong>Illness/travel:</strong> Pause the method, resume when back to normal</li>
                </ul>
                
                <h3>Method 2: Pick Up/Put Down (PUPD)</h3>
                
                <h4>How It Works:</h4>
                <p>You pick up your baby when they cry, comfort them until calm, then put them back down. 
                Repeat as needed until they fall asleep.</p>
                
                <h4>PUPD Step-by-Step:</h4>
                <ol>
                    <li><strong>Complete bedtime routine</strong> and put baby down awake</li>
                    <li><strong>Leave the room</strong> for 3-5 minutes</li>
                    <li><strong>If baby cries consistently:</strong> Return and pick them up</li>
                    <li><strong>Comfort until calm</strong> (not necessarily asleep) - usually 2-5 minutes</li>
                    <li><strong>Put baby back down</strong> while awake but calm</li>
                    <li><strong>Leave again</strong> and repeat cycle as needed</li>
                </ol>
                
                <h4>PUPD Success Tips:</h4>
                <ul>
                    <li><strong>Be consistent:</strong> Always pick up when baby cries, always put down when calm</li>
                    <li><strong>Stay boring:</strong> No talking, singing, or eye contact during comfort</li>
                    <li><strong>Don't rush:</strong> Make sure baby is truly calm before putting down</li>
                    <li><strong>Expect multiple rounds:</strong> May take 10-20 cycles the first few nights</li>
                    <li><strong>Track progress:</strong> Most babies improve significantly by night 3-5</li>
                </ul>
                
                <h4>When PUPD Works Best:</h4>
                <ul>
                    <li>Babies 6-12 months old</li>
                    <li>Babies who calm quickly when picked up</li>
                    <li>Parents who can handle multiple trips back to the nursery</li>
                    <li>When you have 2-3 weeks to be consistent</li>
                </ul>
                
                <h3>Method 3: Gradual Fading</h3>
                
                <h4>How It Works:</h4>
                <p>You gradually reduce the amount of help you provide for sleep over 1-3 weeks, 
                moving from high support to independence in small steps.</p>
                
                <h4>Fading Your Current Routine:</h4>
                
                <h5>If You Currently Rock to Sleep:</h5>
                <ul>
                    <li><strong>Week 1:</strong> Rock until drowsy (eyes heavy but open), then put down</li>
                    <li><strong>Week 2:</strong> Rock for 5 minutes regardless of drowsiness level, then put down</li>
                    <li><strong>Week 3:</strong> Gentle patting in crib instead of rocking</li>
                    <li><strong>Week 4:</strong> Hand on chest only, then no touch</li>
                </ul>
                
                <h5>If You Currently Feed to Sleep:</h5>
                <ul>
                    <li><strong>Week 1:</strong> Feed until drowsy, then detach and put down awake</li>
                    <li><strong>Week 2:</strong> Move feeding earlier in bedtime routine</li>
                    <li><strong>Week 3:</strong> Add 10 minutes between end of feed and putting down</li>
                    <li><strong>Week 4:</strong> Complete separation of feeding and sleep</li>
                </ul>
                
                <h5>If You Currently Co-sleep:</h5>
                <ul>
                    <li><strong>Week 1:</strong> Start night in baby's bed, come to your bed after first wake</li>
                    <li><strong>Week 2:</strong> Stay in baby's bed until 2am, then move to your bed</li>
                    <li><strong>Week 3:</strong> Full night in baby's bed, you can sleep on floor if needed</li>
                    <li><strong>Week 4:</strong> You sleep in your own bed</li>
                </ul>
                
                <h3>Method 4: Check and Console (Gentle Version)</h3>
                
                <h4>How It Works:</h4>
                <p>Similar to traditional "cry it out" but with shorter intervals and more responsive checking.</p>
                
                <h4>Gentle Check Schedule:</h4>
                <ul>
                    <li><strong>Night 1:</strong> Check after 3, then 5, then 7 minutes (repeat 7-minute intervals)</li>
                    <li><strong>Night 2:</strong> Check after 5, then 7, then 10 minutes</li>
                    <li><strong>Night 3:</strong> Check after 7, then 10, then 15 minutes</li>
                    <li><strong>Continue:</strong> Increase by 2-3 minutes each night until baby sleeps through</li>
                </ul>
                
                <h4>During Check-ins:</h4>
                <ul>
                    <li><strong>Stay 1-2 minutes maximum</strong></li>
                    <li><strong>Verbal comfort only:</strong> "You're okay, it's time to sleep"</li>
                    <li><strong>No picking up</strong> unless baby is standing and needs help lying down</li>
                    <li><strong>Stay calm and boring</strong> - you're just providing reassurance</li>
                    <li><strong>Leave even if baby is still crying</strong> - the goal is brief comfort, not stopping tears</li>
                </ul>
                
                <h3>Combining Methods for Maximum Success</h3>
                
                <h4>The Graduated Approach:</h4>
                <ol>
                    <li><strong>Weeks 1-2:</strong> Use fading to reduce current sleep props</li>
                    <li><strong>Weeks 3-4:</strong> Implement chair method or PUPD</li>
                    <li><strong>Week 5+:</strong> Switch to check and console if needed for final independence</li>
                </ol>
                
                <h4>Customizing for Your Baby:</h4>
                <ul>
                    <li><strong>Sensitive babies:</strong> Use longer fading periods, shorter check intervals</li>
                    <li><strong>Determined babies:</strong> May need quicker progression through methods</li>
                    <li><strong>Inconsistent sleepers:</strong> Focus on one method for at least 2 weeks before switching</li>
                </ul>
                
                <h3>Gentle Method Challenges & Solutions</h3>
                
                <h4>"It's Taking Too Long!"</h4>
                <ul>
                    <li><strong>Normal timeline:</strong> 2-4 weeks for full success with gentle methods</li>
                    <li><strong>Progress markers:</strong> Look for shorter crying periods, easier bedtimes, longer sleep stretches</li>
                    <li><strong>Stay consistent:</strong> Switching methods frequently delays progress</li>
                    <li><strong>Celebrate small wins:</strong> Baby putting themselves back to sleep once per night is huge progress</li>
                </ul>
                
                <h4>"Baby Gets More Upset When I Try to Comfort"</h4>
                <ul>
                    <li><strong>Over-stimulation:</strong> Your presence might be keeping baby alert</li>
                    <li><strong>Solution:</strong> Try check and console with very brief visits</li>
                    <li><strong>Alternative:</strong> Comfort from outside the room with voice only</li>
                </ul>
                
                <h4>"I Can't Handle Any Crying"</h4>
                <ul>
                    <li><strong>Remember:</strong> Some protest is normal when changing any routine</li>
                    <li><strong>Reframe:</strong> You're teaching a valuable life skill, not abandoning your baby</li>
                    <li><strong>Support system:</strong> Have partner take over if you become too stressed</li>
                    <li><strong>Self-care:</strong> Use earplugs, listen to music, or take breaks as needed</li>
                </ul>
                
                <h3>Measuring Success with Gentle Methods</h3>
                
                <h4>Week 1 Goals:</h4>
                <ul>
                    <li>Baby accepts new routine without major meltdowns</li>
                    <li>Crying decreases from 45+ minutes to 20-30 minutes</li>
                    <li>At least one night where baby sleeps 4+ hours straight</li>
                </ul>
                
                <h4>Week 2 Goals:</h4>
                <ul>
                    <li>Bedtime crying reduced to 10-15 minutes most nights</li>
                    <li>Baby occasionally puts themselves back to sleep during night wakings</li>
                    <li>Longer periods of independent sleep</li>
                </ul>
                
                <h4>Week 3-4 Goals:</h4>
                <ul>
                    <li>Minimal crying at bedtime (less than 10 minutes)</li>
                    <li>Baby sleeps through the night 3-4 times per week</li>
                    <li>When baby wakes, they often resettle within 10-15 minutes</li>
                </ul>
                
                <h4>Full Success Markers:</h4>
                <ul>
                    <li>Baby falls asleep independently within 10-15 minutes</li>
                    <li>Sleeps through the night 5+ nights per week</li>
                    <li>When wake-ups occur, baby returns to sleep without help</li>
                    <li>Naps improve as nighttime sleep consolidates</li>
                </ul>
            </div>
            
            <div class="timeline">
                <h2>Your Gentle Training Timeline:</h2>
                <h3>Commitment Required:</h3>
                <ul>
                    <li><strong>Time investment:</strong> 2-4 weeks for full success</li>
                    <li><strong>Consistency:</strong> Must follow chosen method every night</li>
                    <li><strong>Patience:</strong> Progress is gradual but lasting</li>
                    <li><strong>Support:</strong> Having a partner helps maintain consistency</li>
                </ul>
                
                <h3>Why Gentle Methods Work:</h3>
                <p>While gentle methods take longer than traditional sleep training, they build lasting 
                sleep skills while maintaining your baby's trust and security. The gradual approach 
                means less crying overall and often results in better long-term sleep habits.</p>
            </div>
        """,
        
        'module_2_readiness': """
            <h1>Sleep Training Readiness (4-6 Months)</h1>
            
            <div class="key-points">
                <h2>Is Your Baby Ready for Sleep Training?</h2>
                <p>This is the sweet spot for sleep training! Your baby is developmentally ready to learn 
                independent sleep skills while still being young enough to adapt quickly.</p>
                
                <h3>Readiness Checklist (Your Baby Should Have Most of These):</h3>
                <ul>
                    <li>✓ <strong>Age:</strong> 4-6 months old (corrected age if premature)</li>
                    <li>✓ <strong>Weight:</strong> At least 12-14 pounds</li>
                    <li>✓ <strong>Feeding:</strong> Can go 4+ hours between feeds during the day</li>
                    <li>✓ <strong>Alert time:</strong> Can stay awake for 1.5-2 hours between sleeps</li>
                    <li>✓ <strong>Self-soothing:</strong> Occasionally settles briefly on their own</li>
                    <li>✓ <strong>Physical development:</strong> Good head control, rolling one direction</li>
                    <li>✓ <strong>Health:</strong> No current illness, growth spurts, or major changes</li>
                </ul>
            </div>
            
            <h2>Pre-Training Setup (Week Before Starting):</h2>
            
            <div class="action-steps">
                <h3>Step 1: Optimize Sleep Environment</h3>
                <h4>Room Conditions:</h4>
                <ul>
                    <li><strong>Temperature:</strong> 68-70°F (baby should feel cool, not warm)</li>
                    <li><strong>Darkness:</strong> Room should be cave-dark for all sleeps (blackout curtains essential)</li>
                    <li><strong>White noise:</strong> Consistent, loud enough to mask household sounds (50-60 decibels)</li>
                    <li><strong>Air quality:</strong> Well-ventilated, consider humidifier if air is dry</li>
                </ul>
                
                <h4>Sleep Space Safety:</h4>
                <ul>
                    <li>✓ Firm mattress with fitted sheet only</li>
                    <li>✓ No loose bedding, bumpers, toys, or pillows</li>
                    <li>✓ Sleep sack or wearable blanket instead of loose blankets</li>
                    <li>✓ Crib or bassinet in good condition</li>
                </ul>
                
                <h3>Step 2: Establish Consistent Schedule</h3>
                <h4>Sample 4-6 Month Schedule:</h4>
                <ul>
                    <li><strong>6:30 AM:</strong> Wake up, feed</li>
                    <li><strong>8:00 AM:</strong> Nap 1 (1-2 hours)</li>
                    <li><strong>10:00 AM:</strong> Wake, feed, play</li>
                    <li><strong>12:30 PM:</strong> Nap 2 (1-2 hours)</li>
                    <li><strong>2:30 PM:</strong> Wake, feed, play</li>
                    <li><strong>4:30 PM:</strong> Nap 3 (30-45 minutes)</li>
                    <li><strong>5:15 PM:</strong> Wake, play</li>
                    <li><strong>6:00 PM:</strong> Feed</li>
                    <li><strong>6:30 PM:</strong> Bedtime routine</li>
                    <li><strong>7:00 PM:</strong> Bedtime</li>
                </ul>
                
                <h4>Wake Window Guidelines:</h4>
                <ul>
                    <li><strong>First wake window:</strong> 1.5-2 hours</li>
                    <li><strong>Middle wake windows:</strong> 2-2.5 hours</li>
                    <li><strong>Last wake window:</strong> 2.5-3 hours</li>
                </ul>
                
                <h3>Step 3: Perfect Your Bedtime Routine</h3>
                <h4>Ideal 20-30 Minute Routine:</h4>
                <ol>
                    <li><strong>Bath</strong> (every other night, or washcloth wipe-down)</li>
                    <li><strong>Fresh diaper and pajamas</strong></li>
                    <li><strong>Feeding</strong> (breast or bottle in dimly lit room)</li>
                    <li><strong>Burping and calming</strong> (5 minutes of gentle holding/patting)</li>
                    <li><strong>Sleep sack</strong> (if using)</li>
                    <li><strong>Brief cuddle</strong> (2-3 minutes of quiet connection)</li>
                    <li><strong>Into crib awake</strong> (drowsy but alert)</li>
                    <li><strong>"Good night"</strong> and leave room</li>
                </ol>
                
                <h4>Routine Success Tips:</h4>
                <ul>
                    <li><strong>Same order every time:</strong> Predictability helps baby prepare for sleep</li>
                    <li><strong>Calm environment:</strong> Dim lights, quiet voices, slow movements</li>
                    <li><strong>No stimulation:</strong> Avoid exciting play, bright lights, or loud sounds</li>
                    <li><strong>End routine in sleep space:</strong> Don't carry sleeping baby to crib</li>
                </ul>
                
                <h3>Step 4: Choose Your Sleep Training Method</h3>
                <h4>Method Options:</h4>
                <ul>
                    <li><strong>Extinction (CIO):</strong> Put baby down awake, don't return until morning</li>
                    <li><strong>Graduated Extinction:</strong> Check at increasing intervals</li>
                    <li><strong>Chair Method:</strong> Gradually move your presence away from crib</li>
                    <li><strong>Pick Up/Put Down:</strong> Comfort when crying, put down when calm</li>
                </ul>
                
                <h4>Choosing What's Right for You:</h4>
                <ul>
                    <li><strong>Quick results needed:</strong> Extinction or graduated extinction</li>
                    <li><strong>Prefer gradual approach:</strong> Chair method or fading</li>
                    <li><strong>Very sensitive baby:</strong> Pick up/put down or gentle fading</li>
                    <li><strong>Consistent schedule needed:</strong> Any method works with commitment</li>
                </ul>
                
                <h3>Step 5: Prepare for Success</h3>
                <h4>Partner Communication:</h4>
                <ul>
                    <li><strong>Choose method together:</strong> Both partners must be on board</li>
                    <li><strong>Assign roles:</strong> Who handles bedtime, night wakings, early mornings</li>
                    <li><strong>Set expectations:</strong> Discuss how long you'll try before adjusting</li>
                    <li><strong>Support plan:</strong> How to support each other during difficult nights</li>
                </ul>
                
                <h4>Timing Considerations:</h4>
                <ul>
                    <li><strong>Start on weekend:</strong> When you can be more flexible with schedule</li>
                    <li><strong>Clear calendar:</strong> No trips, visitors, or major events for 2 weeks</li>
                    <li><strong>Health check:</strong> Baby is well, no recent vaccines or illness</li>
                    <li><strong>Mental preparation:</strong> You feel ready and committed</li>
                </ul>
            </div>
            
            <div class="next-steps">
                <h2>What to Expect in the First Week:</h2>
                <h3>Night 1-3:</h3>
                <ul>
                    <li>Expect 30-60 minutes of crying at bedtime</li>
                    <li>May wake 2-4 times during night initially</li>
                    <li>Stay consistent with your chosen method</li>
                </ul>
                
                <h3>Night 4-7:</h3>
                <ul>
                    <li>Crying should decrease to 15-30 minutes</li>
                    <li>Longer sleep stretches emerge</li>
                    <li>Some babies sleep through by end of week 1</li>
                </ul>
                
                <h3>Signs of Success:</h3>
                <ul>
                    <li>Baby falls asleep within 20 minutes of being put down</li>
                    <li>Sleeps for 6+ hour stretches</li>
                    <li>When baby wakes, often settles back to sleep alone</li>
                    <li>More predictable wake-up time in morning</li>
                </ul>
            </div>
        """,
        
        'module_3_established': """
            <h1>Established Sleeper Problems (7-12 Months)</h1>
            
            <div class="key-points">
                <h2>Your Baby's Sleep Development:</h2>
                <p>Your baby's sleep patterns are more mature now, but new challenges emerge. This age often 
                brings sleep regressions, increased mobility, and separation anxiety that can disrupt previously 
                good sleep habits.</p>
                
                <h3>Common Issues at This Age:</h3>
                <ul>
                    <li><strong>8-10 month sleep regression:</strong> Due to major brain development</li>
                    <li><strong>Increased mobility:</strong> Rolling, sitting, standing in crib</li>
                    <li><strong>Separation anxiety:</strong> Peaks around 8-10 months</li>
                    <li><strong>Schedule transitions:</strong> Moving from 3 to 2 naps</li>
                    <li><strong>Teething disruptions:</strong> Multiple teeth coming through</li>
                </ul>
            </div>
            
            <h2>Advanced Sleep Solutions:</h2>
            
            <div class="action-steps">
                <h3>Problem 1: Standing in Crib and Can't Get Down</h3>
                <h4>Why This Happens:</h4>
                <p>Babies learn to pull to standing before they learn to sit back down. They get "stuck" 
                standing and cry for help, even though they're not in distress.</p>
                
                <h4>Solutions:</h4>
                <ul>
                    <li><strong>Daytime practice:</strong> Teach sitting down during play time</li>
                    <li><strong>Crib practice:</strong> Put baby in crib during day to practice standing/sitting</li>
                    <li><strong>Night strategy:</strong> Help them down 1-2 times, then let them figure it out</li>
                    <li><strong>Patience:</strong> Most babies master this skill within 1-2 weeks</li>
                    <li><strong>Safety first:</strong> Lower crib mattress to lowest setting</li>
                </ul>
                
                <h4>Step-by-Step Night Protocol:</h4>
                <ol>
                    <li>Go in and gently help baby sit down (don't pick up)</li>
                    <li>Say "lie down, sleep time" and leave</li>
                    <li>If baby stands again, wait 10-15 minutes before helping again</li>
                    <li>After 2-3 times, let baby work it out independently</li>
                    <li>Most babies learn to sit down within 3-5 nights</li>
                </ol>
                
                <h3>Problem 2: 8-10 Month Sleep Regression</h3>
                <h4>What's Happening:</h4>
                <p>Major brain development causes temporary sleep disruption. Your baby is processing 
                new skills like crawling, standing, and language development.</p>
                
                <h4>Regression Characteristics:</h4>
                <ul>
                    <li>Sudden onset after good sleep</li>
                    <li>Increased night wakings</li>
                    <li>Difficulty falling asleep</li>
                    <li>Shorter naps</li>
                    <li>More clinginess during day</li>
                </ul>
                
                <h4>How to Handle It:</h4>
                <ul>
                    <li><strong>Stay consistent:</strong> Don't introduce new sleep props</li>
                    <li><strong>Extra practice:</strong> More tummy time and movement during day</li>
                    <li><strong>Earlier bedtime:</strong> Temporarily move bedtime 15-30 minutes earlier</li>
                    <li><strong>Patience:</strong> Regression typically lasts 2-6 weeks</li>
                    <li><strong>Comfort minimally:</strong> Brief check-ins but don't restart old habits</li>
                </ul>
                
                <h3>Problem 3: Separation Anxiety at Bedtime</h3>
                <h4>Understanding Separation Anxiety:</h4>
                <p>Your baby now understands that you exist even when they can't see you, but doesn't 
                understand that you'll always come back. This creates anxiety at separation times.</p>
                
                <h4>Signs of Separation Anxiety:</h4>
                <ul>
                    <li>Crying when you leave the room (even briefly)</li>
                    <li>Wanting to be held constantly</li>
                    <li>Disrupted sleep after previously sleeping well</li>
                    <li>Increased clinginess during the day</li>
                </ul>
                
                <h4>Bedtime Strategies:</h4>
                <ul>
                    <li><strong>Extra connection time:</strong> 10-15 minutes of focused attention before bedtime</li>
                    <li><strong>Predictable routine:</strong> Same steps every night for security</li>
                    <li><strong>Comfort object:</strong> Introduce lovey or small stuffed animal</li>
                    <li><strong>Gradual separation:</strong> Brief practice separations during day</li>
                    <li><strong>Consistent response:</strong> Don't pick up at night, offer verbal comfort only</li>
                </ul>
                
                <h3>Problem 4: Schedule Transitions</h3>
                <h4>Moving from 3 to 2 Naps (6-9 months):</h4>
                
                <h5>Signs It's Time:</h5>
                <ul>
                    <li>Third nap becoming very short or skipped</li>
                    <li>Bedtime getting later and later</li>
                    <li>First two naps are solid (1+ hours each)</li>
                    <li>Baby can handle 3+ hour wake window</li>
                </ul>
                
                <h5>Transition Strategy:</h5>
                <ul>
                    <li><strong>Week 1:</strong> Shorten third nap to 20-30 minutes</li>
                    <li><strong>Week 2:</strong> Skip third nap every other day</li>
                    <li><strong>Week 3:</strong> Drop third nap completely</li>
                    <li><strong>Adjust bedtime:</strong> Move 30-60 minutes earlier temporarily</li>
                    <li><strong>Longer wake windows:</strong> Gradually extend to 3-3.5 hours before bed</li>
                </ul>
                
                <h4>Sample 2-Nap Schedule (8+ months):</h4>
                <ul>
                    <li><strong>6:30 AM:</strong> Wake up, feed</li>
                    <li><strong>9:30 AM:</strong> Nap 1 (1-2 hours)</li>
                    <li><strong>11:30 AM:</strong> Wake, feed, play</li>
                    <li><strong>2:30 PM:</strong> Nap 2 (1-2 hours)</li>
                    <li><strong>4:30 PM:</strong> Wake, feed, play</li>
                    <li><strong>6:00 PM:</strong> Dinner</li>
                    <li><strong>6:30 PM:</strong> Bedtime routine</li>
                    <li><strong>7:00 PM:</strong> Bedtime</li>
                </ul>
                
                <h3>Problem 5: Teething Sleep Disruption</h3>
                <h4>Real vs. Perceived Teething:</h4>
                <p>Teething is often blamed for sleep issues, but true teething pain typically lasts 
                only 2-3 days per tooth and mainly affects daytime behavior.</p>
                
                <h4>Signs of True Teething Disruption:</h4>
                <ul>
                    <li>Drooling more than usual</li>
                    <li>Chewing on everything</li>
                    <li>Slightly elevated temperature (under 101°F)</li>
                    <li>Red, swollen, or tender gums</li>
                    <li>Changes in eating patterns</li>
                </ul>
                
                <h4>Managing Teething and Sleep:</h4>
                <ul>
                    <li><strong>Pain relief:</strong> Offer appropriate pain medication before bed (consult pediatrician)</li>
                    <li><strong>Cold comfort:</strong> Frozen washcloth or teething toys during day</li>
                    <li><strong>Extra comfort:</strong> Additional cuddles during bedtime routine</li>
                    <li><strong>Maintain routine:</strong> Don't abandon sleep training progress</li>
                    <li><strong>Time limit:</strong> If sleep doesn't improve after 4-5 days, it's not teething</li>
                </ul>
                
                <h3>Problem 6: Early Morning Wakings</h3>
                <h4>Defining Early Morning Waking:</h4>
                <p>Consistently waking before 6:00 AM and unable to return to sleep.</p>
                
                <h4>Common Causes and Solutions:</h4>
                <ul>
                    <li><strong>Too late bedtime:</strong> Counter-intuitively, move bedtime earlier by 15-30 minutes</li>
                    <li><strong>Room too bright:</strong> Ensure complete darkness until desired wake time</li>
                    <li><strong>Overtired:</strong> Evaluate if naps are adequate length and timing</li>
                    <li><strong>Developmental leap:</strong> May resolve on its own in 1-2 weeks</li>
                    <li><strong>Schedule issue:</strong> May need to adjust nap timing or drop a nap</li>
                </ul>
                
                <h4>Early Morning Protocol:</h4>
                <ol>
                    <li>Don't respond immediately - wait 10-15 minutes</li>
                    <li>If baby doesn't resettle, offer brief verbal comfort but don't pick up</li>
                    <li>Keep room dark and boring until desired wake time</li>
                    <li>Don't start the day before 6:00 AM</li>
                    <li>If baby falls back asleep, let them sleep until normal wake time</li>
                </ol>
            </div>
            
            <div class="next-steps">
                <h2>Maintaining Good Sleep Habits:</h2>
                <h3>Consistency is Key:</h3>
                <ul>
                    <li>Stick to established bedtime routine</li>
                    <li>Maintain age-appropriate schedule</li>
                    <li>Don't introduce new sleep props during difficult phases</li>
                    <li>Remember that some sleep disruption is normal during development</li>
                </ul>
                
                <h3>When to Seek Help:</h3>
                <ul>
                    <li>Sleep problems persist for more than 3-4 weeks</li>
                    <li>Baby seems unwell or in pain</li>
                    <li>Significant changes in appetite or behavior</li>
                    <li>Multiple wake-ups every night for several weeks</li>
                </ul>
            </div>
        """,
        
        'module_4_toddler': """
            <h1>Toddler Sleep Transitions (12-24 Months)</h1>
            
            <div class="key-points">
                <h2>Toddler Sleep Challenges:</h2>
                <p>Your toddler's sleep needs are changing dramatically. They're developing independence, 
                language, and strong opinions about everything - including sleep!</p>
                
                <h3>Unique Toddler Factors:</h3>
                <ul>
                    <li><strong>Cognitive development:</strong> Understanding cause and effect, testing boundaries</li>
                    <li><strong>Language explosion:</strong> Learning new words daily affects sleep</li>
                    <li><strong>Physical development:</strong> Climbing, running, increased mobility</li>
                    <li><strong>Emotional development:</strong> Big feelings, tantrums, assertion of independence</li>
                    <li><strong>Schedule transitions:</strong> Moving from 2 naps to 1 nap</li>
                </ul>
            </div>
            
            <h2>Major Toddler Sleep Solutions:</h2>
            
            <div class="action-steps">
                <h3>Transition 1: Moving to One Nap (12-18 months)</h3>
                
                <h4>Signs Your Toddler is Ready:</h4>
                <ul>
                    <li>Consistently fighting one of the two naps</li>
                    <li>Taking longer to fall asleep at bedtime</li>
                    <li>Bedtime moving later and later</li>
                    <li>Can stay awake comfortably for 5+ hours</li>
                    <li>When they do take both naps, one is very short</li>
                </ul>
                
                <h4>Gradual Transition Method (2-3 weeks):</h4>
                <h5>Week 1: Push Morning Nap Later</h5>
                <ul>
                    <li>Move morning nap 15 minutes later every 2-3 days</li>
                    <li>Keep afternoon nap at normal time</li>
                    <li>If toddler gets too tired, allow short 20-minute afternoon nap</li>
                    <li>Move bedtime 30 minutes earlier temporarily</li>
                </ul>
                
                <h5>Week 2: Merge Naps</h5>
                <ul>
                    <li>Aim for one nap starting between 12:00-1:00 PM</li>
                    <li>Allow 2-3 hour nap (longer than previous naps)</li>
                    <li>If toddler seems overtired, alternate days with 2 naps</li>
                    <li>Maintain earlier bedtime</li>
                </ul>
                
                <h5>Week 3: Establish New Routine</h5>
                <ul>
                    <li>Consistent one nap at same time daily</li>
                    <li>Gradual return to normal bedtime</li>
                    <li>Watch for signs of overtiredness</li>
                </ul>
                
                <h4>Sample One-Nap Schedule:</h4>
                <ul>
                    <li><strong>6:30 AM:</strong> Wake up</li>
                    <li><strong>7:00 AM:</strong> Breakfast</li>
                    <li><strong>9:00 AM:</strong> Snack, active play</li>
                    <li><strong>11:30 AM:</strong> Lunch</li>
                    <li><strong>12:30 PM:</strong> Nap (2-3 hours)</li>
                    <li><strong>3:30 PM:</strong> Wake, snack</li>
                    <li><strong>5:30 PM:</strong> Dinner</li>
                    <li><strong>6:30 PM:</strong> Bedtime routine</li>
                    <li><strong>7:30 PM:</strong> Bedtime</li>
                </ul>
                
                <h3>Challenge 2: Climbing Out of Crib</h3>
                
                <h4>Safety First Approach:</h4>
                <ul>
                    <li><strong>Lower mattress:</strong> To lowest possible setting</li>
                    <li><strong>Remove climbing aids:</strong> No bumpers, large stuffed animals, or blankets</li>
                    <li><strong>Sleep sack:</strong> Makes climbing more difficult</li>
                    <li><strong>Room safety:</strong> Childproof entire room in case they get out</li>
                </ul>
                
                <h4>Behavioral Strategies:</h4>
                <ul>
                    <li><strong>Immediate return:</strong> Walk toddler back to crib without talking or eye contact</li>
                    <li><strong>Consistent response:</strong> Same reaction every single time</li>
                    <li><strong>Boring consequences:</strong> No attention, interaction, or entertainment</li>
                    <li><strong>Patience:</strong> May take 20-50 returns the first few nights</li>
                </ul>
                
                <h4>When to Consider Toddler Bed:</h4>
                <ul>
                    <li>Consistently climbing out despite safety measures</li>
                    <li>Child is over 35 inches tall</li>
                    <li>Potty training has begun</li>
                    <li>New baby needs the crib</li>
                </ul>
                
                <h3>Challenge 3: Transitioning to Toddler Bed</h3>
                
                <h4>Preparing for the Transition:</h4>
                <ul>
                    <li><strong>Timing:</strong> Avoid major changes (new baby, moving, etc.)</li>
                    <li><strong>Room setup:</strong> Toddler-proof entire room thoroughly</li>
                    <li><strong>Safety gate:</strong> Consider gate at bedroom door</li>
                    <li><strong>Involve toddler:</strong> Let them help choose bedding or arrange room</li>
                </ul>
                
                <h4>First Week Strategy:</h4>
                <ul>
                    <li><strong>Same routine:</strong> Keep bedtime routine identical</li>
                    <li><strong>Clear expectations:</strong> "Stay in bed until morning"</li>
                    <li><strong>Immediate returns:</strong> Walk back to bed silently every time they get up</li>
                    <li><strong>Morning reward:</strong> Praise for staying in bed</li>
                    <li><strong>Patience:</strong> May take 1-2 weeks to adjust</li>
                </ul>
                
                <h4>Toddler Bed Rules:</h4>
                <ol>
                    <li>"Stay in your bed until the sun comes up" (or wake-up light)</li>
                    <li>"Call for Mommy/Daddy if you need help"</li>
                    <li>"Bedtime means lying down and closing eyes"</li>
                </ol>
                
                <h3>Challenge 4: Bedtime Battles and Stalling</h3>
                
                <h4>Understanding Toddler Stalling:</h4>
                <p>Toddlers are masters at delaying bedtime. They've learned that certain requests 
                will get them out of bed and extend their time with you.</p>
                
                <h4>Common Stalling Tactics:</h4>
                <ul>
                    <li>"I need water"</li>
                    <li>"I have to go potty"</li>
                    <li>"One more book"</li>
                    <li>"I'm scared"</li>
                    <li>"My tummy hurts"</li>
                </ul>
                
                <h4>Preventing Bedtime Battles:</h4>
                <h5>Proactive Routine:</h5>
                <ul>
                    <li><strong>Address needs first:</strong> Potty, water, snacks before bedtime routine</li>
                    <li><strong>Set expectations:</strong> "After three books, it's time for sleep"</li>
                    <li><strong>Choices within limits:</strong> "Do you want to brush teeth first or put on pajamas?"</li>
                    <li><strong>Wind-down time:</strong> 30 minutes of calm activities before bed</li>
                </ul>
                
                <h5>During Routine:</h5>
                <ul>
                    <li><strong>Consistent timing:</strong> Same time every night</li>
                    <li><strong>Clear beginning and end:</strong> "Bedtime routine is starting now"</li>
                    <li><strong>No negotiations:</strong> Routine is non-negotiable</li>
                    <li><strong>Connection time:</strong> Focus fully on toddler during routine</li>
                </ul>
                
                <h4>Responding to Post-Bedtime Requests:</h4>
                <ul>
                    <li><strong>First request:</strong> Address if reasonable (water, potty)</li>
                    <li><strong>Subsequent requests:</strong> "You already had water. Time for sleep."</li>
                    <li><strong>Stay boring:</strong> No extra stories, songs, or conversations</li>
                    <li><strong>Be brief:</strong> In and out in under 30 seconds</li>
                </ul>
                
                <h3>Challenge 5: Night Wakings and Fear</h3>
                
                <h4>Developmental Night Wakings:</h4>
                <p>Toddlers experience vivid dreams and separation anxiety that can cause night wakings 
                even after previously sleeping through the night.</p>
                
                <h4>Addressing Night Fears:</h4>
                <ul>
                    <li><strong>Acknowledge feelings:</strong> "You feel scared. You are safe in your bed."</li>
                    <li><strong>Comfort object:</strong> Special stuffed animal or blanket</li>
                    <li><strong>Night light:</strong> Dim, warm light for comfort</li>
                    <li><strong>Monster spray:</strong> Water bottle to "spray away" monsters</li>
                    <li><strong>Stay brief:</strong> 2-3 minutes of comfort, then leave</li>
                </ul>
                
                <h4>Night Waking Protocol:</h4>
                <ol>
                    <li>Wait 3-5 minutes to see if toddler settles alone</li>
                    <li>If crying continues, go in briefly</li>
                    <li>Offer quick comfort without picking up</li>
                    <li>Remind of bedtime rules</li>
                    <li>Leave room</li>
                    <li>If calling out continues, wait longer before returning</li>
                </ol>
                
                <h3>Challenge 6: Early Morning Wakings</h3>
                
                <h4>Toddler-Specific Causes:</h4>
                <ul>
                    <li><strong>Excitement about the day:</strong> Toddlers are eager to start playing</li>
                    <li><strong>Light sensitivity:</strong> Even small amounts of light can wake them</li>
                    <li><strong>Schedule needs adjustment:</strong> Nap too late or bedtime too early</li>
                    <li><strong>Learned behavior:</strong> Getting attention for early waking</li>
                </ul>
                
                <h4>Solutions:</h4>
                <ul>
                    <li><strong>OK-to-wake clock:</strong> Visual cue for when to get up</li>
                    <li><strong>Room environment:</strong> Complete darkness until wake time</li>
                    <li><strong>Delayed response:</strong> Don't go in immediately when toddler wakes</li>
                    <li><strong>Consistent wake time:</strong> Same time every day, even if they wake earlier</li>
                    <li><strong>Special activity:</strong> Something exciting that only happens after appropriate wake time</li>
                </ul>
            </div>
            
            <div class="next-steps">
                <h2>Toddler Sleep Success Strategies:</h2>
                <h3>Key Principles:</h3>
                <ul>
                    <li><strong>Consistency:</strong> Same rules and responses every time</li>
                    <li><strong>Patience:</strong> Toddler changes take longer than baby changes</li>
                    <li><strong>Connection:</strong> Fulfill need for attention during appropriate times</li>
                    <li><strong>Clear boundaries:</strong> Toddlers feel secure with predictable limits</li>
                </ul>
                
                <h3>Remember:</h3>
                <p>Toddler sleep challenges are temporary phases in development. Maintaining consistent 
                boundaries while showing empathy for their big feelings will help them develop healthy 
                sleep habits that last into childhood.</p>
            </div>
        """,
        
        'module_5_cio': """
            <h1>Cry It Out Method (Extinction Sleep Training)</h1>
            
            <div class="key-points">
                <h2>Understanding Cry It Out:</h2>
                <p>The extinction method, commonly called "cry it out" (CIO), involves putting your baby 
                down awake and not returning until the next feeding or morning. It's the fastest method 
                for teaching independent sleep skills.</p>
                
                <h3>Perfect for You If:</h3>
                <ul>
                    <li>You want the quickest results possible (usually 3-7 nights)</li>
                    <li>You can handle some crying without it causing you severe distress</li>
                    <li>You need predictable results due to work/schedule constraints</li>
                    <li>Previous gentler methods haven't worked</li>
                    <li>Your baby is healthy and over 4-6 months old</li>
                </ul>
                
                <h3>Not Recommended If:</h3>
                <ul>
                    <li>Baby is under 4 months old</li>
                    <li>Significant health issues or feeding concerns</li>
                    <li>Major life changes happening (moving, new job, etc.)</li>
                    <li>You feel extremely anxious about baby crying</li>
                    <li>Partner is not supportive of the method</li>
                </ul>
            </div>
            
            <h2>Complete CIO Implementation Guide:</h2>
            
            <div class="action-steps">
                <h3>Pre-CIO Preparation (1 Week Before):</h3>
                
                <h4>Perfect the Bedtime Routine:</h4>
                <ul>
                    <li><strong>Consistent timing:</strong> Same time every night (±15 minutes)</li>
                    <li><strong>Optimal length:</strong> 20-30 minutes total</li>
                    <li><strong>Calming activities:</strong> Bath, feeding, books, gentle holding</li>
                    <li><strong>End in sleep space:</strong> Last steps happen in nursery</li>
                    <li><strong>Practice putting down awake:</strong> Even if you pick back up</li>
                </ul>
                
                <h4>Optimize Sleep Environment:</h4>
                <ul>
                    <li><strong>Room temperature:</strong> 68-70°F</li>
                    <li><strong>Complete darkness:</strong> No nightlights, blackout curtains essential</li>
                    <li><strong>White noise:</strong> Consistent, loud enough to mask household sounds</li>
                    <li><strong>Safe sleep space:</strong> Crib with fitted sheet only</li>
                    <li><strong>Comfort items:</strong> Sleep sack, small lovey (if over 6 months)</li>
                </ul>
                
                <h4>Schedule Optimization:</h4>
                <ul>
                    <li><strong>Age-appropriate wake windows:</strong> Not overtired at bedtime</li>
                    <li><strong>Consistent nap times:</strong> Predictable day schedule</li>
                    <li><strong>Last feeding:</strong> 30+ minutes before sleep to break feed-sleep association</li>
                    <li><strong>Activity level:</strong> Adequate physical and mental stimulation during day</li>
                </ul>
                
                <h3>The CIO Method: Night-by-Night Guide</h3>
                
                <h4>Night 1: The Foundation</h4>
                <h5>Bedtime Routine:</h5>
                <ol>
                    <li>Complete your established bedtime routine</li>
                    <li>Put baby in crib awake (drowsy is fine, but eyes should be open)</li>
                    <li>Say your goodnight phrase ("Good night, I love you, time to sleep")</li>
                    <li>Leave the room and close the door</li>
                    <li>Do not return until morning or scheduled night feeding</li>
                </ol>
                
                <h5>What to Expect:</h5>
                <ul>
                    <li><strong>Crying duration:</strong> 30-90 minutes is normal for first night</li>
                    <li><strong>Crying intensity:</strong> May escalate before it decreases</li>
                    <li><strong>Your feelings:</strong> Anxiety, doubt, and stress are normal</li>
                    <li><strong>Sleep result:</strong> Baby will eventually fall asleep</li>
                </ul>
                
                <h5>During the Crying:</h5>
                <ul>
                    <li><strong>Stay out:</strong> Do not go back in the room</li>
                    <li><strong>Monitor safely:</strong> Use baby monitor to ensure safety</li>
                    <li><strong>Self-care:</strong> Put on headphones, take a shower, call a friend</li>
                    <li><strong>Trust the process:</strong> Your baby is learning a new skill</li>
                </ul>
                
                <h4>Night 2-3: Building Progress</h4>
                <h5>Expectations:</h5>
                <ul>
                    <li><strong>Reduced crying:</strong> Usually 15-45 minutes</li>
                    <li><strong>Possible extinction burst:</strong> Night 2 might be worse before getting better</li>
                    <li><strong>Faster falling asleep:</strong> Process speeds up</li>
                    <li><strong>Night wakings:</strong> May still occur but should be shorter</li>
                </ul>
                
                <h4>Night 4-7: Establishing Success</h4>
                <h5>Expected Progress:</h5>
                <ul>
                    <li><strong>Minimal crying:</strong> 5-15 minutes or less</li>
                    <li><strong>Self-soothing:</strong> Baby falls asleep independently</li>
                    <li><strong>Longer sleep stretches:</strong> Fewer night wakings</li>
                    <li><strong>Confidence:</strong> Baby adapts to new routine</li>
                </ul>
                
                <h3>Handling Night Wakings with CIO:</h3>
                
                <h4>Before Midnight Wakings:</h4>
                <ul>
                    <li><strong>Usually not hunger:</strong> If bedtime was recent, likely need to practice sleep skills</li>
                    <li><strong>Apply same rules:</strong> Do not go in unless scheduled feeding time</li>
                    <li><strong>Expect protest:</strong> Baby may cry for 20-60 minutes initially</li>
                    <li><strong>Stay consistent:</strong> This teaches sleep skills for all sleep periods</li>
                </ul>
                
                <h4>Middle-of-Night Wakings:</h4>
                <ul>
                    <li><strong>Assess timing:</strong> Is it close to a scheduled feeding?</li>
                    <li><strong>Age considerations:</strong> Babies under 6 months may need 1-2 night feeds</li>
                    <li><strong>If not feeding time:</strong> Apply same CIO principles</li>
                    <li><strong>Gradual elimination:</strong> Night feeds will naturally reduce as sleep improves</li>
                </ul>
                
                <h4>Early Morning Wakings:</h4>
                <ul>
                    <li><strong>Define "morning":</strong> Nothing before 6:00 AM is morning</li>
                    <li><strong>Wait it out:</strong> Many babies will return to sleep</li>
                    <li><strong>Room environment:</strong> Keep dark and boring until desired wake time</li>
                    <li><strong>Consistency:</strong> Don't start the day early even if baby is awake</li>
                </ul>
                
                <h3>CIO for Naps:</h3>
                
                <h4>When to Start Nap Training:</h4>
                <ul>
                    <li><strong>After night success:</strong> Wait until nights are going well (3-5 days)</li>
                    <li><strong>One nap at a time:</strong> Start with most consistent nap</li>
                    <li><strong>Different timeline:</strong> Naps often take longer to improve than nights</li>
                </ul>
                
                <h4>Nap CIO Protocol:</h4>
                <ol>
                    <li>Complete short, calm pre-nap routine</li>
                    <li>Put baby down awake in sleep space</li>
                    <li>Leave room and set timer for 60 minutes</li>
                    <li>If baby hasn't slept after 60 minutes, get them up</li>
                    <li>Try again at next scheduled nap time</li>
                    <li>Don't compensate with earlier bedtime unless baby is truly overtired</li>
                </ol>
                
                <h3>Troubleshooting Common CIO Challenges:</h3>
                
                <h4>"The Crying is Getting Worse, Not Better"</h4>
                <ul>
                    <li><strong>Extinction burst:</strong> Temporary increase in crying is normal around night 2-3</li>
                    <li><strong>Stay consistent:</strong> Going in will restart the process</li>
                    <li><strong>Check basics:</strong> Ensure baby isn't overtired, sick, or uncomfortable</li>
                    <li><strong>Timeline:</strong> Give it 5-7 full nights before evaluating effectiveness</li>
                </ul>
                
                <h4>"Baby Stands Up and Won't Lie Down"</h4>
                <ul>
                    <li><strong>New skill practice:</strong> Normal for babies learning to stand</li>
                    <li><strong>Don't intervene:</strong> Baby will figure out how to lie down</li>
                    <li><strong>Daytime practice:</strong> Help baby practice sitting down during play</li>
                    <li><strong>Patience:</strong> Usually resolves within a few nights</li>
                </ul>
                
                <h4>"I'm Too Stressed to Continue"</h4>
                <ul>
                    <li><strong>Partner support:</strong> Have partner handle bedtime if possible</li>
                    <li><strong>Leave the house:</strong> Go for a walk during bedtime</li>
                    <li><strong>Reminder of goals:</strong> Focus on long-term sleep health</li>
                    <li><strong>Professional support:</strong> Consult pediatrician if needed</li>
                </ul>
                
                <h4>"Baby Gets Sick During CIO"</h4>
                <ul>
                    <li><strong>Pause training:</strong> Comfort sick baby as needed</li>
                    <li><strong>Wait for recovery:</strong> Resume after baby is completely well</li>
                    <li><strong>Expect some regression:</strong> May need to restart process</li>
                    <li><strong>Shorter timeline:</strong> Second time usually goes faster</li>
                </ul>
                
                <h3>Measuring CIO Success:</h3>
                
                <h4>Night 1-3 Goals:</h4>
                <ul>
                    <li>Baby eventually falls asleep independently</li>
                    <li>Crying duration decreases each night</li>
                    <li>You maintain consistency without going in</li>
                </ul>
                
                <h4>End of Week 1 Goals:</h4>
                <ul>
                    <li>Baby falls asleep within 15 minutes</li>
                    <li>Sleeps for 6+ hour stretches</li>
                    <li>Night wakings are brief and self-resolved</li>
                    <li>Family is getting better rest</li>
                </ul>
                
                <h4>Long-term Success Markers:</h4>
                <ul>
                    <li>Bedtime is calm and predictable</li>
                    <li>Baby sleeps through the night consistently</li>
                    <li>Naps improve and become more predictable</li>
                    <li>Everyone in family is well-rested</li>
                </ul>
            </div>
            
            <div class="timeline">
                <h2>Why CIO Works:</h2>
                <h3>The Science:</h3>
                <ul>
                    <li><strong>Extinction learning:</strong> Behavior that isn't reinforced eventually stops</li>
                    <li><strong>Self-soothing development:</strong> Baby learns internal regulation skills</li>
                    <li><strong>Sleep pressure:</strong> Natural tiredness helps baby fall asleep</li>
                    <li><strong>Habit formation:</strong> New sleep associations develop quickly</li>
                </ul>
                
                <h3>Long-term Benefits:</h3>
                <ul>
                    <li><strong>Independent sleep skills:</strong> Baby can sleep anywhere, anytime</li>
                    <li><strong>Better night sleep:</strong> Longer, more restorative sleep</li>
                    <li><strong>Improved naps:</strong> Better daytime sleep follows night success</li>
                    <li><strong>Family well-being:</strong> Everyone gets the rest they need</li>
                    <li><strong>Confidence:</strong> Baby feels secure in their sleep abilities</li>
                </ul>
                
                <h3>Addressing Concerns:</h3>
                <p><strong>Will this harm my baby?</strong> Research shows that sleep training, including CIO, 
                does not cause emotional or developmental harm when done with healthy babies over 4-6 months. 
                In fact, better sleep supports optimal brain development and emotional regulation.</p>
                
                <p><strong>Will this damage our relationship?</strong> Teaching independent sleep skills 
                actually supports a secure attachment by ensuring both baby and parents are well-rested 
                and emotionally available during awake times.</p>
            </div>
        """,
        
        'module_7_feeding': """
            <h1>Breaking Feed-to-Sleep Associations</h1>
            
            <div class="key-points">
                <h2>Understanding Feed-to-Sleep Associations:</h2>
                <p>Feeding your baby to sleep is one of the most common and natural ways babies fall asleep. 
                However, when babies rely solely on feeding to fall asleep, they often can't return to sleep 
                during normal night wakings without being fed again.</p>
                
                <h3>Signs of Feed-to-Sleep Dependency:</h3>
                <ul>
                    <li>Baby always falls asleep while feeding</li>
                    <li>Frequent night wakings (every 1-3 hours) even when not hungry</li>
                    <li>Very short feeds during night wakings</li>
                    <li>Baby won't take bottles/breast unless drowsy or asleep</li>
                    <li>Naps are very short unless baby is held while feeding</li>
                    <li>Bedtime requires feeding even if baby just ate</li>
                </ul>
                
                <h3>Why Breaking This Association Helps:</h3>
                <ul>
                    <li><strong>Longer sleep stretches:</strong> Baby can sleep through light sleep cycles</li>
                    <li><strong>Better nutrition:</strong> More efficient, focused feeds when awake</li>
                    <li><strong>Flexibility:</strong> Other caregivers can put baby to sleep</li>
                    <li><strong>Self-regulation:</strong> Baby learns other ways to comfort themselves</li>
                </ul>
            </div>
            
            <h2>Complete Feed-to-Sleep Breaking System:</h2>
            
            <div class="action-steps">
                <h3>Method 1: Gradual Separation (2-3 weeks)</h3>
                
                <h4>Week 1: Feed Until Drowsy, Not Asleep</h4>
                <h5>Bedtime Strategy:</h5>
                <ol>
                    <li>Start bedtime routine as normal</li>
                    <li>Begin feeding in usual location</li>
                    <li>When baby's sucking slows and eyes get heavy, gently break the latch/remove bottle</li>
                    <li>Hold baby upright for 1-2 minutes (helps wake them slightly)</li>
                    <li>Put baby down in crib while drowsy but awake</li>
                    <li>If baby cries, try gentle patting or picking up briefly before putting back down</li>
                </ol>
                
                <h5>What to Expect:</h5>
                <ul>
                    <li>Baby may protest initially when feeding stops</li>
                    <li>May take 15-30 minutes to fall asleep first few nights</li>
                    <li>Some babies adapt quickly, others need more time</li>
                    <li>Stay consistent - don't go back to feeding to sleep</li>
                </ul>
                
                <h4>Week 2: Move Feeding Earlier in Routine</h4>
                <h5>New Routine Order:</h5>
                <ol>
                    <li>Bath time</li>
                    <li>Fresh diaper and pajamas</li>
                    <li>Feeding (in well-lit, less cozy environment)</li>
                    <li>Burping and brief upright time</li>
                    <li>Story time or quiet song</li>
                    <li>Into crib awake</li>
                </ol>
                
                <h5>Key Changes:</h5>
                <ul>
                    <li><strong>Environment during feed:</strong> Brighter lights, less cozy positioning</li>
                    <li><strong>Keep baby alert:</strong> Talk softly, stroke feet, change positions if getting sleepy</li>
                    <li><strong>Buffer activities:</strong> Add 5-10 minutes between feed and sleep</li>
                    <li><strong>Gradual timing:</strong> Move feeding 5 minutes earlier every few days</li>
                </ul>
                
                <h4>Week 3: Complete Separation</h4>
                <h5>Final Routine:</h5>
                <ul>
                    <li><strong>30-45 minutes before bed:</strong> Final feeding in living room or other non-sleep space</li>
                    <li><strong>Regular routine:</strong> Bath, pajamas, books, brief cuddle</li>
                    <li><strong>Independent sleep:</strong> Baby goes down completely awake</li>
                    <li><strong>No backup feeding:</strong> If baby cries, use other comfort methods</li>
                </ul>
                
                <h3>Method 2: Cold Turkey Approach (5-7 days)</h3>
                
                <h4>When to Use This Method:</h4>
                <ul>
                    <li>Baby is over 6 months old</li>
                    <li>Gradual approach hasn't been successful</li>
                    <li>You need faster results</li>
                    <li>Baby doesn't seem to respond to partial changes</li>
                </ul>
                
                <h4>Implementation:</h4>
                <ol>
                    <li><strong>Night 1:</strong> Complete normal bedtime routine but end feeding 15-20 minutes before putting baby down</li>
                    <li><strong>After feeding:</strong> Include calming activities like books, gentle rocking, or quiet songs</li>
                    <li><strong>Put down awake:</strong> Baby should be alert but calm when placed in crib</li>
                    <li><strong>No middle-of-night feeding:</strong> Unless it's a scheduled feeding time for baby's age</li>
                    <li><strong>Stay consistent:</strong> Don't revert to feeding to sleep even if baby protests</li>
                </ol>
                
                <h4>Supporting Baby Through the Change:</h4>
                <ul>
                    <li><strong>Extra comfort during routine:</strong> More cuddling, longer books, gentle massage</li>
                    <li><strong>New sleep associations:</strong> White noise, lovey, pacifier (if using)</li>
                    <li><strong>Patience with crying:</strong> Baby is learning new skills</li>
                    <li><strong>Consistent response:</strong> Use same comfort method each time</li>
                </ul>
                
                <h3>Handling Night Wakings During Transition:</h3>
                
                <h4>Distinguishing Hunger from Habit:</h4>
                <h5>Signs of True Hunger:</h5>
                <ul>
                    <li>Full, efficient feeding (10+ minutes)</li>
                    <li>Baby settles completely after feeding</li>
                    <li>Waking is at predictable times (every 4+ hours)</li>
                    <li>Baby under 6 months or still gaining weight rapidly</li>
                </ul>
                
                <h5>Signs of Habitual Waking:</h5>
                <ul>
                    <li>Very short feeds (2-5 minutes)</li>
                    <li>Falls asleep immediately when latched</li>
                    <li>Frequent wakings (every 1-2 hours)</li>
                    <li>Baby over 6 months with good weight gain</li>
                </ul>
                
                <h4>Night Weaning Strategy:</h4>
                <h5>For Babies 4-6 Months:</h5>
                <ul>
                    <li><strong>Maintain 1-2 night feeds:</strong> Usually around 11-12pm and 3-4am</li>
                    <li><strong>Gradually space feeds:</strong> Don't feed closer than 3-4 hours apart</li>
                    <li><strong>Comfort other wakings:</strong> Use patting, shushing, or brief pickup/putdown</li>
                    <li><strong>Full feeds only:</strong> If baby doesn't take a full feed, try comfort first</li>
                </ul>
                
                <h5>For Babies 6+ Months:</h5>
                <ul>
                    <li><strong>Eliminate night feeds:</strong> Most babies this age can sleep 11-12 hours without eating</li>
                    <li><strong>Gradually reduce:</strong> Shorten feeds by 2-3 minutes every few nights</li>
                    <li><strong>Replace with comfort:</strong> Use other soothing methods for all wakings</li>
                    <li><strong>Increase day feeds:</strong> Ensure adequate nutrition during awake hours</li>
                </ul>
                
                <h3>Special Considerations for Breastfeeding:</h3>
                
                <h4>Managing Your Milk Supply:</h4>
                <ul>
                    <li><strong>Gradual reduction:</strong> Slowly eliminate night feeds to prevent discomfort</li>
                    <li><strong>Pump if needed:</strong> Brief pumping for comfort, but don't maintain full supply</li>
                    <li><strong>Increase day feeds:</strong> More frequent or longer feeds during day</li>
                    <li><strong>Stay hydrated:</strong> Maintain good nutrition and fluid intake</li>
                </ul>
                
                <h4>Comfort vs. Nutrition:</h4>
                <ul>
                    <li><strong>Pacifier introduction:</strong> Can provide sucking comfort without feeding</li>
                    <li><strong>Other comfort measures:</strong> Rocking, patting, singing, white noise</li>
                    <li><strong>Partner involvement:</strong> Have partner handle some night wakings</li>
                    <li><strong>Timing of change:</strong> Avoid during growth spurts or illness</li>
                </ul>
                
                <h3>Troubleshooting Common Challenges:</h3>
                
                <h4>"Baby Won't Take Full Feeds When Awake"</h4>
                <ul>
                    <li><strong>Environmental changes:</strong> Feed in brighter, less cozy space</li>
                    <li><strong>Increase gaps:</strong> Space feeds further apart to build appetite</li>
                    <li><strong>Stay alert techniques:</strong> Talk, stroke baby, change positions during feed</li>
                    <li><strong>Be patient:</strong> May take several days for baby to adjust</li>
                </ul>
                
                <h4>"Baby Wakes Up as Soon as I Put Them Down"</h4>
                <ul>
                    <li><strong>Ensure truly awake:</strong> Baby should have open eyes when put down</li>
                    <li><strong>Gradual transition:</strong> Hold for progressively shorter times before putting down</li>
                    <li><strong>Warm the sleep surface:</strong> Use heating pad on crib, remove before placing baby</li>
                    <li><strong>Keep hand on chest:</strong> Maintain contact for 30-60 seconds after putting down</li>
                </ul>
                
                <h4>"Night Wakings Have Increased"</h4>
                <ul>
                    <li><strong>Normal initially:</strong> Temporary increase in night wakings is common</li>
                    <li><strong>Stay consistent:</strong> Don't revert to feeding during transition</li>
                    <li><strong>Alternative comfort:</strong> Use other methods to help baby return to sleep</li>
                    <li><strong>Timeline:</strong> Usually improves within 5-7 days of consistency</li>
                </ul>
                
                <h4>"I Miss the Bonding Time"</h4>
                <ul>
                    <li><strong>Create new bonding:</strong> Special cuddle time after feeds</li>
                    <li><strong>Daytime connection:</strong> Extra skin-to-skin during awake hours</li>
                    <li><strong>Feeding focus:</strong> More attentive, interactive feeds when baby is alert</li>
                    <li><strong>Quality over quantity:</strong> Better rested parents are more emotionally available</li>
                </ul>
                
                <h3>Maintaining Success:</h3>
                
                <h4>Preventing Regression:</h4>
                <ul>
                    <li><strong>Consistent routine:</strong> Keep feeding separate from sleep permanently</li>
                    <li><strong>Illness protocol:</strong> Brief comfort feeds during sickness, but return to routine when well</li>
                    <li><strong>Travel preparation:</strong> Maintain feeding-sleep separation even in new environments</li>
                    <li><strong>Growth spurts:</strong> Increase day feeds rather than reinstating night feeds</li>
                </ul>
                
                <h4>Long-term Benefits:</h4>
                <ul>
                    <li><strong>Better sleep quality:</strong> Longer, more restorative sleep periods</li>
                    <li><strong>Improved nutrition:</strong> More efficient, focused feeds</li>
                    <li><strong>Flexibility:</strong> Anyone can put baby to sleep</li>
                    <li><strong>Self-regulation:</strong> Baby develops multiple self-soothing strategies</li>
                    <li><strong>Family well-being:</strong> Parents get better rest and more freedom</li>
                </ul>
            </div>
            
            <div class="timeline">
                <h2>Expected Timeline for Breaking Feed-to-Sleep:</h2>
                <h3>Gradual Method:</h3>
                <ul>
                    <li><strong>Week 1:</strong> Some protest, but baby adapts to being put down drowsy</li>
                    <li><strong>Week 2:</strong> Easier bedtimes, baby accepts routine changes</li>
                    <li><strong>Week 3:</strong> Independent sleep skills established</li>
                </ul>
                
                <h3>Cold Turkey Method:</h3>
                <ul>
                    <li><strong>Days 1-3:</strong> Increased crying, frequent night wakings</li>
                    <li><strong>Days 4-5:</strong> Noticeable improvement in sleep stretches</li>
                    <li><strong>Days 6-7:</strong> New routine established, better sleep for all</li>
                </ul>
                
                <h3>Success Indicators:</h3>
                <ul>
                    <li>Baby falls asleep independently at bedtime</li>
                    <li>Night wakings are less frequent and shorter</li>
                    <li>Feeds are more efficient and focused</li>
                    <li>Baby can be put to sleep by other caregivers</li>
                    <li>Overall family sleep quality improves</li>
                </ul>
            </div>
        """,
        
        'module_8_room_sharing': """
            <h1>Room Sharing Solutions</h1>
            
            <div class="key-points">
                <h2>Your Room Sharing Situation:</h2>
                <ul>
                    <li>Room sharing is safe and recommended until 6-12 months</li>
                    <li>Common challenges: mutual wake-ups, space constraints</li>
                    <li>Solutions focus on creating separate sleep zones</li>
                </ul>
            </div>
            
            <h2>Creating Sleep Zones:</h2>
            
            <div class="action-steps">
                <h3>Physical Separation</h3>
                <ul>
                    <li>Use room divider or curtain between beds</li>
                    <li>Position baby's crib away from your bed</li>
                    <li>Consider white noise machine between you</li>
                    <li>Use separate lighting sources</li>
                </ul>
                
                <h3>Sound Management</h3>
                <ul>
                    <li>White noise for baby (and optionally for you)</li>
                    <li>Use earplugs during partner's turn with baby</li>
                    <li>Learn to differentiate cries from sleep sounds</li>
                    <li>Wait 5-10 minutes before responding to noises</li>
                </ul>
                
                <h3>Schedule Coordination</h3>
                <ul>
                    <li>Stagger bedtimes if needed</li>
                    <li>Use dim red lighting for night feeds</li>
                    <li>Have baby sleeping before your bedtime</li>
                    <li>Consider temporary separate sleeping during training</li>
                </ul>
            </div>
            
            <div class="pro-tips">
                <h2>Pro Tips for Room Sharing:</h2>
                <ul>
                    <li>Baby doesn't need to move out to sleep train</li>
                    <li>You may sleep better with some distance</li>
                    <li>Consider a video monitor even in same room</li>
                    <li>Room sharing can continue as long as it works for everyone</li>
                </ul>
            </div>
        """
    }
    
    return summaries.get(module_name, f'<h1>{module_name}</h1><p>Summary content for this module.</p>')

def get_pdf_styles():
    """
    Clean, professional CSS styles for PDF
    """
    return """
    @page {
        size: A4;
        margin: 2cm;
        @bottom-center {
            content: counter(page);
            font-size: 9pt;
            color: #7f8c8d;
        }
    }
    
    body {
        font-family: 'Helvetica', 'Arial', sans-serif;
        font-size: 12pt;
        line-height: 1.5;
        color: #2c3e50;
        margin: 0;
        padding: 0;
    }
    
    /* Cover Page */
    .cover-page {
        text-align: center;
        padding-top: 4cm;
        page-break-after: always;
    }
    
    .logo-header {
        text-align: center;
        margin-bottom: 2cm;
    }
    
    .pdf-logo {
        height: 80px;
        width: auto;
        max-width: 300px;
    }
    
    .cover-page h1 {
        font-size: 28pt;
        color: #2c3e50;
        margin-bottom: 1cm;
        font-weight: bold;
    }
    
    .cover-page .subtitle {
        font-size: 16pt;
        color: #7f8c8d;
        margin-bottom: 2cm;
        font-style: italic;
        text-align: center;
    }
    
    .cover-page .date {
        font-size: 11pt;
        color: #95a5a6;
        margin-bottom: 1.5cm;
        text-align: center;
    }
    
    .cover-page .footer p {
        text-align: center;
        margin: 0.2cm 0;
    }
    
    .personalization-box {
        background-color: #f8f9fa;
        padding: 1.5cm;
        margin: 2cm auto;
        border-radius: 8px;
        border-left: 4px solid #3498db;
        max-width: 12cm;
        text-align: left;
    }
    
    .personalization-box h2 {
        color: #2c3e50;
        font-size: 14pt;
        margin-bottom: 0.5cm;
    }
    
    .personalization-box ul {
        margin: 0;
        padding-left: 1cm;
    }
    
    .personalization-box li {
        margin-bottom: 0.3cm;
        font-size: 11pt;
    }
    
    /* Page Breaks */
    .page-break {
        page-break-before: always;
    }
    
    /* Headers */
    h1 {
        color: #2c3e50;
        font-size: 20pt;
        margin-top: 0;
        margin-bottom: 1cm;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5cm;
    }
    
    h2 {
        color: #34495e;
        font-size: 16pt;
        margin-top: 1cm;
        margin-bottom: 0.5cm;
    }
    
    h3 {
        color: #34495e;
        font-size: 14pt;
        margin-top: 0.8cm;
        margin-bottom: 0.4cm;
    }
    
    /* Content Boxes */
    .key-points, .action-steps, .next-steps, .timeline, .pro-tips {
        background-color: #f8f9fa;
        padding: 1cm;
        margin: 0.8cm 0;
        border-radius: 6px;
        border-left: 3px solid #3498db;
    }
    
    .key-points h2, .action-steps h2, .next-steps h2, .timeline h2, .pro-tips h2 {
        margin-top: 0;
        color: #2c3e50;
        font-size: 14pt;
    }
    
    /* Lists */
    ul, ol {
        padding-left: 1.2cm;
        margin: 0.5cm 0;
    }
    
    li {
        margin-bottom: 0.4cm;
        line-height: 1.4;
    }
    
    /* Strong emphasis */
    strong {
        color: #2c3e50;
        font-weight: bold;
    }
    
    /* Strong headings (like Night X:) need more spacing */
    p strong:only-child {
        display: block;
        margin-top: 1em;
        margin-bottom: 0.5em;
    }
    
    /* Quiz summary */
    .quiz-summary {
        background-color: #e8f4f8;
        padding: 1cm;
        margin: 1cm 0;
        border-radius: 6px;
        border: 1px solid #bdc3c7;
    }
    
    .quiz-summary h3 {
        margin-top: 0;
        color: #2c3e50;
    }
    
    /* Encouragement box */
    .encouragement-box, .final-message {
        background-color: #d5f4e6;
        padding: 1cm;
        margin: 1.5cm 0;
        border-radius: 8px;
        border-left: 4px solid #27ae60;
        text-align: center;
    }
    
    .encouragement-box h3, .final-message h3 {
        margin-top: 0;
        color: #27ae60;
        font-size: 16pt;
    }
    
    /* Footer */
    .footer {
        position: absolute;
        bottom: 2cm;
        left: 2cm;
        right: 2cm;
        text-align: center;
        font-size: 9pt;
        color: #7f8c8d;
        border-top: 1px solid #bdc3c7;
        padding-top: 0.5cm;
    }
    
    /* Module content */
    .module-content {
        page-break-before: always;
        margin-bottom: 2cm;
    }
    
    /* Conclusion page */
    .conclusion-page {
        page-break-before: always;
    }
    
    /* Ensure good spacing */
    p {
        margin: 0.5cm 0;
        text-align: justify;
    }
    """
    
def generate_quick_start_guide_pdf(customer):
    """
    Generate the Quick-Start Guide PDF.
    
    Args:
        customer: Customer object
        
    Returns:
        str: Path to generated PDF
    """
    if not WEASYPRINT_AVAILABLE:
        raise RuntimeError("PDF generation not available: WeasyPrint dependencies not installed")
    
    if not MARKDOWN2_AVAILABLE:
        raise RuntimeError("PDF generation not available: markdown2 package not installed")

    # Create filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"quick_start_guide_{customer.id}_{timestamp}.pdf"
    output_path = os.path.join(Config.PDF_OUTPUT_DIR, filename)
    
    os.makedirs(Config.PDF_OUTPUT_DIR, exist_ok=True)
    
    # Load Markdown content from file
    content_path = os.path.join(os.path.dirname(__file__), '../../content/quick_start_guide.md')
    with open(content_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
        
    # Personalize markdown content
    markdown_content = markdown_content.replace('{customer_name}', customer.name or 'there')

    # Convert markdown to HTML
    html_body = markdown2.markdown(
        markdown_content,
        extras=['fenced-code-blocks', 'tables', 'break-on-newline', 'header-ids']
    )
    
    # Wrap in complete HTML document
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Your Quick-Start Guide</title>
    </head>
    <body>
        <!-- Cover Page -->
        <div class="cover-page">
            <div class="logo-header">
                <img src="file://{os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend/images/napocalypse.png'))}" alt="Napocalypse Logo" class="pdf-logo">
            </div>
            <h1>Quick-Start Guide</h1>
            <p class="subtitle">Your First Steps to Better Sleep</p>
            <p class="subtitle">Customized for {get_personalized_subtitle(customer)}</p>
            <p class="date">Generated: {datetime.now().strftime('%B %d, %Y')}</p>
            
            <div class="footer">
                <p>&copy; {datetime.now().year} Napocalypse. All rights reserved.</p>
                <p>support@napocalypse.com</p>
            </div>
        </div>

        <!-- Guide Content -->
        <div class="page-break"></div>
        <div class="module-content">
            {html_body}
        </div>
        
        <!-- Footer on last page -->
        <div class="footer-page">
            <hr style="border: none; border-top: 2px solid #ddd; margin: 30px 0;">
            <div style="text-align: center; color: #666; font-size: 10pt;">
                <p>&copy; {datetime.now().year} Napocalypse. All rights reserved.</p>
                <p>support@napocalypse.com | napocalypse.com</p>
                <p style="margin-top: 20px; font-size: 9pt;">
                    This guide is for informational purposes only and does not constitute medical advice.<br>
                    Always consult with your pediatrician before making changes to your baby's sleep routine.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Generate PDF
    HTML(string=html_content).write_pdf(
        output_path,
        stylesheets=[CSS(string=get_pdf_styles())]
    )
    
    return output_path
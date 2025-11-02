"""
PDF Generation Service
Combines selected modules into a personalized PDF guide
"""

import os
from weasyprint import HTML, CSS
from datetime import datetime
from config import Config
from .module_selector import get_module_info

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

def generate_personalized_pdf(customer, quiz_data, modules):
    """
    Generate personalized PDF guide
    
    Args:
        customer: Customer object
        quiz_data (dict): Quiz response data
        modules (list): List of module names to include
        
    Returns:
        str: Path to generated PDF
    """
    # Create filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"sleep_guide_{customer.id}_{timestamp}.pdf"
    output_path = os.path.join(Config.PDF_OUTPUT_DIR, filename)
    
    # Generate HTML content
    html_content = generate_html_content(customer, quiz_data, modules)
    
    # Generate PDF
    HTML(string=html_content).write_pdf(
        output_path,
        stylesheets=[CSS(string=get_pdf_styles())]
    )
    
    return output_path

def generate_html_content(customer, quiz_data, modules):
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
            <h1>Your Personalized Baby Sleep Guide</h1>
            <p class="subtitle">Customized for {get_personalized_subtitle(customer)}</p>
            <p class="date">Generated: {datetime.now().strftime('%B %d, %Y')}</p>
            
            <div class="personalization-box">
                <h2>Your Personalized Plan Includes:</h2>
                <ul>
                    {''.join([f'<li>{m["title"]}</li>' for m in module_details])}
                </ul>
            </div>
            
            <div class="footer">
                <p>© {datetime.now().year} Napocalypse. All rights reserved.</p>
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
                    <li><strong>{customer.baby_name + "'s" if customer.baby_name else "Baby's"} Age:</strong> {quiz_data.get('baby_age', 'N/A')}</li>
                    <li><strong>Sleep Challenge:</strong> {quiz_data.get('biggest_challenge', 'N/A')}</li>
                    <li><strong>Your Approach:</strong> {quiz_data.get('sleep_philosophy', 'N/A')}</li>
                    <li><strong>Living Situation:</strong> {quiz_data.get('living_situation', 'N/A')}</li>
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
        {generate_module_content(modules)}
        
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

def generate_module_content(modules):
    """
    Generate condensed, personalized module content (not full modules)
    """
    combined_content = ""
    
    for module_name in modules:
        module_summary = get_module_summary(module_name)
        combined_content += f'<div class="page-break"></div><div class="module-content">{module_summary}</div>'
    
    return combined_content

def get_module_summary(module_name):
    """
    Get condensed summary for each module (2-3 pages max per module)
    """
    summaries = {
        'module_1_newborn': """
            <h1>Newborn Sleep Foundations (0-3 Months)</h1>
            
            <div class="key-points">
                <h2>Key Points for Your Newborn:</h2>
                <ul>
                    <li><strong>Newborns cannot be sleep trained</strong> - and that's normal!</li>
                    <li>Expect 2-4 hour sleep stretches (14-17 hours total per day)</li>
                    <li>No day/night rhythm until 6-12 weeks</li>
                    <li>Focus on survival and building healthy foundations</li>
                </ul>
            </div>
            
            <h2>Your Action Plan:</h2>
            <div class="action-steps">
                <h3>1. Create a Safe Sleep Environment</h3>
                <ul>
                    <li>Room temperature 68-72°F</li>
                    <li>Blackout curtains or sleep mask for daytime naps</li>
                    <li>White noise machine</li>
                    <li>Safe sleep space (crib, bassinet, or bedside sleeper)</li>
                </ul>
                
                <h3>2. Start Gentle Routines</h3>
                <ul>
                    <li>Simple bedtime routine: feed, change, swaddle, shush</li>
                    <li>Keep nighttime interactions calm and dim</li>
                    <li>Bright light and activity during day feeds</li>
                </ul>
                
                <h3>3. Feeding and Sleep Connection</h3>
                <ul>
                    <li>Feed every 2-3 hours during day</li>
                    <li>Allow longer stretches at night (if baby wants them)</li>
                    <li>Dream feeds can help extend night sleep</li>
                </ul>
            </div>
            
            <div class="next-steps">
                <h2>When You're Ready (Around 4 Months):</h2>
                <p>Look for signs of sleep training readiness: longer natural sleep stretches, 
                more predictable nap times, and ability to stay awake for 1.5-2 hours between sleeps.</p>
            </div>
        """,
        
        'module_6_gentle': """
            <h1>Gentle Sleep Methods</h1>
            
            <div class="key-points">
                <h2>Perfect for Your Preference:</h2>
                <ul>
                    <li>Gradual approach with minimal crying</li>
                    <li>Responsive to your baby's needs</li>
                    <li>Builds trust while encouraging independence</li>
                    <li>Works well for sensitive babies and parents</li>
                </ul>
            </div>
            
            <h2>Your Gentle Method Options:</h2>
            
            <div class="action-steps">
                <h3>Option 1: Chair Method (Pick Up/Put Down)</h3>
                <ul>
                    <li>Sit in chair next to crib</li>
                    <li>Pick up baby when crying, put down when calm</li>
                    <li>Move chair further away every 3-7 days</li>
                    <li>Eventually remove chair completely</li>
                </ul>
                
                <h3>Option 2: Gradual Fading</h3>
                <ul>
                    <li>Start with your current routine</li>
                    <li>Gradually reduce assistance over 1-2 weeks</li>
                    <li>Example: patting → hand on chest → hand near baby → hand off</li>
                    <li>Take small steps backward in support</li>
                </ul>
                
                <h3>Option 3: Check and Console</h3>
                <ul>
                    <li>Leave room, return at intervals to briefly comfort</li>
                    <li>Start with short intervals (3-5 minutes)</li>
                    <li>Gradually increase time between checks</li>
                    <li>Keep check-ins brief and boring</li>
                </ul>
            </div>
            
            <div class="timeline">
                <h2>Expected Timeline:</h2>
                <p><strong>2-3 weeks</strong> for significant improvement with gentle methods. 
                Be patient and consistent - gentle approaches take longer but build lasting habits.</p>
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

def convert_markdown_to_html(markdown_text):
    """
    Simple markdown to HTML conversion
    For production, use a proper markdown library like markdown2 or mistune
    """
    # This is a simplified version - replace with proper markdown parser
    html = markdown_text
    
    # Headers
    html = html.replace('# ', '<h1>').replace('\n\n', '</h1>\n\n')
    html = html.replace('## ', '<h2>').replace('\n\n', '</h2>\n\n')
    html = html.replace('### ', '<h3>').replace('\n\n', '</h3>\n\n')
    
    # Paragraphs
    lines = html.split('\n\n')
    html = ''.join([f'<p>{line}</p>' if not line.startswith('<') else line for line in lines])
    
    return html

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
    }
    
    .cover-page .date {
        font-size: 11pt;
        color: #95a5a6;
        margin-bottom: 1.5cm;
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
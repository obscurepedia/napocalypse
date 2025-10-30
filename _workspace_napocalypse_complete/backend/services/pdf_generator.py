"""
PDF Generation Service
Combines selected modules into a personalized PDF guide
"""

import os
from weasyprint import HTML, CSS
from datetime import datetime
from config import Config
from .module_selector import get_module_info

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
            <p class="subtitle">Customized for {customer.name or 'Your Family'}</p>
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
            <h1>Welcome to Your Sleep Journey</h1>
            
            <p>Congratulations on taking the first step toward better sleep for your entire family!</p>
            
            <p>This guide has been personalized specifically for you based on your quiz responses:</p>
            
            <div class="quiz-summary">
                <h3>Your Situation:</h3>
                <ul>
                    <li><strong>Baby's Age:</strong> {quiz_data.get('baby_age', 'N/A')}</li>
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
                <h3>You've Got This!</h3>
                <p>Better sleep is just days away. Trust the process, stay consistent, and remember: you're teaching your baby a valuable life skill.</p>
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
    Load and combine module content
    """
    content_dir = os.path.join(os.path.dirname(__file__), '../../content/modules')
    combined_content = ""
    
    for module_name in modules:
        module_file = f"{module_name}_FULL_CONTENT.md"
        module_path = os.path.join(content_dir, module_file)
        
        if os.path.exists(module_path):
            with open(module_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
                # Convert markdown to HTML (simplified - you may want to use a proper markdown library)
                html_content = convert_markdown_to_html(markdown_content)
                combined_content += f'<div class="page-break"></div><div class="module-content">{html_content}</div>'
        else:
            combined_content += f'<div class="page-break"></div><div class="module-content"><h1>{module_name}</h1><p>Module content will be added here.</p></div>'
    
    return combined_content

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
    CSS styles for PDF
    """
    return """
    @page {
        size: A4;
        margin: 2cm;
    }
    
    body {
        font-family: 'Helvetica', 'Arial', sans-serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #333;
    }
    
    .cover-page {
        text-align: center;
        padding-top: 5cm;
    }
    
    .cover-page h1 {
        font-size: 32pt;
        color: #2c3e50;
        margin-bottom: 1cm;
    }
    
    .cover-page .subtitle {
        font-size: 18pt;
        color: #7f8c8d;
        margin-bottom: 2cm;
    }
    
    .personalization-box {
        background-color: #ecf0f1;
        padding: 1cm;
        margin: 2cm 0;
        border-radius: 8px;
    }
    
    .page-break {
        page-break-after: always;
    }
    
    h1 {
        color: #2c3e50;
        font-size: 24pt;
        margin-top: 1cm;
        margin-bottom: 0.5cm;
    }
    
    h2 {
        color: #34495e;
        font-size: 18pt;
        margin-top: 0.8cm;
        margin-bottom: 0.4cm;
    }
    
    h3 {
        color: #34495e;
        font-size: 14pt;
        margin-top: 0.6cm;
        margin-bottom: 0.3cm;
    }
    
    .quiz-summary {
        background-color: #e8f4f8;
        padding: 0.5cm;
        margin: 0.5cm 0;
        border-left: 4px solid #3498db;
    }
    
    .encouragement-box {
        background-color: #d5f4e6;
        padding: 0.5cm;
        margin: 1cm 0;
        border-left: 4px solid #27ae60;
    }
    
    .final-message {
        background-color: #fef5e7;
        padding: 1cm;
        margin: 1cm 0;
        border-left: 4px solid #f39c12;
        text-align: center;
    }
    
    ul, ol {
        margin-left: 1cm;
    }
    
    li {
        margin-bottom: 0.3cm;
    }
    
    .footer {
        position: absolute;
        bottom: 2cm;
        width: 100%;
        text-align: center;
        font-size: 9pt;
        color: #7f8c8d;
    }
    """
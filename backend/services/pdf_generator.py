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
                <p style="font-size: 32pt; font-weight: bold; color: #2c3e50; margin: 0.5cm 0;">🌙 Napocalypse</p>
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
        <div class="module-content">
            {html_body}

            <!-- Footer -->
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

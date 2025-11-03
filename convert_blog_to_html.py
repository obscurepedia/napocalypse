#!/usr/bin/env python3
"""
Convert markdown blog posts to HTML with consistent styling
"""

import os
import re
from pathlib import Path

# HTML template
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Napocalypse</title>
    <meta name="description" content="{description}">
    <meta name="keywords" content="{keywords}">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.8;
            color: #333;
            background: #f8f9fa;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 20px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 15px;
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
        }}
        
        .header .meta {{
            font-size: 1em;
            opacity: 0.9;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            display: grid;
            grid-template-columns: 1fr 300px;
            gap: 40px;
        }}
        
        .main-content {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .sidebar {{
            position: sticky;
            top: 20px;
            height: fit-content;
        }}
        
        .sidebar-box {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        
        .sidebar-box h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        .related-post {{
            padding: 12px 0;
            border-bottom: 1px solid #eee;
        }}
        
        .related-post:last-child {{
            border-bottom: none;
        }}
        
        .related-post a {{
            color: #333;
            text-decoration: none;
            font-weight: 500;
        }}
        
        .related-post a:hover {{
            color: #667eea;
        }}
        
        .product-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }}
        
        .product-card h4 {{
            color: #333;
            margin-bottom: 8px;
        }}
        
        .product-card p {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
        }}
        
        .product-card .price {{
            font-size: 1.2em;
            color: #667eea;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .product-card a {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
        }}
        
        .product-card a:hover {{
            background: #5568d3;
        }}
        
        .main-content h2 {{
            color: #2c3e50;
            margin-top: 40px;
            margin-bottom: 20px;
            font-size: 2em;
        }}
        
        .main-content h3 {{
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.5em;
        }}
        
        .main-content p {{
            margin-bottom: 20px;
            font-size: 1.1em;
        }}
        
        .main-content ul, .main-content ol {{
            margin-bottom: 20px;
            margin-left: 30px;
        }}
        
        .main-content li {{
            margin-bottom: 10px;
            font-size: 1.1em;
        }}
        
        .main-content strong {{
            color: #2c3e50;
        }}
        
        .main-content em {{
            color: #555;
        }}
        
        .cta-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            text-align: center;
            margin: 40px 0;
        }}
        
        .cta-box h3 {{
            color: white;
            margin-bottom: 15px;
        }}
        
        .cta-box p {{
            margin-bottom: 25px;
            font-size: 1.1em;
        }}
        
        .cta-box a {{
            display: inline-block;
            background: white;
            color: #667eea;
            padding: 15px 40px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            font-size: 1.1em;
        }}
        
        .cta-box a:hover {{
            background: #f0f0f0;
        }}
        
        .footer {{
            background: #2c3e50;
            color: white;
            padding: 40px 20px;
            text-align: center;
            margin-top: 60px;
        }}
        
        .footer a {{
            color: #667eea;
            text-decoration: none;
        }}
        
        .footer a:hover {{
            text-decoration: underline;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                grid-template-columns: 1fr;
            }}
            
            .sidebar {{
                position: static;
            }}
            
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .main-content {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{h1_title}</h1>
        <div class="meta">
            <span>📖 Reading Time: {reading_time} minutes</span> | 
            <span>Method: {method}</span> | 
            <span>Published: January 2024</span>
        </div>
    </div>

    <div class="container">
        <main class="main-content">
            {content}
        </main>

        <aside class="sidebar">
            <div class="sidebar-box">
                <h3>📚 Related Stories</h3>
                {related_stories}
            </div>

            <div class="sidebar-box">
                <h3>🎯 Advanced Training</h3>
                <div class="product-card">
                    <h4>Advanced {method_type} Playbook</h4>
                    <p>Complete step-by-step protocols for every {method_type} scenario</p>
                    <div class="price">$27</div>
                    <a href="#">Learn More →</a>
                </div>
            </div>

            <div class="sidebar-box">
                <h3>🚀 Coming Soon</h3>
                <div class="product-card">
                    <h4>Toddler Sleep Guide</h4>
                    <p>Handle toddler sleep challenges with confidence</p>
                    <p style="color: #667eea; font-weight: bold;">Launching Soon</p>
                </div>
            </div>
        </aside>
    </div>

    <div class="footer">
        <p><strong>Napocalypse</strong> – Surviving the Napocalypse, One Night at a Time</p>
        <p style="margin-top: 20px;">
            <a href="https://napocalypse.com">Home</a> | 
            <a href="https://napocalypse.com/blog">Blog</a> | 
            <a href="https://napocalypse.com/privacy.html">Privacy Policy</a> | 
            <a href="https://napocalypse.com/terms.html">Terms of Service</a>
        </p>
        <p style="margin-top: 20px; font-size: 0.9em;">© 2024 Napocalypse. All rights reserved.</p>
    </div>
</body>
</html>'''

def markdown_to_html(md_content):
    """Convert markdown to HTML"""
    html = md_content
    
    # Convert headers
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    
    # Convert bold and italic
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    
    # Convert lists
    lines = html.split('\n')
    in_ul = False
    in_ol = False
    result = []
    
    for line in lines:
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            if not in_ul:
                result.append('<ul>')
                in_ul = True
            result.append(f'<li>{line.strip()[2:]}</li>')
        elif re.match(r'^\d+\. ', line.strip()):
            if not in_ol:
                result.append('<ol>')
                in_ol = True
            cleaned_line = re.sub(r"^\d+\. ", "", line.strip())
            result.append(f'<li>{cleaned_line}</li>')
        else:
            if in_ul:
                result.append('</ul>')
                in_ul = False
            if in_ol:
                result.append('</ol>')
                in_ol = False
            if line.strip() and not line.strip().startswith('<'):
                result.append(f'<p>{line}</p>')
            else:
                result.append(line)
    
    if in_ul:
        result.append('</ul>')
    if in_ol:
        result.append('</ol>')
    
    return '\n'.join(result)

def extract_title(md_content):
    """Extract title from markdown"""
    match = re.search(r'^# (.+)$', md_content, re.MULTILINE)
    return match.group(1) if match else "Blog Post"

def get_method_type(filename):
    """Determine if CIO or Gentle"""
    return "CIO" if "cio" in filename else "Gentle Methods"

def get_related_stories(filename, method_type):
    """Get related stories based on method type"""
    if "cio" in filename:
        stories = [
            ('sarah-cio-feeding-success.html', 'Breaking Feed-to-Sleep with CIO'),
            ('mike-cio-motion-success.html', 'Ending Motion Dependency'),
            ('emma-cio-pacifier-success.html', 'Breaking Pacifier Dependency'),
            ('lisa-cio-naps-success.html', 'Fixing 30-Minute Naps'),
            ('tom-cio-early-morning-success.html', 'Ending 5 AM Wake-Ups'),
        ]
    else:
        stories = [
            ('rachel-gentle-feeding-success.html', 'Breaking Feed-to-Sleep Gently'),
            ('david-gentle-motion-success.html', 'Ending Motion Dependency'),
            ('amy-gentle-pacifier-success.html', 'Breaking Pacifier Dependency'),
            ('chris-gentle-naps-success.html', 'Fixing 30-Minute Naps'),
            ('jessica-gentle-early-morning-success.html', 'Ending 5 AM Wake-Ups'),
        ]
    
    # Remove current file from list
    stories = [(url, title) for url, title in stories if url not in filename]
    
    html = ""
    for url, title in stories[:4]:  # Show 4 related stories
        html += f'<div class="related-post"><a href="{url}">{title}</a></div>\n'
    
    return html

def convert_md_to_html(md_file, output_dir):
    """Convert a markdown file to HTML"""
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Extract metadata
    title = extract_title(md_content)
    method_type = get_method_type(md_file.name)
    
    # Remove the first h1 (we'll use it in the header)
    md_content = re.sub(r'^# .+$', '', md_content, count=1, flags=re.MULTILINE)
    
    # Convert markdown to HTML
    content_html = markdown_to_html(md_content)
    
    # Get related stories
    related_stories = get_related_stories(md_file.name, method_type)
    
    # Fill template
    html = HTML_TEMPLATE.format(
        title=title,
        description=title[:160],
        keywords="baby sleep, sleep training, " + method_type.lower(),
        h1_title=title,
        reading_time="8-9",
        method=method_type,
        content=content_html,
        related_stories=related_stories,
        method_type=method_type
    )
    
    # Write output
    output_file = output_dir / md_file.name.replace('.md', '.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Converted: {md_file.name} → {output_file.name}")

def main():
    blog_dir = Path('content/blog')
    
    # Get all markdown files
    md_files = list(blog_dir.glob('*.md'))
    
    print(f"Found {len(md_files)} markdown files to convert\n")
    
    for md_file in md_files:
        try:
            convert_md_to_html(md_file, blog_dir)
        except Exception as e:
            print(f"❌ Error converting {md_file.name}: {e}")
    
    print(f"\n✅ Conversion complete! {len(md_files)} files converted.")

if __name__ == '__main__':
    main()
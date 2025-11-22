import re
import os

blog_dir = r'C:\napo\napocalypse\frontend\blog'

# Get all HTML files in blog directory
blog_files = [f for f in os.listdir(blog_dir) if f.endswith('.html')]

for filename in blog_files:
    filepath = os.path.join(blog_dir, filename)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Remove upsell-box divs (with all content inside)
    content = re.sub(r'<div class="upsell-box">.*?</div>', '', content, flags=re.DOTALL | re.IGNORECASE)

    # Remove standalone upsell links (links that point to /upsell)
    content = re.sub(r'<p>\s*<a href="/upsell[^"]*"[^>]*>.*?</a>\s*</p>', '', content, flags=re.DOTALL | re.IGNORECASE)

    # Remove any remaining links to /upsell
    content = re.sub(r'<a href="/upsell[^"]*"[^>]*>.*?</a>', '', content, flags=re.DOTALL | re.IGNORECASE)

    # Remove upsell-related CSS classes
    content = re.sub(r'\.upsell-box\s*\{[^}]+\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\.upsell-box\s+h3\s*\{[^}]+\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\.upsell-benefits\s*\{[^}]+\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\.upsell-benefits\s+p\s*\{[^}]+\}', '', content, flags=re.DOTALL)

    # Clean up excessive blank lines (more than 2 consecutive)
    content = re.sub(r'\n{3,}', '\n\n', content)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Cleaned {filename}")
    else:
        print(f"  {filename} (no changes)")

print("\nDone! All blog files processed.")

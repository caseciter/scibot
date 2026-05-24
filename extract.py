import os
import urllib.request
from pypdf import PdfReader

def download_pdf(save_path="document.pdf"):
    url = "https://cdn.sci-notifier.codechips.in/orders/latest.pdf"
    print(f"Downloading PDF from {url}...")
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response, open(save_path, 'wb') as out_file:
            out_file.write(response.read())
        print("Download completed successfully.")
        return True
    except Exception as e:
        print(f"Error executing download: {e}")
        return False

def pdf_to_markdown(pdf_path="document.pdf", output_md="latest.md"):
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found. Generation halted.")
        return

    reader = PdfReader(pdf_path)
    extracted_text = []
    
    for page in reader.pages:
        text = page.extract_text()
        if text:
            extracted_text.append(text)
            
    full_text = "\n\n".join(extracted_text)
    paragraphs = full_text.split('\n\n')
    
    md_segments = []
    for p in paragraphs:
        if p.strip():
            # Standard markdown line breaking format
            clean_paragraph = p.replace('\n', '  \n')
            md_segments.append(clean_paragraph)
            
    md_content = "\n\n".join(md_segments)

    with open(output_md, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Successfully updated text output in {output_md}")

if __name__ == "__main__":
    if download_pdf():
        pdf_to_markdown()
    
    # Process text cleanly into Markdown layout paragraph breaks
    md_segments = []
    for p in paragraphs:
        if p.strip():
            clean_paragraph = p.replace('\n', '  \n')
            md_segments.append(clean_paragraph)
            
    md_content = "\n\n".join(md_segments)

    # 1. Save raw extracted content as latest.md
    with open(output_md, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Successfully saved text to {output_md}")

    # 2. Save index.html template with high-contrast B&W styling and Georgia typography
    # This setup dynamically fetches latest.md to avoid string parsing syntax errors entirely
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Latest Orders</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        body {
            background-color: #ffffff;
            color: #000000;
            font-family: Georgia, serif;
            line-height: 1.6;
            margin: 0;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
        }
        main {
            max-width: 650px;
            width: 100%;
        }
        p {
            margin-bottom: 1.5em;
            font-size: 1.1rem;
            text-align: justify;
        }
        h1, h2, h3 {
            font-weight: bold;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }
    </style>
</head>
<body>
    <main id="content">Loading latest data layout...</main>
    <script>
        // Safely fetch the generated markdown file dynamically from the environment
        fetch('latest.md')
            .then(response => response.text())
            .then(markdownText => {
                document.getElementById('content').innerHTML = marked.parse(markdownText);
            })
            .catch(err => {
                document.getElementById('content').innerHTML = '<p>Error rendering document content.</p>';
                console.error(err);
            });
    </script>
</body>
</html>
"""

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"Successfully generated static structural file: {output_html}")

if __name__ == "__main__":
    if download_pdf():
        pdf_to_markdown_and_html()

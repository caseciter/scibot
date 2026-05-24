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

def pdf_to_html(pdf_path="document.pdf", output_html="index.html"):
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
    
    # FIX: Process the replacement outside of the f-string expression
    html_segments = []
    for p in paragraphs:
        if p.strip():
            clean_paragraph = p.replace('\n', '<br>')
            html_segments.append(f"<p>{clean_paragraph}</p>")
            
    html_content = "".join(html_segments)

    # Minimalist, high-contrast B&W style theme with Georgia typography
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Latest Orders</title>
    <style>
        body {{
            background-color: #ffffff;
            color: #000000;
            font-family: Georgia, serif;
            line-height: 1.6;
            margin: 0;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
        }}
        main {{
            max-width: 650px;
            width: 100%;
        }}
        p {{
            margin-bottom: 1.5em;
            font-size: 1.1rem;
            text-align: justify;
        }}
    </style>
</head>
<body>
    <main>
        {html_content}
    </main>
</body>
</html>
"""

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"Successfully compiled template into {output_html}")

if __name__ == "__main__":
    if download_pdf():
        pdf_to_html()

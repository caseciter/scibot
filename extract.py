import os
import urllib.request
from pypdf import PdfReader

def download_pdf(save_path="document.pdf"):
    # The URL is hardcoded directly inside the function
    url = "https://cdn.sci-notifier.codechips.in/orders/latest.pdf"
    
    print(f"Downloading PDF from {url}...")
    try:
        # Using a standard User-Agent header to bypass basic server blocks
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response, open(save_path, 'wb') as out_file:
            out_file.write(response.read())
        print("Download complete successfully.")
        return True
    except Exception as e:
        print(f"Error executing download: {e}")
        return False

def pdf_to_html(pdf_path="document.pdf", output_html="index.html"):
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found. Generation halted.")
        return

    # Extract clean text segments from the downloaded document
    reader = PdfReader(pdf_path)
    extracted_text = []
    
    for page in reader.pages:
        text = page.extract_text()
        if text:
            extracted_text.append(text)
            
    full_text = "\n\n".join(extracted_text)

    # Convert line breaks to clean HTML paragraphs
    paragraphs = full_text.split('\n\n')
    html_content = "".join(f"<p>{p.replace('\n', '<br>')}</p>" for p in paragraphs if p.strip())

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
    # Call the download function without needing to pass an external URL
    if download_pdf():
        pdf_to_html()
    # Convert line breaks to HTML paragraphs
    paragraphs = full_text.split('\n\n')
    html_content = "".join(f"<p>{p.replace('\n', '<br>')}</p>" for p in paragraphs if p.strip())

    # Minimalist, high-contrast B&W template with Georgia typography
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
            white-space: pre-line;
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
    print(f"Successfully generated {output_html}")

if __name__ == "__main__":
    pdf_url = "https://cdn.sci-notifier.codechips.in/orders/latest.pdf"
    
    # Download the latest PDF target file dynamically
    if download_pdf(pdf_url):
        pdf_to_html()

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

def pdf_to_markdown_and_html(pdf_path="document.pdf", output_md="latest.md", output_html="index.html"):
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
    
    # Clean up line breaks for formatting
    md_segments = []
    for p in paragraphs:
        if p.strip():
            # Double space at line-end creates natural breaks in standard Markdown engines
            clean_paragraph = p.replace('\n', '  \n')
            md_segments.append(clean_paragraph)
            
    md_content = "\n\n".join(md_segments)

    # 1. Save raw extracted content as a .md file
    with open(output_md, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Successfully saved text to {output_md}")

    # Escaping standard backticks for the javascript template string below
    safe_md_content = md_content.replace('`', '\\`').replace('$', '\\$')

    # 2. Save index.html template with a minimalist theme utilizing Georgia typography
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Latest Orders</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        body {{
            background-color: #ffffff;
            color: #000000;
            font-family: Georgia, serif;
            line-height:

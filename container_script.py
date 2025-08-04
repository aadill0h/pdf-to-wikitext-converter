# File: container_script.py (Corrected)

import pymupdf4llm
import subprocess
import os
import sys

# The directory where the mounted data resides
DATA_DIR = "/data"

def pdf_to_markdown(input_filename):
    """Converts a PDF file to a Markdown file."""
    try:
        # Construct full paths relative to the /data directory
        input_path = os.path.join(DATA_DIR, input_filename)
        base_name = os.path.splitext(os.path.basename(input_filename))[0]
        md_filename = f"{base_name}.md"
        output_path = os.path.join(DATA_DIR, md_filename)
        
        md_text = pymupdf4llm.to_markdown(input_path)
        with open(output_path, 'w', encoding='utf-8') as md_file:
            md_file.write(md_text)
        
        print(f"[CONTAINER] Markdown file created successfully: {md_filename}")
        return md_filename
    except Exception as e:
        print(f"[CONTAINER] An error occurred while converting PDF to Markdown: {e}")
        return None

def markdown_to_wikitext(md_filename):
    """Converts a Markdown file to a Wikitext file using Pandoc."""
    try:
        # Construct full paths relative to the /data directory
        input_path = os.path.join(DATA_DIR, md_filename)
        base_name = os.path.splitext(os.path.basename(md_filename))[0]
        wiki_filename = f"{base_name}_wikitext.txt"
        output_path = os.path.join(DATA_DIR, wiki_filename)
        
        subprocess.run([
            'pandoc',
            '-f', 'markdown',
            '-t', 'mediawiki',
            '-o', output_path,
            input_path
        ], check=True)
        
        print(f"[CONTAINER] Wikitext file created successfully: {wiki_filename}")
    except Exception as e:
        print(f"[CONTAINER] Unexpected error during Pandoc conversion: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[CONTAINER] Error: No input file name provided.")
        sys.exit(1)
        
    source_filename = sys.argv[1]
    
    print(f"[CONTAINER] Processing file: {source_filename} from {DATA_DIR}")
    
    input_file_path = os.path.join(DATA_DIR, source_filename)
    if not os.path.exists(input_file_path):
        print(f"[CONTAINER] Error: File not found inside the container at {input_file_path}")
        # List contents of /data for debugging
        print(f"[CONTAINER] Contents of {DATA_DIR}: {os.listdir(DATA_DIR)}")
        sys.exit(1)

    markdown_file = pdf_to_markdown(source_filename)
    
    if markdown_file:
        markdown_to_wikitext(markdown_file)
        
    print("[CONTAINER] Conversion process finished.")

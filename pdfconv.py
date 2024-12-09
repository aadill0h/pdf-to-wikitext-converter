'''import pymupdf4llm
import subprocess

def pdf_to_markdown(input_filename):
    try:
        md_text = pymupdf4llm.to_markdown(input_filename)
        with open("output.md",'w') as md_file:
            md_file.write(md_text)
    except:
        print(f"unknown error occured while converting PDF to Markdown {e}")

def markdown_to_wikitext(md_filename,wiki_filename = 'wikitext.txt'):
    try :
        subprocess.run([
            'pandoc',
            '-f','markdown',
            '-t','mediawiki',
            '-o',wiki_filename,
            md_filename
        ],check = True
    )
        print(f"process completed sucessfully")
    except FileNotFoundError:
        print(f"pandoc not found")
    except subprocess.CalledProcessError as e:
        print(f"error:{e}")
    except Exception as e:
        print(f"unexepected error:{e}")

pdf_to_markdown("test.pdf")
markdown_to_wikitext("output.md","wikitxt.txt")
'''
import pymupdf4llm
import subprocess
import os

def pdf_to_markdown(input_filename):
    try:
        input_dir = os.path.dirname(input_filename)
        base_name = os.path.splitext(os.path.basename(input_filename))[0]
        
        md_filename = os.path.join(input_dir, f"{base_name}.md")
        
        md_text = pymupdf4llm.to_markdown(input_filename)
        with open(md_filename, 'w') as md_file:
            md_file.write(md_text)
        
        print(f"Markdown file created successfully at: {md_filename}")
        return md_filename
    except Exception as e:
        print(f"An error occurred while converting PDF to Markdown: {e}")

def markdown_to_wikitext(md_filename):
    try:
        input_dir = os.path.dirname(md_filename)
        base_name = os.path.splitext(os.path.basename(md_filename))[0]
        
        wiki_filename = os.path.join(input_dir, f"{base_name}_wikitext.txt")
        
        subprocess.run([
            'pandoc',
            '-f', 'markdown',
            '-t', 'mediawiki',
            '-o', wiki_filename,
            md_filename
        ], check=True)
        
        print(f"Wikitext file created successfully at: {wiki_filename}")
    except FileNotFoundError:
        print("Pandoc not found. Please ensure it is installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during conversion: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    source_filename = input("Enter the source PDF file name (with path if not in the current directory): ").strip()
    
    markdown_file = pdf_to_markdown(source_filename)
    
    if markdown_file:
        markdown_to_wikitext(markdown_file)

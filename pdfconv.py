import pymupdf4llm
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
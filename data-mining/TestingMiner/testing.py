from pdfminer.high_level import *
import os
from sys import platform

if platform == "win32" or platform == "win64":
    x = "\\"
else:
    x = "/"

pdf_folder = os.chdir(f"..{x}data-files") # cd into the folder with data

pdfs = [f for f in os.listdir() if f.endswith(".pdf")]
num_pdfs = len(pdfs)

num_pages = len(list(extract_pages(pdfs[0])))

contents_page = None
for i in range(num_pages):
    s=extract_text(pdfs[0],page_numbers=[i])
    if "contents" in s.lower():
        contents_page = s
        break

contents_page = contents_page.split("\n")

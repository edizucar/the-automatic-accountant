from pdfminer.high_level import extract_text
import os
from sys import platform

if platform == "win32" or platform == "win64":
    x = "\\"
else:
    x = "/"

pdf_folder = os.chdir(f"..{x}data-files") # cd into the folder with data

pdfs = [f for f in os.listdir() if f.endswith(".pdf")]
num_pdfs = len(pdfs)

for pdf in pdfs[:1]:
    text = extract_text(pdf)
    print(text)
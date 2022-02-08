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
contents,directors,comprehensive_income,balance_sheet,equity = [extract_pages(pdfs[0],page_numbers=[i]) for i in [1,2,9,10,11]]
print(contents)
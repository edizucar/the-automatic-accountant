#from pdfminer.high_level import extract_pages, extract_text
from PDF import PDF
import os
from sys import platform
from PyPDF2 import PdfFileReader

if platform == "win32" or platform == "win64":
    x = "\\"
else:
    x = "/"

pdf_folder = os.chdir(f"..{x}data-files") # cd into the folder with data

pdf = [PDF(f) for f in os.listdir() if f.endswith(".pdf")][0]

pdfpath = [f for f in os.listdir() if f.endswith(".pdf")][0]
pdfreader = PdfFileReader(pdfpath)

print(pdfreader.getPage(1).items())


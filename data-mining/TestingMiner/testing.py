from pdfminer.high_level import extract_text
import os

pdf_folder = os.chdir(os.getcwd() + "\\data-files") # cd into the folder with data

pdfs = [f for f in os.listdir() if f.endswith(".pdf")]
num_pdfs = len(pdfs)
for pdf in pdfs[:1]:
    text = extract_text(pdf)
    print(text)
from pdfminer.high_level import extract_text
import os

pdf_folder = os.chdir("..\\data-files") # cd into the folder with data

pdfs = [f for f in os.listdir() if f.endswith(".pdf")]
num_pdfs = len(pdfs)
contents,directors,comprehensive_income,balance_sheet,equity = [extract_text(pdfs[0],page_numbers=[i]) for i in [1,2,9,10,11]]
print(contents)
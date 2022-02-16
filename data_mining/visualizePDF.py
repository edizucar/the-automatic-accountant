from pdfquery import PDFQuery

import pdfminer
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator

import matplotlib.pyplot as plt
from matplotlib import patches

import pandas as pd



def extract_page_layouts(file):
    """
    Extracts LTPage objects from a pdf file.
    modified from: http://www.degeneratestate.org/posts/2016/Jun/15/extracting-tabular-data-from-pdfs/
    Tests show that using PDFQuery to extract the document is ~ 5 times faster than pdfminer.
    """
    laparams = LAParams()
    
    with open(file, mode='rb') as pdf_file:
        print("Open document %s" % pdf_file.name)
        document = PDFQuery(pdf_file).doc

        if not document.is_extractable:
            raise PDFTextExtractionNotAllowed

        rsrcmgr = PDFResourceManager()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        layouts = []
        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
            layouts.append(device.get_result())
    
    return layouts

#example_file = "example_anonymous.pdf"
example_file = "CE Statutory Accounts FY18-19.pdf"
page_layouts = extract_page_layouts(example_file)
print("Number of pages: %d" % len(page_layouts))



current_page = page_layouts[10]
for obj in set(type(o) for o in current_page):
    print(obj)


texts = []
rects = []

# seperate text and rectangle elements
for elem in current_page:
    if isinstance(elem, pdfminer.layout.LTTextBoxHorizontal):
        texts.append(elem)
    elif isinstance(elem, pdfminer.layout.LTRect):
        rects.append(elem)



TEXT_ELEMENTS = [
    pdfminer.layout.LTTextBox,
    pdfminer.layout.LTTextBoxHorizontal,
    pdfminer.layout.LTTextLine,
    pdfminer.layout.LTTextLineHorizontal
]

def flatten(lst):
    """Flattens a list of lists"""
    return [item for sublist in lst for item in sublist]

def extract_characters(element):
    """
    Recursively extracts individual characters from 
    text elements. 
    """
    if isinstance(element, pdfminer.layout.LTChar):
        return [element]

    if any(isinstance(element, i) for i in TEXT_ELEMENTS):
        return flatten([extract_characters(e) for e in element])

    if isinstance(element, list):
        return flatten([extract_characters(l) for l in element])

    return []

# extract characters from texts
characters = extract_characters(texts)
print("--- Print LTChar ----")
print(characters[10])

def draw_rect_bbox(bbox, ax, color):
    """
    Draws an unfilled rectable onto ax.
    """
    x0,y0,x1,y1 = tuple(bbox)
    ax.add_patch( 
        patches.Rectangle(
            (x0, y0),
            x1 - x0,
            y1 - y0,
            fill=False,
            color=color
        )    
    )
    
def draw_rect(rect, ax, color="black"):
    draw_rect_bbox(rect.bbox, ax, color)

xmin, ymin, xmax, ymax = current_page.bbox
size = 6
num_pages = 2

fig, axes = plt.subplots(1,num_pages, figsize = (num_pages*size, size * (ymax/xmax)), sharey=True, sharex=True)

# rects and chars
ax = axes[0]
for rect in rects:
    draw_rect(rect, ax)
    
for c in characters:
    draw_rect(c, ax, "red")

# chars and TextBoxes
ax = axes[1]
for c in characters:
    draw_rect(c, ax, "red")    

for textbox in texts:
    draw_rect(textbox, ax, "blue")
    

plt.xlim(xmin, xmax)
plt.ylim(ymin, ymax)
plt.show()


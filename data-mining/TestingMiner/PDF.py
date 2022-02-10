#from pdfminer.high_level import extract_pages, extract_text
from PyPDF2 import PdfFileReader

class PDF:
    def __init__(self, path):
        self.pdfreader = PdfFileReader(path)
        self.__path = path
        self.__pages = {}
        self.__num_pages = self.pdfreader.getNumPages()
        self.__content_index = None
        self.__directors_index = None
        self.__balance_sheet_index = None
        self.__equity_changes_index = None
        self.__comprehensive_income_index = None


    def get_num_pages(self):
        return self.__num_pages

    def get_path(self):
        return self.__path

    def get_page(self, i):
        if i in self.__pages:
            return self.__pages[i]
        else:
            self.__pages[i] = self.pdfreader.extractText(i)
            return self.__pages[i]
    
    def find_contents_index(self):
        if self.__content_index != None:
            return self.__content_index

        for i in range(self.__num_pages):
            s=self.get_page(i)
            if "contents" in s.lower():
                self.__content_index = i
                return self.__content_index
        raise Exception("Contents page not found.")

    def get_contents_content(self):
        return self.get_page(self.find_contents_index())

    def find_directors_index(self):
        if self.__directors_index != None:
            return self.__directors_index

    def get_directors_content(self):
        return self.get_page(self.find_directors_index())

    def find_balance_sheet_index(self):
        if self.__balance_sheet_index != None:
            return self.__balance_sheet_index
    
    def get_balance_sheet_content(self):
        return self.get_page(self.find_balance_sheet_index())

    def find_equity_changes_index(self):
        if self.__equity_changes_index != None:
            return self.__equity_changes_index

    def get_equity_changes_content(self):
        return self.get_page(self.find_equity_changes_index())

    def find_comprehensive_income_index(self):
        if self.__comprehensive_income_index != None:
            return self.__comprehensive_income_index

    def get_contents_page_content(self):
        return self.get_page(self.find_comprehensive_income_index())
    

            
import sys
import time

from PyQt5 import QtCore, QtWebEngineWidgets, QtWidgets
from PyQt5 import QtGui
import json
from fpdf import FPDF
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, \
    QFileDialog, QPushButton, QHBoxLayout, QVBoxLayout, QTextEdit, QPlainTextEdit, QLabel, QStackedWidget
from PyQt5.QtGui import QIcon
from enum import Enum, IntEnum, auto

import pathlib
import os



sys.path.append('.')
sys.path.append('../data_analysis')
from data_analysis.analysis_testing import main as getAnalysisJSON
class Type(IntEnum):
    ONE_YEAR_ONE_COMPANY = 1
    MULTIPLE_YEARS_ONE_COMPANY = 2
    ONE_YEAR_TWO_COMPANIES = 3


class Combined(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'The Automatic Accountant'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480
        self.screen = 0
        self.initUI()

    def initUI(self):
        self.stackedWidget = QStackedWidget()

        self.firstWindow = App(self.resultsScreen)
        self.stackedWidget.addWidget(self.firstWindow)
        self.secondWindow = SecondWindow(self.mainScreen)
        self.stackedWidget.addWidget(self.secondWindow)

        self.stackedWidget.show()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.stackedWidget)
        self.stackedWidget.show()
        print(self.stackedWidget.currentIndex())

    def resultsScreen(self):
        data = getAnalysisJSON(self.firstWindow.filesToAnalyse)
        self.secondWindow.giveAnalysisData(data)
        self.stackedWidget.setCurrentIndex(1)
        
    def mainScreen(self):
        self.stackedWidget.setCurrentIndex(0)


class App(QWidget):

    def __init__(self,swapScreen):
        super().__init__()
        self.title = 'The Automatic Accountant'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480
        self.initUI()
        self.swapScreen = swapScreen

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.mainTopWidget = QWidget()
        self.mainBottomWidget = QWidget()

        # Create Layouts
        self.mainLayout = QVBoxLayout()
        self.mainTopLayout = QHBoxLayout()
        self.mainBottomLayout = QHBoxLayout()

        print(self.mainLayout.alignment())

        self.label = QLabel("Please upload the files you would like us to analyze")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("QLabel {color: grey;}")
        self.mainLayout.addWidget(self.label)

        self.mainLayout.addWidget(self.mainTopWidget)
        self.mainLayout.addWidget(self.mainBottomWidget)

        # Assign Layouts
        self.setLayout(self.mainLayout)
        self.mainTopWidget.setLayout(self.mainTopLayout)
        self.mainBottomWidget.setLayout(self.mainBottomLayout)

        # Create Buttons
        self.uploadAccountsButton = QPushButton("📁 Upload Accounts")
        # self.uploadAccountsButton.setStyleSheet("QPushButton {background-color : dark-yellow}")
        self.uploadAccountsButton.setCheckable(True)
        self.uploadAccountsButton.clicked.connect(self.uploadAccounts)

        # Button To look up companies
        self.CompanyLookup = QPushButton("Lookup Company")
        self.CompanyLookup.setCheckable(True)
        self.CompanyLookup.clicked.connect(self.companyLookup)

        self.textbox = QLineEdit(self)

        self.runAnalysisButton = QPushButton("Run Analysis")
        self.runAnalysisButton.setCheckable(True)
        self.runAnalysisButton.setEnabled(False)
        self.runAnalysisButton.clicked.connect(self.analyseAccounts)

        self.filesText = QTextEdit()
        self.filesText.setText("No files currently imported")
        self.filesText.setReadOnly(True)
        # Add text


        # Add Buttons to window

        self.mainTopLayout.addWidget(self.uploadAccountsButton)
        self.mainBottomLayout.addWidget(self.runAnalysisButton)
        self.mainBottomLayout.addWidget(self.CompanyLookup)
        self.mainBottomLayout.addWidget(self.filesText)
        self.mainLayout.addWidget(self.textbox)

        self.show()

    def companyLookup(self):
        company = self.textbox.text()
        link = f"https://find-and-update.company-information.service.gov.uk/search?q={company}"
        print(link)

    def uploadAccounts(self):
        files = self.openFileNamesDialog()
        
        # No files selected
        if not files:
            return
        else:
            self.runAnalysisButton.setEnabled(True)
            #pal = self.runAnalysisButton.palette()
            #pal.setColor(QtGui.QPalette.Button, QtGui.QColor.fromRgb(255, 255, 0))
            #self.runAnalysisButton.setPalette(pal)
            #self.runAnalysisButton.update()
            self.filesText.setText("\n".join([("📃" + i.split("/")[-1]) for i in files]))
            self.filesToAnalyse = files

        
    def analyseAccounts(self):
        print("ANALYSIS")
        self.swapScreen()
        # TODO: Analyse accounts

    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select Accounts to Analyse", "",
                                                "Html Files (*.html);;Xhtml Files (*.xhtml);;", options=options)
        if files:
            return files
        else:
            return None

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(fileName)

class SecondWindow(QWidget):
    def __init__(self, swapScreen):
        super().__init__()
        self.title = 'The Automatic Accountant'
        self.left = 100
        self.top = 100
        self.width = 800
        self.height = 600
        self.initUI()
        self.twoPDFS = False
        self.swapScreen = swapScreen
        self.analysisType = None

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.mainTopWidget = QWidget()
        self.mainBottomWidget = QWidget()

        # Create Layouts
        self.mainLayout = QVBoxLayout()
        self.mainTopLayout = QHBoxLayout()
        self.mainBottomLayout = QHBoxLayout()

        #print(self.mainLayout.alignment())-

        self.label = QLabel("Here are the results of the analysis")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("QLabel {color: grey;}")
        self.mainTopLayout.addWidget(self.label)
        
        self.backButton = QPushButton("Return")
        self.downloadFilesButton = QPushButton("Download Results")
        
        self.backButton.clicked.connect(self.goToMainPage)
        self.downloadFilesButton.clicked.connect(self.downloadResults)

        
        

        
        self.mainLayout.addWidget(self.mainTopWidget)
        self.mainLayout.addWidget(self.mainBottomWidget)
        self.mainTopWidget.setMaximumHeight(50)

        self.mainTopLayout.addWidget(self.backButton)
        self.mainTopLayout.addWidget(self.downloadFilesButton)
        
        self.mainTopLayout.addStretch()
        
        self.timestamp = time.time()
        
        self.view = QtWebEngineWidgets.QWebEngineView()
        self.settings = self.view.settings()
        self.settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, True)
        
        self.mainBottomLayout.addWidget(self.view)
        
        self.view2 = QtWebEngineWidgets.QWebEngineView()
        self.settings2 = self.view2.settings()
        self.settings2.setAttribute(QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, True)
        
        


        """
        #self.mainLayout.addWidget(self.mainBottomWidget)
        self.filename = os.path.join(os.path.dirname(__file__), 'GFG.pdf')
        #print(os.path)
        #filename = "GFG.pdf"

        self.view = QtWebEngineWidgets.QWebEngineView()
        self.settings = self.view.settings()
        self.settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, True)
        self.url = QtCore.QUrl.fromLocalFile(self.filename)
        

        self.mainBottomLayout.addWidget(self.view)

        #Trying to
        self.filename2 = os.path.join(os.path.dirname(__file__), 'GFG2.pdf')
        self.view2 = QtWebEngineWidgets.QWebEngineView()
        self.settings2 = self.view2.settings()
        self.settings2.setAttribute(QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, True)
        self.url2 = QtCore.QUrl.fromLocalFile(self.filename2)
        """

        #self.mainBottomLayout.addWidget(self.view2)

        #filename2 = "/Users/danielvlasits/PycharmProjects/the-automatic-accountant/Interface/GFG2.pdf"
        #view2 = QtWebEngineWidgets.QWebEngineView()
        #url2 = QtCore.QUrl.fromLocalFile(filename2)
        #view2.load(url2)
        #view2.show()

        #self.mainLayout.addWidget(view2)


        # Assign Layouts
        self.setLayout(self.mainLayout)
        
        self.mainTopWidget.setLayout(self.mainTopLayout)
        self.mainBottomWidget.setLayout(self.mainBottomLayout)

        self.show()
        
    def downloadResults(self):
        # TODO: Allow user to save pdf of results
        return
    
    def goToMainPage(self):
        self.swapScreen()

    def printBasic(self, item, json, pdf,noFlag = False, c1 = False, c2 = False):
        try:
            if not noFlag:
                pdf.set_font("Arial", size=15)
                pdf.set_text_color(0, 0, 0)
                if json[item]["Flag"] == 2:
                    pdf.set_text_color(0, 0, 100)
                if json[item]["Flag"] == 3:
                    pdf.set_text_color(100, 0, 0)
            print("_________________________________________")
            for key,value in json[item].items():

                print(key,value)

                if key not in ["Flag", "Message"]:
                    if item == "Suspicious Changes":
                        pdf.set_text_color(100, 0, 0)
                    if key == "Company1":
                        key = c1
                    if key == "Company2":
                        key = c2
                    pdf.cell(200, 10, txt=f"{key} : {value}",
                             ln=4, align='L')
                    if noFlag:
                        pdf.set_text_color(0, 0, 0)
            if not noFlag:
                if json[item]["Flag"] != 1:
                    pdf.multi_cell(200, 10, txt=f"Error Identified : {json[item]['Message']}",
                             align='L')
        except KeyError:
            pass



    def giveAnalysisData(self,data):
        #TODO CREATE PDF HERE
        # DATA IS EITHER FOR:
        # Single Company Single Year
        # 2 Companies Single Year - Side by side
        # Single Company Multiple Years
        self.data = data
        with open('json_data.json', 'w') as outfile:
            json.dump(self.data, outfile,indent=4)
        
        if data["Type"] == Type.ONE_YEAR_ONE_COMPANY:
            pdf, textToWrite = generateSingleYearSingleCompanyPDF(self, data)
            self.analysisType = Type.ONE_YEAR_ONE_COMPANY
            
            self.label.setText(textToWrite)

            name1 = "Analysis_{}_{}.pdf".format(data["Company Details"]["Company Name"],
                                                data["Company Details"]["Start date covered by report"])

            self.filename = os.path.join(os.path.dirname(__file__), name1)

            
            # save the pdf with name .pdf
            pdf.output(self.filename)
            self.setMinimumSize(800, 800)

            self.url = QtCore.QUrl.fromLocalFile(self.filename)
            
            if (self.twoPDFS):
                self.twoPDFS = False
                self.view2.hide()
                self.mainBottomLayout.removeWidget(self.view2)
                        
            
            
            self.view.load(self.url)
            self.view.show()        
            

        elif data["Type"] == Type.ONE_YEAR_TWO_COMPANIES:
            self.analysisType = Type.ONE_YEAR_TWO_COMPANIES
            pdf, textToWrite = generateSingleYearSingleCompanyPDF(self, data["Company 1"])
            pdf2, textToWrite2 = generateSingleYearSingleCompanyPDF(self, data["Company 2"], pdf)
            pdf2 = doComparisons(self,data)
            
            # save the pdf with name .pdf
            name1 = "Analysis_{}_{}.pdf".format(data["Company 1"]["Company Details"]["Company Name"], data["Company 1"]["Company Details"]["Start date covered by report"])
            name2 = "Analysis_{}_{}.pdf".format(data["Company 2"]["Company Details"]["Company Name"], data["Company 2"]["Company Details"]["Start date covered by report"])
            
           
            self.filename = os.path.join(os.path.dirname(__file__), name1)
            self.url = QtCore.QUrl.fromLocalFile(self.filename)
            self.filename2 = os.path.join(os.path.dirname(__file__), name2)
            self.url2 = QtCore.QUrl.fromLocalFile(self.filename2)

            #self.url = os.path.join("Interface",name1)
            #self.url2 = os.path.join("Interface",name2)
            
            pdf.output(self.filename)
            # save the pdf with name .pdf
            pdf2.output(self.filename2)
            
            self.view.load(self.url)
            self.view.show()
            
            self.view2.load(self.url2)
            self.view2.show()
            if (not self.twoPDFS):
                self.twoPDFS = True
                self.mainBottomLayout.addWidget(self.view2)

            self.setMinimumSize(1400, 800)
        elif data["Type"] == Type.MULTIPLE_YEARS_ONE_COMPANY:
            self.analysisType = Type.ONE_YEAR_ONE_COMPANY
            (pdf, pdf2), textToWrite = generateMultiYearSingleCompanyPDF(self, data["Yearly Analysis"], data)
            name1 = "PDF1"
            name2 = "PDF2"
            self.filename2 = os.path.join(os.path.dirname(__file__), name2)
            pdf2.output(self.filename2)
            self.url2 = QtCore.QUrl.fromLocalFile(self.filename2)
            self.view2.load(self.url2)
            self.view2.show()

            self.filename = os.path.join(os.path.dirname(__file__), name1)
            pdf.output(self.filename)
            self.url = QtCore.QUrl.fromLocalFile(self.filename)
            self.view.load(self.url)
            self.view.show()
            self.twoPDFS = True
            self.mainBottomLayout.addWidget(self.view2)
            if False:#(self.twoPDFS):
                self.twoPDFS = False
                self.view2.hide()
                self.mainBottomLayout.removeWidget(self.view2)
                

def generateSingleYearSingleCompanyPDF(self, CompanyData, samePDF = False):
    textToWrite = ""
    if not samePDF:
        pdf = FPDF()
    else:
        pdf = samePDF
    pdf.add_page()
        
    for key,value in CompanyData["Company Details"].items():
        pdf.set_font("Arial", size=15)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(200, 10, txt=f"{key}: {value}",
                    ln=4, align='C')
        if key not in ["SIC", "Industry", "Sector"]:
            textToWrite += str(value) + " "

    CompanyData["Negative Indices"]["Flag"] = 3
    CompanyData["Negative Indices"]["Message"] = "Index has negative value while it should be positive"

    #pdf.add_page()
    getDict = {"Director Info": ["Directors", "Director Turnover"],
                "Turnover Info": ["Turnover", "Turnover by Region"],
                "Profit Info": ["Gross Profit", "Net Profit", "Liquidity Ratio"],
                "Debtor Info": ["Debtor Days"],
                "Indices": ["Negative Indices"]}
    longLine = "-----------------------------------------------------------"
    for bigName in ["Director Info", "Turnover Info", "Profit Info", "Debtor Info", "Indices"]:
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', 'B', 15)
        pdf.cell(200, 10, txt=longLine,
                    ln=4, align='L', )
        pdf.cell(200, 10, txt=bigName,
                    ln=4, align='L', )
        pdf.set_font('Arial', size=15)
        for item in getDict[bigName]:
            pdf.cell(200, 10, txt=item,
                        ln=4, align='L')
            self.printBasic(item, CompanyData, pdf)
    self.label.setText(textToWrite)
    return pdf, textToWrite
def doComparisons(self, c2):
    companies = [{"Company Name": c2["Company 1"]['Company Details']['Company Name']}, {"Company Name" : c2["Company 2"]['Company Details']['Company Name']}]
    pdf2 = FPDF()
    pdf2.add_page()
    pdf2.set_font("Arial", size=15)
    pdf2.set_text_color(0, 0, 0)

    item = c2["Comparison"]

    pdf2.set_font("Arial", 'B', size=19)
    pdf2.set_text_color(0, 0, 0)
    longLine = "-----------------------------------------------------------"
    pdf2.multi_cell(200, 10, txt=f"Comparing Companies: {companies[0]['Company Name']} with {companies[1]['Company Name']}", align='C')
    pdf2.set_font('Arial', size=15)
    for key,value in item.items():
        if all([i is not None for i in value.values()]):
            print("here!!!!!")
            print(key)
            print(item)
            pdf2.set_font('Arial', 'B', 15)
            pdf2.cell(200, 10, txt=key,
                     ln=4, align='L', )
            pdf2.set_font('Arial', size=15)
            c1 = companies[0]['Company Name']
            c2 = companies[1]['Company Name']
            self.printBasic(key, item, pdf2,True, c1, c2)
            pdf2.cell(200, 10, txt=longLine,
                     ln=4, align='L', )


    companies.pop(0)


    return pdf2

def generateMultiYearSingleCompanyPDF(self, CompanyData2, c2):
    textToWrite = ""
    pdf = FPDF()
    pdf2 = FPDF()
    pdf.add_page()
    pdf2.add_page()
    pdf2.set_font("Arial", size=15)
    pdf2.set_text_color(0, 0, 0)
    companies = []
    for index,CompanyData in enumerate(CompanyData2):
        companies.append(CompanyData["Company Details"])
        for key,value in CompanyData["Company Details"].items():
            if index == 0:
                pdf.set_font("Arial", size=15)
                pdf.set_text_color(0, 0, 0)
                pdf.cell(200, 10, txt=f"{key}: {value}",
                         ln=4, align='C')
                if key not in ["SIC", "Industry", "Sector"]:
                    textToWrite += str(value) + " "
            else:
                if key == "Start date covered by report":
                    pdf.set_font("Arial", size=18,style="B")
                    pdf.set_text_color(0, 0, 0)
                    pdf.cell(200, 10, txt=f"Next Year : {value}",
                             ln=4, align='C')
                    pdf.set_font("Arial", size=15)

        CompanyData["Negative Indices"]["Flag"] = 3
        CompanyData["Negative Indices"]["Message"] = "Index has negative value while it should be positive"

        #pdf.add_page()
        getDict = {"Director Info": ["Directors", "Director Turnover"],
                    "Turnover Info": ["Turnover", "Turnover by Region"],
                    "Profit Info": ["Gross Profit", "Net Profit", "Liquidity Ratio"],
                    "Debtor Info": ["Debtor Days"],
                    "Indices": ["Negative Indices"]}
        longLine = "-----------------------------------------------------------"
        for bigName in ["Director Info", "Turnover Info", "Profit Info", "Debtor Info", "Indices"]:
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Arial', 'B', 15)
            pdf.cell(200, 10, txt=longLine,
                        ln=4, align='L', )
            pdf.cell(200, 10, txt=bigName,
                     ln=4, align='L', )
            pdf.set_font('Arial', size=15)
            for item in getDict[bigName]:
                pdf.cell(200, 10, txt=item,
                            ln=4, align='L')
                self.printBasic(item, CompanyData, pdf)
    print(companies)
    print(c2["Comparisons"])
    for item in c2["Comparisons"]:
        pdf2.set_font("Arial", 'B', size=19)
        pdf2.set_text_color(0, 0, 0)
        pdf2.cell(200, 10, txt=f"Comparing Year {companies[0]['Start date covered by report']} with {companies[1]['Start date covered by report']}",
                 ln=4, align='C')
        pdf2.set_font('Arial', size=15)
        for key,value in item.items():
            if all([i is not None for i in value.values()]):
                print("here!!!!!")
                print(key)
                print(item)
                pdf2.set_font('Arial', 'B', 15)
                pdf2.cell(200, 10, txt=key,
                         ln=4, align='L', )
                pdf2.set_font('Arial', size=15)
                c1 = companies[0]['Start date covered by report']
                c2 = companies[1]['Start date covered by report']
                self.printBasic(key, item, pdf2,True, c1, c2)
                pdf2.cell(200, 10, txt=longLine,
                         ln=4, align='L', )


        companies.pop(0)

    pdf2.add_page()
    p = os.path.join(os.path.dirname(__file__), "..", "directors.png")
    pdf2.image(p, w=190, h=100)
    p = os.path.join(os.path.dirname(__file__), "..", "Liquidity Ratio.png")
    pdf2.image(p, w=190, h=100)

    return (pdf,pdf2), textToWrite


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Combined()
    ##ex.swapScreen()
    sys.exit(app.exec_())

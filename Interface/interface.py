import sys
from PyQt5 import QtCore, QtWebEngineWidgets
from PyQt5 import QtGui
import json
from fpdf import FPDF
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, \
    QFileDialog, QPushButton, QHBoxLayout, QVBoxLayout, QTextEdit, QPlainTextEdit, QLabel, QStackedWidget
from PyQt5.QtGui import QIcon
import pathlib
import os


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
        path = pathlib.Path("../data_analysis/output_files/oneyear.json")
        with open(path, "r") as file:
            data = json.load(file)
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
        self.swapScreen = swapScreen

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.mainTopWidget = QWidget()
        self.mainBottomWidget = QWidget()

        # Create Layouts
        self.mainLayout = QVBoxLayout()
        self.mainTopLayout = QHBoxLayout()
        self.mainBottomLayout = QVBoxLayout()

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

        self.mainTopLayout.addWidget(self.backButton)
        self.mainTopLayout.addWidget(self.downloadFilesButton)
        
        self.mainTopLayout.addStretch()
        
        

        #self.mainLayout.addWidget(self.mainBottomWidget)
        filename = os.path.join(os.path.dirname(__file__), 'GFG.pdf')

        view = QtWebEngineWidgets.QWebEngineView()
        settings = view.settings()
        settings.setAttribute(QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, True)
        url = QtCore.QUrl.fromLocalFile(filename)
        view.load(url)
        view.show()
        
        self.resize(200,1400)
        

        self.mainBottomLayout.addWidget(view) 

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

    def printBasic(self, item, json, pdf):
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
                pdf.cell(200, 10, txt=f"{key} : {value}",
                         ln=4, align='L')
        if json[item]["Flag"] != 1:
            pdf.multi_cell(200, 10, txt=f"Error Identified : {json[item]['Message']}",
                     align='L')




    def giveAnalysisData(self,data):
        #TODO CREATE PDF HERE
        self.data = data
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=15)
        for key,value in data["Company Details"].items():
            pdf.cell(200, 10, txt=f"{key} : {value}",
                     ln=4, align='C')

        self.data["Negative Indices"]["Flag"] = 3
        self.data["Negative Indices"]["Message"] = "Index has negative value while it should be positive"

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
                self.printBasic(item, self.data, pdf)


        # save the pdf with name .pdf
        pdf.output("GFG.pdf")
        for i in self.data:
            print(i)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Combined()
    ##ex.swapScreen()
    sys.exit(app.exec_())

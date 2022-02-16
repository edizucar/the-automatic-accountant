import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog, QPushButton, QHBoxLayout, QVBoxLayout, QTextEdit, QPlainTextEdit
from PyQt5.QtGui import QIcon





class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'The Automatic Accountant'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.mainTopWidget = QWidget()
        self.mainBottomWidget = QWidget()
        
        # Create Layouts
        self.mainLayout = QVBoxLayout()
        self.mainTopLayout = QHBoxLayout()
        self.mainBottomLayout = QHBoxLayout()
        
        self.mainLayout.addWidget(self.mainTopWidget)
        self.mainLayout.addWidget(self.mainBottomWidget)
        
        # Assign Layouts
        self.setLayout(self.mainLayout)
        self.mainTopWidget.setLayout(self.mainTopLayout)
        self.mainBottomWidget.setLayout(self.mainBottomLayout)

        
        # Create Buttons
        self.uploadAccountsButton = QPushButton("Upload Accounts")
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
        self.filesText.setReadOnly(True)
        
        # Add Buttons to window
        self.mainTopLayout.addWidget(self.uploadAccountsButton)
        self.mainBottomLayout.addWidget(self.runAnalysisButton)
        self.mainBottomLayout.addWidget(self.CompanyLookup)
        self.mainBottomLayout.addWidget(self.filesText)

        
        self.show()

    def companyLookup(self):
        company = self.textbox.text()
        link = f"https://find-and-update.company-information.service.gov.uk/search?q={company}"
        print(link)

    
    def uploadAccounts(self):
        files = self.openFileNamesDialog()
        
        self.runAnalysisButton.setEnabled(True)
        self.filesText.setText("\n".join([i.split("/")[-1] for i in files]))
        print(self.filesText.isReadOnly())
        #TODO: Show selected files on window
    
    def analyseAccounts(self):
        print("ANALYSIS")
        #TODO: Analyse accounts
        
        
        
    
    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self,"Select Accounts to Analyse", "","All Files (*);;Python Files (*.py)", options=options)
        if files:
            return files
        else:
            return None
    
    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(fileName)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())

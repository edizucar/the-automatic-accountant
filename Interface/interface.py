import sys

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, \
    QFileDialog, QPushButton, QHBoxLayout, QVBoxLayout, QTextEdit, QPlainTextEdit, QLabel, QStackedWidget
from PyQt5.QtGui import QIcon


class Combined(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'The Automatic Accountant'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):
        self.stackedWidget = QStackedWidget()

        self.stackedWidget.addWidget(App(self.swapScreen))
        self.stackedWidget.addWidget(SecondWindow())

        self.stackedWidget.show()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.stackedWidget)
        self.stackedWidget.show()
        print(self.stackedWidget.currentIndex())

    def swapScreen(self):
        self.stackedWidget.setCurrentIndex(1)


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

        self.runAnalysisButton.setEnabled(True)
        #pal = self.runAnalysisButton.palette()
        #pal.setColor(QtGui.QPalette.Button, QtGui.QColor.fromRgb(255, 255, 0))
        #self.runAnalysisButton.setPalette(pal)
        #self.runAnalysisButton.update()
        self.filesText.setText("\n".join([("📃" + i.split("/")[-1]) for i in files]))
        # TODO: Show selected files on window

    def analyseAccounts(self):
        print("ANALYSIS")
        self.swapScreen()
        # TODO: Analyse accounts

    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select Accounts to Analyse", "",
                                                "All Files (*);;Python Files (*.py)", options=options)
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

        print(self.mainLayout.alignment())

        self.label = QLabel("Here are the results of the analysis")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("QLabel {color: grey;}")
        self.mainLayout.addWidget(self.label)

        self.mainLayout.addWidget(self.mainTopWidget)
        self.mainLayout.addWidget(self.mainBottomWidget)

        # Assign Layouts
        self.setLayout(self.mainLayout)
        self.mainTopWidget.setLayout(self.mainTopLayout)
        self.mainBottomWidget.setLayout(self.mainBottomLayout)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Combined()
    sys.exit(app.exec_())

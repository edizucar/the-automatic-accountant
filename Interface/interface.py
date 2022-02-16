import PyQt5


#!/usr/bin/python

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout


def main():

    app = QApplication(sys.argv)

    w = QWidget()
    w.resize(250, 150)
    w.move(300, 300)
    w.setWindowTitle('Automatic Accountant')
    layout = QVBoxLayout()
    layout.addWidget(QPushButton('Import Files'))
    layout.addWidget(QPushButton('Bottom'))
    w.setLayout(layout)
    w.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
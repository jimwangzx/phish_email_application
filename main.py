import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import json

import joblib
from bs4 import BeautifulSoup, SoupStrainer
import decodeEmail
import testPhishScore

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Phishing Detection Application")
        self.setGeometry(50, 50, 500, 300)
        
        
        layout = QVBoxLayout()

        title = QLabel("Enter a MHT file to check if phish or not")
        layout.addWidget(title)

        self.fileName = ""
        self.fileNameLabel = QLabel()
        layout.addWidget(self.fileNameLabel)

        file_btn = QPushButton("File", self)
        file_btn.clicked.connect(self.openFileNameDialog)
        # file_btn.setAlignment(Qt.AlignHCenter)
        layout.addWidget(file_btn)
        
        self.res_list = QListWidget()
        layout.addWidget(self.res_list)

        confirm_btn = QPushButton("Check", self)
        confirm_btn.clicked.connect(self.confirm)

        # confirm_btn.setAlignment(Qt.AlignHCenter)
        layout.addWidget(confirm_btn)

        self.phish_score = QLabel("Is Phish?")
        layout.addWidget(self.phish_score)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def openFileNameDialog(self):
        # options = QFileDialog.Options()
        self.fileName, _ = QFileDialog.getOpenFileName(self,"Choose the email to be tested", "","All Files (*);;Email files (*.mht);;Text files(*.txt)")
        name = 'File(s) path: ' + self.fileName
        self.fileNameLabel.setText(name)
        if self.fileName:
            print(name)
    
    def confirm(self):
        import re
        # import requests
        self.phish_score.setText("Is Phish?")
        self.res_list.clear()
        text = ''
        
        content = decodeEmail.findUrl(self.fileName)
        # print(content)
        for link in (BeautifulSoup(content).find_all('a', href=True)):
            print(link)
            url_res = re.search("(?P<url>https?://[^\s]+)", link['href'])
            if(url_res):
                # links.append(res.group("url"))
                url = url_res.group("url")
                newItem = QListWidgetItem()

                import pandas as pd
                df = pd.read_csv("phishtank.csv")
                if url in list(df["url"]):
                    text = url + " is in Phishtank."
                    newItem.setBackground(QColor("red"))
                else:
                    text = url + " is not in Phishtank."
                    
                newItem.setText(text)
                newItem.setHidden(False)
                self.res_list.addItem(newItem)

        
        content4model = ''
        try:
            f = open(self.fileName, "r", errors="ignore")
        except:
            f = open(self.fileName, "r", encoding="utf-8", errors="ignore")
        # bs_content=f.read()
        # print(f.read())
        bs_content = BeautifulSoup(f.read()).get_text()
        # print(bs_content)
        content4model = decodeEmail.oriParser(bs_content)
        # print(content4model)
        
        self.phish_score.setText("Is Phish?\t" + "Phish!" if(testPhishScore.predict(content4model)) else " Legit!!!!!" )
        # print(links) 
        
app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec_()
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
            url_res = re.search("(?P<url>https?://[^\s]+)", link['href'])
            if(url_res):
                # links.append(res.group("url"))
                url = url_res.group("url")
                import pandas as pd
                
                df = pd.read_csv("phishtank.csv")
                if url in df["url"]:
                    text = url + " is Phish."
                else:
                    text = url + " is not in Phishtank."
                # response = requests.post("http://checkurl.phishtank.com/checkurl/", params={"url":url, "format":"json", "__cf_chl_captcha_tk__":"cf92ed8dc174bccf3fafcbe52b284251580a6485-1618379888-0-AUFBr5sIcjEN5B7rcvUx86uCGHIOWV-gFrDMWDAMC6GpgwVoT89GqsmuahQmDR6--YJEQXMLFZDBkIwp_U_CJSJUC61BwMfWd0w15Zo4GxvvomfC8VLyXGcGmEVbPkMyLwW-TUEkJNeewN0mGbdCN98VU5IfRAvCjWvhjkf9l1Ci3aURoyVotOYx-E7pHHUvKE6-gPiQGaesFM-DSyL65OBWwtG4qIbFCJxsNRtL81g1NAhrvwNCVsqxvK1IyfPnWNz9XO5ukgnawrOPow1afJ0JbiUSdNx-gsaov_YcAjI1WCJ94zmGy9VEbxC3S3qo2hPZbdmQuuuvXBFfYdovJrDUFki7T67vRMIZXUOaULqrwqX5ra1zBihzkNcPPxg5epiTZj8luhJMDOl2whBp6BjLVbwYYMqhsUizYOWJp_nlldxI65jKKvrbW2qvo4wxnWMOdzm44zW52nToTEZQWs01RIyNgOlNPFh4gSoSBG4u5H5_gPqV9Fpb5LTIXp1j2LXHp9K7ND5bNPMcfKcYYNsUpCqC_UnyNoO7lwDT3w6acjF8u7IrDhJIiojtTEzXvii5YisRnglLhLfRlUWGK6RG6ovHM255cqbn79yeGDGu_TSDxw7WfysJMxCComu_--XQFt4GiVlXwykfcJDCJ96eXoB9dg2tl5xNxYPvyB0BV5shFLfQ8-P7KYShBc0kFw"})
                # print(response)
                # if(response.status_code == 200):
                #     res = json.load(response.json())
                #     if(res["in_database"] == 'y'):
                #         if(res["verified"] == 'y'):
                #             if(res["valid"] == 'y'):
                #                 text = url + " is Phish"
                #             else:
                #                 text = url + " is NOT Phish"
                #         else:
                #             text = url + " is not verified as Phish or not"
                #     else:
                #         text = url + " is not in database"
                # else:
                #     newItem = QListWidgetItem()
                #     newItem.setText("server went down")
                #     newItem.setHidden(False)
                #     self.res_list.addItem(newItem)
        newItem = QListWidgetItem()
        newItem.setText(text)
        newItem.setHidden(False)
        self.res_list.addItem(newItem)
        content4model = ''
        try:
            f = open(self.fileName, "r", errors="ignore")
        except:
            f = open(self.fileName, "r", encoding="utf-8", errors="ignore")
        # print(f.read())
        bs_content = BeautifulSoup(f.read()).get_text()
        # print(bs_content)
        content4model = decodeEmail.oriParser(bs_content)
        print(content4model)
        
        self.phish_score.setText("Is Phish?\t" + "Phish!"if(testPhishScore.predict(content4model)) else " Legit!!!!!" )
        # print(links) 
        




app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec_()
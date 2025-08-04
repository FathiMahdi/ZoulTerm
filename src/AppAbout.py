from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from about_zoulTerm import Ui_DialogAbout


# About
class DialogAbout(QDialog,Ui_DialogAbout):  
    def __init__(self):
        super(DialogAbout, self).__init__()
        self.setupUi(self)
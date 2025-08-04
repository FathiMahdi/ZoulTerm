from AppMain import *


if __name__ == '__main__':
    app = QApplication(sys.argv) 
    window = MyWindow()  
    window.show() 
    app.exec_()
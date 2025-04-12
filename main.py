import sys
import subprocess
import time
from PyQt5 import QtWidgets, QtCore, QtGui


from QT.QT_Main import Ui_MainPage

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Setup page
        self.ui = Ui_MainPage()
        self.ui.setupUi(self)



     

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
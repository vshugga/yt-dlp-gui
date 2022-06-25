# Old implementation
'''
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from qt_ui import Ui_MainWindow

app = QApplication(sys.argv)
window = QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(window)

window.show()
sys.exit(app.exec_())
'''

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
import sys
import qt_ui
import downloader

class App(QtWidgets.QMainWindow, qt_ui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.setupUi(self)
        self.ytDownloader = downloader.YtDownloader() 
        self.downloadButton.clicked.connect(self.downloadPressed)
    
    def downloadPressed(self):
        self.ytDownloader.url = self.urlInput.text()
        self.urlInput.clear()
        self.ytDownloader.download()


def main():
    app = QApplication(sys.argv)
    form = App()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
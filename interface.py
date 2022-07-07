from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QTableWidget
import sys
import downloader


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("main.ui", self)
        self.ytDownloader = downloader.YtDownloader()

        self.downloadTable.setColumnWidth(0,293)
        for i in range(1,5):
            self.downloadTable.setColumnWidth(i,111)


        self.downloadButton.clicked.connect(self.download_pressed)
        self.pathButton.clicked.connect(self.path_pressed)



    def download_pressed(self):
        # Check for valid url?
        self.ytDownloader.url = self.urlInput.text()
        self.urlInput.clear()

        self.ytDownloader.song_path = self.pathInput.text()

        # Possibly make new instance
        self.ytDownloader.download()

        # Use multiple YTDL instances for downloads (May cause problems writing to log files)
        # join() voids the purpose of multiprocessing, possibly run in downloader instead?

        # TODO: Download archive includes playlist url instead of individual vids
        
        # yt_process.join()
        

    def start_download():
        self.ytDownloader.download()


    def path_pressed(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)
        dir_name = dialog.getExistingDirectory(
            self,
            "Select Download Directory",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )

        if dir_name:
            self.pathInput.setText(dir_name)

    def update_table():
        pass
        #self.downloadTable.
        #QTableWidget.

def main():
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    try:
        app.exec_()
    except:
        print('Exiting')

if __name__ == "__main__":
    main()



# Old implementation
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from qt_ui import Ui_MainWindow

app = QApplication(sys.argv)
window = QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(window)

window.show()
sys.exit(app.exec_())
"""
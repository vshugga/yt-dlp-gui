from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from multiprocessing import Process, Lock
import sys
import downloader


class App(QMainWindow):
    def __init__(self):
        super(App, self).__init__()
        uic.loadUi("main.ui", self)

        self.ytDownloader = downloader.YtDownloader()

        self.downloadButton.clicked.connect(self.download_pressed)
        self.pathButton.clicked.connect(self.path_pressed)


    def download_pressed(self):
        # Check for valid url?
        self.ytDownloader.url = self.urlInput.text()
        self.ytDownloader.song_path = self.pathInput.text()

        self.urlInput.clear()

        # Use multiple YTDL instances for downloads (May cause problems writing to log files)
        # join() voids the purpose of multiprocessing, possibly run in downloader instead?
        lock = Lock()
        yt_process = Process(target=self.ytDownloader.download, args=(lock,)) 
        yt_process.start()
        # yt_process.join()
        

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


def main():
    app = QApplication(sys.argv)
    form = App()
    form.show()
    app.exec_()


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
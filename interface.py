from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QTableWidget, QWidget, QLabel, QVBoxLayout, QComboBox
import qt_ui

# from multiprocessing import Process, Lock
from threading import Thread, Lock
from time import sleep
import sys
import downloader
import table_info


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("main.ui", self)

        self.table_inf_obj = table_info.TableInfo()
        self.downloader = downloader.YtDownloader(self.table_inf_obj)
        self.format_box_disabled = [0, 1, 10]

        # Possibly start/control with downloads (don't update when not downloading)
        self.table_update_interval = 0.1
        update_table = Thread(target=self.table_updater)
        update_table.start()

        self.setup_ui()

        


    def setup_ui(self):
        self.downloadButton.clicked.connect(self.download_pressed)
        self.pathButton.clicked.connect(self.path_pressed)
        self.optionsButton.clicked.connect(self.show_options)

        for x in self.format_box_disabled:
            self.formatBox.model().item(x).setEnabled(False)

        #self.formatBox.setFrame(True)
        #self.formatBox.setPlaceholderText("--Choose Format--")
        #self.setEditable(False)
        #self.formatBox.setCurrentIndex(-1)
        #self.formatBox.currentText = "--Choose Format--"


        test_mode = True
        if test_mode:
            self.urlInput.setText("OyWbQwK65Qc")
            self.pathInput.setText("./test/download")

    def download_pressed(self):
        self.downloader.url = self.urlInput.text()
        self.downloader.song_path = self.pathInput.text()

        fformat, ex_audio = self.get_format_item()  
        if ex_audio:
            self.downloader.convert_video = ''
            self.downloader.audio_codec = fformat
            self.downloader.format = 'bestaudio/best'
            self.downloader.extract_audio = True
        else:
            self.downloader.convert_video = fformat
            self.downloader.format = 'bestvideo+bestaudio'
            self.downloader.extract_audio = False
            # self.downloader.preferredquality = something



        self.downloader.start_download_thread()
        self.urlInput.clear()

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

        



    def get_format_item(self):
        index = self.formatBox.currentIndex()
        ex_audio = False
        if index in self.format_box_disabled:
            raise Exception('Format not selected')
        if index > self.format_box_disabled[-1]:
            ex_audio = True

        text = self.formatBox.currentText()
        return text.strip(), ex_audio
        

    def show_options(self):
        print('Show Options')
        self.window = QMainWindow()
        uic.loadUi("options.ui", self.window)
        self.window.show()


    def table_updater(self):
        interval = self.table_update_interval
        while True:
            self.update_table()
            sleep(interval)

    # Update download table
    # Give each download a row ID?
    def update_table(self, row=0):

        # Possible new implementation:
        t_data = self.table_inf_obj.get_table_data()

        if len(t_data) < 1:
            return

        self.downloadTable.setRowCount(len(t_data))

        for r, row in enumerate(t_data):
            for c, col_str in enumerate(row):
                item = QtWidgets.QTableWidgetItem(col_str)
                self.downloadTable.setItem(r, c, item)



    




def main():


    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    try:
        app.exec_()
    except:
        print("Exiting")


if __name__ == "__main__":
    main()
    
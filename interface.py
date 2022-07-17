from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QTableWidget
#from multiprocessing import Process, Lock
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

        self.downloadButton.clicked.connect(self.download_pressed)
        self.pathButton.clicked.connect(self.path_pressed)

        # Possibly start/control with downloads (don't update when not downloading)
        self.table_update_interval = 0.1
        update_table = Thread(target=self.table_updater)
        update_table.start()


        test_mode = True
        if test_mode:
            self.urlInput.setText('OyWbQwK65Qc')
            self.pathInput.setText('./test/download')



    def download_pressed(self):
        self.downloader.url = self.urlInput.text()
        self.downloader.song_path = self.pathInput.text()

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

        #print(t_data)

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
        print('Exiting')

if __name__ == "__main__":
    main()


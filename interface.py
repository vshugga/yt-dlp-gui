from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QTableWidget
#from multiprocessing import Process, Lock
from threading import Thread, Lock
from time import sleep
import sys
import downloader

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("main.ui", self)

        test_mode = True

        if test_mode:
            self.urlInput.setText('OyWbQwK65Qc')
            self.pathInput.setText('./test/download')


        self.ytDownloader = downloader.YtDownloader()
        self.ytDownloader.table_updater = self.update_table


        #self.downloadTable.setColumnWidth(0,293)
        #for i in range(1,5):
        #    self.downloadTable.setColumnWidth(i,111)
        #self.update_table()

        self.downloadButton.clicked.connect(self.download_pressed)
        self.pathButton.clicked.connect(self.path_pressed)


        self.table_update_interval = 0.5
        update_table = Thread(target=self.table_updater)
        update_table.start()


    def download_pressed(self):
        input_url = self.urlInput.text()
        self.urlInput.clear()

        self.ytDownloader.song_path = self.pathInput.text()
        print(input_url)
        self.ytDownloader.start_download_thread(url=input_url) # Possibly make new instance?

        

        #self.ytDownloader.thread_test()
        

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
    # Probably have to use locks to prevent race conditions
    def update_table(self, row=0):

        hook = self.ytDownloader.hook
        if len(hook) < 1:
            return 

        if self.downloadTable.rowCount() <= row:
            self.downloadTable.setRowCount(row + 1)

        cols = [
            'title', 
            'completion', 
            'size', 
            'speed', 
            'downloaded', 
            'eta', 
            'status', 
            'elapsed'
        ]

        keys_needed = {
            'size':'_total_bytes_str',
            'eta':'eta',
            'speed':'speed',
            'elapsed':'_elapsed_str',
            'downloaded':'downloaded_bytes',
            'status':'status',
            'completion':'_percent_str'
        }
        
        row_dict = {
            'title':hook['info_dict']['title']
        }

        if hook['hook_type'] == 'postprocess':
            keys_needed['status'] = 'postprocessor'

        for key, value in keys_needed.items():
            if value in hook:
                row_dict[key] = str(hook[value])
                continue
            if value == 'eta' or value == 'speed':
                row_dict[key] = '-'


        #print('Update table:', table_data)
        #self.downloadTable.setRowCount(self.downloadTable.rowCount() + 1)
        #self.downloadTable.setRowCount(len(table_data))
        #for row, row_dict in enumerate(table_data):
        
        for col, col_key in enumerate(cols):
            if col_key in row_dict:
                self.downloadTable.setItem(row, col, QtWidgets.QTableWidgetItem(row_dict[col_key]))


            
        


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


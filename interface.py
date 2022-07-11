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


        self.downloadButton.clicked.connect(self.download_pressed)
        self.pathButton.clicked.connect(self.path_pressed)


        self.table_update_interval = 0.1
        update_table = Thread(target=self.table_updater)
        update_table.start()


    def download_pressed(self):
        input_url = self.urlInput.text()
        self.urlInput.clear()

        self.ytDownloader.song_path = self.pathInput.text()
        print(input_url)
        self.ytDownloader.start_download_thread(url=input_url) # Possibly make new instance?

        

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

        table_info = self.ytDownloader.table_info
        if len(table_info) < 1:
            return

        if self.downloadTable.rowCount() <= row:
            self.downloadTable.setRowCount(row + 1)


        # Data needed from hook dict
        keys_needed = {
            'info_dict':'info_dict',
            'hook_type':'hook_type',
            'size':'_total_bytes_str',
            'eta':'eta',
            'speed':'speed',
            'elapsed':'_elapsed_str',
            'downloaded':'downloaded_bytes',
            'status':'status',
            'completion':'_percent_str',
            'postprocessor':'postprocessor'
        }


        # If the needed keys are in hook, add to data dict
        data = {}
        for vid_dict in table_info.values():
            for key, value in keys_needed.items():
                if value in vid_dict:
                    data[key] = vid_dict[value]
                    continue
                if value == 'eta' or value == 'speed':
                    data[key] = '-'
        
        if 'info_dict' in data:
            data['title'] = data['info_dict']['title']
        if 'hook_type' in data and 'postprocessor' in data:
            if data['hook_type'] == 'postprocess':
                data['status'] = data['postprocessor']

        


        #print('Update table:', table_data)
        #self.downloadTable.setRowCount(self.downloadTable.rowCount() + 1)
        #self.downloadTable.setRowCount(len(table_data))
        #for row, row_dict in enumerate(table_data):
        
        # Columns to display in order
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

        for col, col_key in enumerate(cols):
            if col_key in data:
                self.downloadTable.setItem(row, col, QtWidgets.QTableWidgetItem(str(data[col_key])))


            
        


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


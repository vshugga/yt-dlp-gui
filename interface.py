from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QTableWidget
#from multiprocessing import Process, Lock
import sys
import downloader

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("main.ui", self)
        
        self.ytDownloader = downloader.YtDownloader()
        self.ytDownloader.table_updater = self.update_table


        #self.downloadTable.setColumnWidth(0,293)
        #for i in range(1,5):
        #    self.downloadTable.setColumnWidth(i,111)
        #self.update_table()

        self.downloadButton.clicked.connect(self.download_pressed)
        self.pathButton.clicked.connect(self.path_pressed)


    def download_pressed(self):
        url = self.urlInput.text()
        self.urlInput.clear()

        self.ytDownloader.song_path = self.pathInput.text()
        self.ytDownloader.start_download_thread(url) # Possibly make new instance?

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


    # Update download table
    # Give each download a row ID?
    def update_table(self, hook):

        table_data = [{
            'title':hook['info_dict']['title'],
            'size':hook["_total_bytes_str"],
            'eta':hook['eta'],
            'speed':hook['speed'],
            'elapsed':hook['_elapsed_str'],
            'downloaded':hook['downloaded_bytes'],
            'status':hook['status'],
            'completion':hook['_percent_str']
        }]

        #print('Update table:', table_data)
        #self.downloadTable.setRowCount(self.downloadTable.rowCount() + 1) # Why doesn't this work?

        self.downloadTable.setRowCount(len(table_data))
        for row, row_dict in enumerate(table_data):
            for col, key in enumerate(row_dict.keys()):
                self.downloadTable.setItem(row, col, QtWidgets.QTableWidgetItem(str(row_dict[key])))
        


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



'''
        row_data = [
            {
            'title':'TEST TITLE',
            'size':'TEST SIZE',
            'completion':'TEST COMPLETION',
            'eta':'TEST ETA',
            'speed':'TEST SPEED'
            },
            {
            'title':'TEST TITLE 2',
            'size':'TEST SIZE 2',
            'completion':'TEST COMPLETION 2',
            'eta':'TEST ETA 2',
            'speed':'TEST SPEED 2'
            }
        ]
        '''
        #print(table_data)
        #exit()

        #rowCount = self.ui.downloadTable.rowCount()


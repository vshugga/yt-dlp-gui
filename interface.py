from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QTableWidget
from multiprocessing import Process, Lock
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
        # Check for valid url?
        url = self.urlInput.text()
        self.urlInput.clear()

        self.ytDownloader.song_path = self.pathInput.text()
        self.ytDownloader.request_download(url) # Possibly make new instance?

        
        
        #self.ytDownloader.download()
        


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

    def update_table(self, table_data):

        '''
        if self.table_updater is None:
            print('Table update method not set!')
            return

        info = hook['info_dict']
        table_data = [{
            'title':info['title'],
            'size':hook["_total_bytes_str"],
            'eta':'TEST ETA',
            'speed':'TEST SPEED',
            'elapsed':hook['_elapsed_str'],
            'downloaded':hook['downloaded_bytes'],
            'status':hook['status'],
            'completion':hook['_percent_str']
        }]
        '''

        # Why is update table called but setting rowcount doesn't work?
        print('Update table')
        self.downloadTable.setRowCount(1) # Why doesn't this work?

        '''
        self.downloadTable.setRowCount(len(table_data))
        for row, row_dict in enumerate(table_data):
            for col, key in enumerate(row_dict.keys()):
                self.downloadTable.setItem(row, col, QtWidgets.QTableWidgetItem(row_dict[key]))
        '''


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
from PyQt5.QtCore import QThread, pyqtSignal

from time import sleep

class UpdateUIThread(QThread):

    def __init__(self, main_window):
        QThread.__init__(self)
        self.main_window = main_window
        

    def __del__(self):
        self.wait()

    '''
    def get_data_task(self):
        while True:
            self.main_window.update_table()
            self.main_window.get_errors()
            sleep(self.main_window.refresh_interval)
    '''

    def run(self):
        #self.get_data_task()
        while True:
            self.main_window.update_table()
            sleep(self.main_window.refresh_interval)

class DownloaderThread(QThread):
    def __init__(self, main_window):
        QThread.__init__(self)
        self.main_window = main_window

    def __del__(self):
        self.wait()

    def run(self):
        self.main_window.downloader._prep_download()
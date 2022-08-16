from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QTableWidget, QWidget, QLabel, QVBoxLayout, QComboBox, QMessageBox, QCheckBox, QButtonGroup
from PyQt5.QtCore import pyqtSignal
import qt_ui

# from multiprocessing import Process, Lock
from threading import Thread, Lock
from time import sleep
from thread_manager import UpdateUIThread, DownloaderThread
import sys
import downloader
import downloader_info


class MainWindow(QMainWindow):
    err_signal = pyqtSignal(str)
    table_signal = pyqtSignal(dict)


    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("main.ui", self)

        
        self.dl_info = downloader_info.DownloaderInfo()
        self.downloader = downloader.YtDownloader(self.dl_info, self.err_signal, self.table_signal)
        #self.downloader_thread = DownloaderThread(self)
        self.format_box_disabled = [0, 1, 10]

        # Possibly start/control with downloads (don't update when not downloading)
        self.refresh_interval = 0.1
        #data_refresher = Thread(target=self.get_data_task)
        #data_refresher.start()

        self.err_signal.connect(self.display_error)
        self.table_signal.connect(self.update_table)

        #self.data_refresh_thread = UpdateUIThread(self)
        #self.data_refresh_thread.start()

        self.setup_ui()

        
    def setup_ui(self):
        self.downloadButton.clicked.connect(self.download_pressed)
        self.pathButton.clicked.connect(self.path_pressed)


        self.optWindow = QMainWindow()
        uic.loadUi("options.ui", self.optWindow)
        self.optWindow.closeButton.clicked.connect(self.save_close_options)
        self.optWindow.archiveButton.clicked.connect(self.archive_path_pressed)
        self.optWindow.errorButton.clicked.connect(self.error_path_pressed)
        self.optionsButton.clicked.connect(self.optWindow.show)

        '''
        self.optWindow.radio_buttons = {
            self.optWindow.bestRB:'best',
            self.optWindow.worstRB:'worst',
            self.optWindow.bestVidRB:'bestvideo',
            self.optWindow.worstVidRB:'worstvideo',
            self.optWindow.bestAudioRB:'bestaudio',
            self.optWindow.worstAudioRB:'worstaudio'
        }
        '''

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

        try:
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
            #self.downloader_thread.start()
            self.urlInput.clear()

        except Exception as e:
            self.display_error(e)
        

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

    def error_path_pressed(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilter("Text files (*.txt)")
        if dialog.exec_():
            fname = dialog.selectedFiles()
            if fname[0]:
                self.optWindow.errorPath.setText(fname[0])

        #fname = dialog.getOpenFileName(self, "Select Error Log File")

    
    def archive_path_pressed(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilter("Text files (*.txt)")
        if dialog.exec_():
            fname = dialog.selectedFiles()
            if fname[0]:
                self.optWindow.archivePath.setText(fname[0])

        #fname = dialog.getOpenFileName(self, "Select Error Log File")


    def get_format_item(self):
        index = self.formatBox.currentIndex()
        ex_audio = False
        if index in self.format_box_disabled:
            raise Exception('Format not selected')
        if index > self.format_box_disabled[-1]:
            ex_audio = True

        text = self.formatBox.currentText()
        return text.strip(), ex_audio
        

    def save_close_options(self):
        archive_path = self.optWindow.archivePath.text()
        error_path = self.optWindow.errorPath.text()
        bitrate = self.optWindow.bitrateText.text()

        skip_archive = self.optWindow.skiparchiveBox.isChecked()
        embed_subs = self.optWindow.subtitleBox.isChecked()
        embed_thumb = self.optWindow.thumbnailBox.isChecked()
        embed_meta = self.optWindow.metadataBox.isChecked()
        
        '''
        for rb in self.optWindow.radio_buttons.keys():
            if rb.isChecked():
                self.downloader.format = self.optWindow.radio_buttons[rb]
                print(f'Format selected: {self.downloader.format}')
        '''

        self.downloader.download_archive = archive_path
        self.downloader.error_log = error_path
        self.downloader.audio_quality = bitrate

        self.downloader.skip_archived = skip_archive
        self.downloader.embed_subtitle = embed_subs
        self.downloader.embed_thumbnail = embed_thumb
        self.downloader.add_metadata = embed_meta

        self.optWindow.close()


    #@QtCore.pyqtSlot(str)
    def display_error(self, exception):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Error")
        msg_box.setText(f"{exception}")
        msg_box.exec()

    '''
    # Updates the table and checks for downloader errors every interval
    def get_data_task(self):
        while True:
            self.update_table()
            self.get_errors()
            sleep(self.get_data_interval)
    '''

    '''
    def get_errors(self):
        cur_error = self.dl_info.cur_dl_error
        if cur_error:
            #
            print('Error seen')
            self.downloader.thread_locker.acquire()
            self.display_error(cur_error)
            self.downloader.thread_locker.release()
            self.dl_info.cur_dl_error = None
    '''

    # Update download table
    # Give each download a row ID?
    def update_table(self, hook_dict):
        t_data = self.dl_info.get_table_data(hook_dict)
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
    
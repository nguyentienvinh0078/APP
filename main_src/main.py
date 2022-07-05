import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, c, QTableWidgetItem, QHeaderView, QSizePolicy, QAbstractScrollArea
from PyQt5.QtCore import Qt, QPoint, QThread, pyqtSignal

from app import Ui_MainWindow

class ThreadClassTikTokGetData(QThread):
    anySingal_download_btn = pyqtSignal(list)
    def __init__(self, index=0, tiktokUrl='', savePathFolder=''):
        super().__init__()
        self.index = index
        self.tiktok_url = tiktokUrl
        self.folder_path = savePathFolder
        self.isRunning = True
        self.tiktok = TikTok()

    def run(self):
        video_data_info = []
        video_data_info = self.tiktok.getVideoData(self.tiktok_url, self.folder_path)
        print('\n')
        print(f'+-------- START --------+')
        print(f'| Thread == {self.index}')
        print(f'+-------- START --------+')
        self.anySingal_download_btn.emit(video_data_info);

    def stop(self):
        print('\n')
        print(f'+-------- STOP --------+')
        print(f'| Thread == {self.index}')
        print(f'+-------- STOP --------+')
        self.isRunning = False
        self.terminate()

    def stop(self):
        print('\n')
        print(f'+-------- STOP --------+')
        print(f'| Thread == {self.index}')
        print(f'+-------- STOP --------+')
        self.isRunning = False
        self.terminate()

class ThreadClassDownload(QThread):
    anySingal_download = pyqtSignal(int)
    def __init__(self, index=0, video_data_info=[]):
        super().__init__()
        self.video_data_info = video_data_info
        self.index = index
        self.isRunning = True

        self.tiktok = TikTok()
    
    def run(self):
        print('\n')
        print(f'+-------- START --------+')
        print(f'| Thread == {self.index}')
        print(f'+-------- START --------+')
        data_length = len(self.video_data_info)
        for i_count in range(data_length):
            try:
                self.tiktok.download([self.video_data_info[i_count]])
                self.anySingal_download.emit(i_count);
            except:
                self.anySingal_download.emit(-999);

    def stop(self):
        print('\n')
        print(f'+-------- STOP --------+')
        print(f'| Thread == {self.index}')
        print(f'+-------- STOP --------+')
        self.isRunning = False
        self.terminate()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.uic = Ui_MainWindow()
        self.uic.setupUi(self)

        self.tiktok = TikTok()
        self.list_test_url = [
            'https://www.tiktok.com/@yenkim07022004__',
            'https://www.tiktok.com/@yenkim07022004__?is_from_webapp=1&sender_device=pc',
            'https://vt.tiktok.com/ZSdgm4UNs/',

            'https://www.tiktok.com/@yenkim07022004__/video/7104196143575239962?is_from_webapp=1&sender_device=pc&web_id=7077083055764915713',
            'https://www.tiktok.com/@yenkim07022004__/video/7104489383570509083?is_copy_url=1&is_from_webapp=v1',
            'https://vt.tiktok.com/ZSdgmCNn2/?k=1',
        ]
        self.threads = {}

        self.uic.folder_line_edit.setText(self.getRootDir())
        self.uic.url_line_edit.setText(self.list_test_url[0])

        self.uic.folder_btn.clicked.connect(self.folder_btn_callback)
        self.uic.download_btn.clicked.connect(self.download_btn_callback)

    def download_btn_callback(self):
        def get_video_data_function(video_data_info):
            print(video_data_info)
            self.uic._03msg_frame.setMaximumHeight(0)
            self.uic._04main_frame.setMinimumHeight(500)

            self.row_number = len(video_data_info)
            self.uic.table_content.setRowCount(self.row_number)
            self.column_number = 4
            self.uic.table_content.setColumnCount(self.column_number)

            for row in range(self.row_number): 
                self.uic.table_content.setItem(row, 0, QTableWidgetItem(video_data_info[row]['videoNumber']))   
                self.uic.table_content.setItem(row, 1, QTableWidgetItem(video_data_info[row]['videoId']))   
                self.uic.table_content.setItem(row, 2, QTableWidgetItem(video_data_info[row]['videoUrlNoWatermark']))   

            def download_function(cnt):
                row = cnt
                status = 'Thành công' if row >= 0 else 'Không thành công'
                self.uic.table_content.setItem(row, 3, QTableWidgetItem(status))   
                if cnt == len(video_data_info)-1:
                    self.threads[self.thread_download].stop()

            self.thread_download = 'thread_download'
            self.threads[self.thread_download] = ThreadClassDownload(index=self.thread_download, video_data_info=video_data_info)
            self.threads[self.thread_download].start()
            self.threads[self.thread_download].anySingal_download.connect(download_function)

            self.threads[self.thread_data].stop()

        self.thread_data = 'download_click'
        self.uic._03msg_frame.setMaximumHeight(50)
        tiktok_url = self.uic.url_line_edit.text()
        folder_path = self.uic.folder_line_edit.text()
        self.threads[self.thread_data] = ThreadClassTikTokGetData(index=self.thread_data, tiktokUrl=tiktok_url, savePathFolder=folder_path)
        self.threads[self.thread_data].start()
        self.threads[self.thread_data].anySingal_download_btn.connect(get_video_data_function)

    def folder_btn_callback(self):
        save_path = QFileDialog.getExistingDirectory(self, 'Select Folder', self.getRootDir())
        if save_path:
            self.uic.folder_line_edit.setText(save_path)
        else:
            self.uic.folder_line_edit.setText(self.getRootDir())

    def getRootDir(selef):
        rootPath = ''
        if getattr(sys, 'frozen', False):
            rootPath = os.path.dirname(sys.executable)
        else:
            try:
                rootPath = os.path.dirname(os.path.realpath(__file__))
            except NameError:
                rootPath = os.getcwd()
        return rootPath 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
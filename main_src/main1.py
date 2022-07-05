import sys, os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem
from PyQt5.QtCore import Qt, QPoint, QThread, pyqtSignal

from demo import Ui_MainWindow
from base_src.Base_APP import Base_APP
from base_src.TikTok import TikTok

class ThreadGetVideoData(QThread):
    send_data_signal = pyqtSignal(list)
    def __init__(self, url, index=0):
        super().__init__()
        self.index = index
        self.isRunning = True
        self.url = url
        self.tiktok = TikTok()
    
    def run(self):
        video_data = []
        video_data = self.tiktok.get_video_data(self.url)
        print('\n')
        print(f'+-------- START --------+')
        print(f'| Thread == {self.index}')
        print(f'+-------- START --------+')
        self.send_data_signal.emit(video_data);

    def stop(self):
        print('\n')
        print(f'+-------- STOP --------+')
        print(f'| Thread == {self.index}')
        print(f'+-------- STOP --------+')
        self.isRunning = False
        self.terminate()

class ThreadDownload(QThread):
    download_signal = pyqtSignal(list)
    def __init__(self, video_data, index=0):
        super().__init__()
        self.index = index
        self.isRunning = True
        self.video_data = video_data
        self.tiktok = TikTok()
    
    def run(self):
        print('\n')
        print(f'+-------- START --------+')
        print(f'| Thread == {self.index}')
        print(f'+-------- START --------+')

        for data in self.video_data:
            self.tiktok.download([data])
            self.download_signal.emit([data]);

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
        self.root_dir = os.path.abspath(os.path.dirname(__file__))
        self.base_app = Base_APP()

        self.threads = {}

        self.url_list_data = [
            'https://www.tiktok.com/@yenkim07022004__',
            'https://www.tiktok.com/@yenkim07022004__?is_from_webapp=1&sender_device=pc',
            'https://vt.tiktok.com/ZSdgm4UNs/',

            'https://www.tiktok.com/@yenkim07022004__/video/7104196143575239962?is_from_webapp=1&sender_device=pc&web_id=7077083055764915713',
            'https://www.tiktok.com/@yenkim07022004__/video/7104489383570509083?is_copy_url=1&is_from_webapp=v1',
            'https://vt.tiktok.com/ZSdgmCNn2/?k=1',
        ]
        
        self.show_msg(show=False)
        # self.uic.header.setMaximumHeight(0)
        ## ========== HEADER ===========
        # self.setWindowFlag(Qt.FramelessWindowHint)
        # self.uic.close_btn.clicked.connect(lambda: self.close())
        # self.uic.max_btn.setDisabled(True)
        # self.uic.min_btn.clicked.connect(lambda: self.showMinimized())
        self.uic.url.setText(self.url_list_data[0])
        self.uic.save_path.setText(self.root_dir)
        self.folder_config()
        self.url_config()

    def url_config(self):
        def download_btn_callback():
            self.show_msg()
            self.uic.get_path_btn.setDisabled(True)
            self.uic.save_path.setDisabled(True)
            self.uic.url.setDisabled(True)
            self.uic.download_btn.setDisabled(True)

            #============================================================================
            def download_function(video_data):
                self.show_msg(show=False)
                self.row_number = len(video_data)
                self.uic.table_content.setRowCount(self.row_number)
                self.column_number = 4
                self.uic.table_content.setColumnCount(self.column_number)
                #========================================================================
                def download(data):
                    row = int(data[0]['video_index'])
                    self.uic.table_content.setItem(row, 0, QTableWidgetItem(data[0]['video_index']))   
                    self.uic.table_content.setItem(row, 1, QTableWidgetItem(data[0]['video_id']))   
                    self.uic.table_content.setItem(row, 2, QTableWidgetItem(data[0]['url_nowatermark']))   
                    self.uic.table_content.setItem(row, 3, QTableWidgetItem('True'))

                    if int(row) == len(video_data):
                        self.uic.get_path_btn.setDisabled(False)
                        self.uic.save_path.setDisabled(False)
                        self.uic.url.setDisabled(False)
                        self.uic.download_btn.setDisabled(False)
                        self.threads[0].stop()
                        self.threads[1].stop()

                self.threads[1] = ThreadDownload(video_data=video_data, index=1)
                self.threads[1].start()
                self.threads[1].download_signal.connect(download)
                #========================================================================
                
            self.threads[0] = ThreadGetVideoData(url=self.uic.url.text(), index=0)
            self.threads[0].start()
            self.threads[0].send_data_signal.connect(download_function)
            #============================================================================

        self.uic.download_btn.clicked.connect(download_btn_callback)

    def show_msg(self, show=True, msg='...Đang lấy dữ liệu vui lòng đợi...'):
        if show: 
            self.uic.fmsg.setMaximumHeight(50)
            self.uic.msg.setText(msg)
        else: 
            self.uic.fmsg.setMaximumHeight(0)
            self.uic.msg.setText(msg)

    def folder_config(self):
        def get_path_btn_callback():
            path_dir = QFileDialog.getExistingDirectory(self, 'Select Folder', self.root_dir)
            if path_dir:
                self.uic.save_path.setText(path_dir)
        self.uic.get_path_btn.clicked.connect(get_path_btn_callback)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
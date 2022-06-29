import sys, time, os
from threading import Timer
from PyQt5 import QtTest
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import Qt, QPoint, QThread, pyqtSignal

from TikTok import *
from gui import Ui_MainWindow

class ThreadClass(QThread):
    anySingal = pyqtSignal(int)
    def __init__(self, index=0):
        super().__init__()
        self.index = index
        self.isRunning = True
    
    def run(self):
        check_pressed = True
        print('\n')
        print(f'+-------- START --------+')
        print(f'| Thread == {self.index}')
        print(f'+-------- START --------+')
        self.anySingal.emit(check_pressed);

    def stop(self):
        print('\n')
        print(f'+-------- STOP --------+')
        print(f'| Thread == {self.index}')
        print(f'+-------- STOP --------+')
        self.isRunning = False
        self.terminate()

class ThreadClassTikTokGetData(QThread):
    anySingal_search = pyqtSignal(list)
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
        self.anySingal_search.emit(video_data_info);

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
        check_pressed = True
        print('\n')
        print(f'+-------- START --------+')
        print(f'| Thread == {self.index}')
        print(f'+-------- START --------+')
        data_length = len(self.video_data_info)
        for i_count in range(data_length):
            self.tiktok.download([self.video_data_info[i_count]])
            self.anySingal_download.emit(i_count);

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

        #======== border green color all =============
        self.style_border_green = "border: 2px solid rgb(12, 245, 12);"
        self.style_border_red = "border: 2px solid rgb(236, 30, 85);"

        #======== border bottom green color =============
        self.style_border_bottom_green = "border-bottom: 2px solid rgb(12, 245, 12);"
        self.style_border_bottom_red = "border-bottom: 2px solid rgb(236, 30, 85);"

        #======== min, max of height for side menu =============
        self.side_menu_min_height = 42
        self.side_menu_max_height = 180

        #======== min, max of height for side control =============
        self.side_control_min_height = 42
        self.side_control_max_height = 180

        #======== min, max of height for folder save frame =============
        self.folder_save_min_height = 0
        self.folder_save_max_height = 50

        #======== min, max of height for search frame =============
        self.search_min_height = 0
        self.search_max_height = 50

        #======== min, max of height for data notification frame =============
        self.wait_notification_min_height = 0
        self.wait_notification_max_height = 50

        #======== min, max of height for main content =============
        self.main_content_min_height = 0
        self.main_content_max_height = 600

        #======== create dict value self.threads for save threads =============
        self.threads = {}

        #======== create list value self.video_data_info for save datas of url =============
        self.video_data_info = []

        #===== hide data notification =====
        self.hide_show_wait_notification(is_hide=True)
        self.hide_show_main_content(is_hide=True)

        #====== remove maximize, minimize, close of default window ========= 
        self.setWindowFlag(Qt.FramelessWindowHint)
        #===== header config function =====
        self.header_config()
        #===== side control config function =====
        self.side_control_config()
        #===== side menu config function =====
        self.side_menu_config()
        #===== main content config function =====
        self.main_content_config()


    def main_content_config(self):
        # ============== Disable start_btn, stop_btn =============
        self.uic._02222start_btn.setDisabled(True)
        self.uic._02223stop_btn.setDisabled(True)

        self.uic._02221search_url_input.setText(self.list_test_url[0])
        
        #============== SEARCH BTN =====================================
        self.search_clicked = False
        def search_btn_callback():
            thread_index = 'search_btn'
            def search_btn_function(check_pressed):
                index = self.sender().index
                if index == thread_index:
                    if check_pressed:
                        # ============== Disable folder_path, folder_btn =============
                        self.uic._02221folder_path.setDisabled(True)
                        self.uic._02221folder_path.setStyleSheet(self.style_border_green)
                        self.uic._02212folder_btn.setDisabled(True)
                        self.uic._02212folder_btn.setStyleSheet(self.style_border_green)

                        # ============== Disable start_btn, stop_btn =============
                        self.uic._02222start_btn.setDisabled(True)
                        self.uic._02223stop_btn.setDisabled(True)

                        # ============== Disable search_btn, and set border green =============
                        self.uic._02222search_btn.setDisabled(True)
                        self.uic._02222search_btn.setStyleSheet(self.style_border_green)

                        # ============== Disable search line edit input, and set border green =============
                        self.uic._02221search_url_input.setDisabled(True)
                        self.uic._02221search_url_input.setStyleSheet(self.style_border_green)

                        # ============== Show get data notification =============
                        self.hide_show_wait_notification(is_hide=False)
                        
                        self.search_clicked = True
                        if self.search_clicked:
                            thread_search = 'search_clicked'
                            def search_clicked_function(video_data_info):
                                self.video_data_info = video_data_info
                                print(self.video_data_info)

                                self.uic._02222start_btn.setDisabled(False)
                                self.uic._02224edit_folder_btn.setDisabled(False)
                                self.uic._02222wait_msg.setText('...Lấy dữ liệu thành công...')
                            
                                # ============== Show get data notification =============
                                self.hide_show_wait_notification(is_hide=True)

                                # ============== Show main content ================
                                self.hide_show_main_content(is_hide=False)
                                self.uic._02231table_content.setHorizontalHeaderLabels(['VIDEO ID', 'LINK NOWATERMARK', 'STATUS'])

                                
                                thread_download = 'download_function'
                                def download_function(i_count):
                                    count = i_count
                                    if count == len(self.video_data_info) - 1:
                                        self.threads[thread_download].stop()
                                        # ============== Disable folder_path, folder_btn =============
                                        self.uic._02221folder_path.setDisabled(False)
                                        self.uic._02221folder_path.setStyleSheet(self.style_border_red)
                                        self.uic._02212folder_btn.setDisabled(False)
                                        self.uic._02212folder_btn.setStyleSheet(self.style_border_red)

                                        # ============== Disable start_btn, stop_btn =============
                                        self.uic._02222start_btn.setDisabled(False)
                                        self.uic._02223stop_btn.setDisabled(False)

                                        # ============== Disable search_btn, and set border green =============
                                        self.uic._02222search_btn.setDisabled(False)
                                        self.uic._02222search_btn.setStyleSheet(self.style_border_red)

                                        # ============== Disable search line edit input, and set border green =============
                                        self.uic._02221search_url_input.setDisabled(False)
                                        self.uic._02221search_url_input.setStyleSheet(self.style_border_red)

                                #======== download threads ===========
                                self.threads[thread_download] = ThreadClassDownload(index=1, video_data_info=self.video_data_info)
                                self.threads[thread_download].start()
                                self.threads[thread_download].anySingal_download.connect(download_function)

                                self.threads[thread_search].stop()
                            
                            tiktokUrl = self.uic._02221search_url_input.text()   
                            savePathFolder = self.uic._02221folder_path.text() 

                            self.threads[thread_search] = ThreadClassTikTokGetData(index=thread_search, tiktokUrl=tiktokUrl, savePathFolder=savePathFolder)
                            self.threads[thread_search].start()
                            self.threads[thread_search].anySingal_search.connect(search_clicked_function)

                    self.threads[thread_index].stop()
            
            self.threads[thread_index] = ThreadClass(index=thread_index)
            self.threads[thread_index].start()
            self.threads[thread_index].anySingal.connect(search_btn_function)

        self.uic._02222search_btn.clicked.connect(search_btn_callback)
        #============== SEARCH BTN =====================================

        #============== EDIT FOLDER BTN =====================================
        self.edit_folder_is_open = True
        def edit_folder_callback():
            thread_index = 'edit_folder'
            def edit_folder_function(check_pressed):
                index = self.sender().index
                if index == thread_index:
                    if check_pressed:
                        if self.edit_folder_is_open:
                            self.edit_folder_is_open = False
                            self.uic._02224edit_folder_btn.setStyleSheet(self.style_border_bottom_red)
                            self.hide_show_folder_save(is_hide=True)
                            self.threads[thread_index].stop()
                        else:
                            self.edit_folder_is_open = True
                            self.hide_show_folder_save(is_hide=False)
                            self.uic._02224edit_folder_btn.setStyleSheet(self.style_border_bottom_green)

            self.threads[thread_index] = ThreadClass(index=thread_index)
            self.threads[thread_index].start()
            self.threads[thread_index].anySingal.connect(edit_folder_function)

        self.uic._02224edit_folder_btn.clicked.connect(edit_folder_callback)
        #============== EDIT FOLDER BTN =====================================

        #============== FOLDER BTN =====================================
        self.uic._02221folder_path.setText(self.get_root_dir())
        def folder_btn_callback():
            thread_index = 'folder_btn'
            def folder_btn_function(check_pressed):
                index = self.sender().index
                if index == thread_index:
                    if check_pressed:
                        save_path = QFileDialog.getExistingDirectory(self, 'Select Folder', self.get_root_dir())
                        if save_path:
                            self.uic._02221folder_path.setText(save_path)
                        else:
                            self.uic._02221folder_path.setText(self.get_root_dir())
                            
                    self.threads[thread_index].stop()

            self.threads[thread_index] = ThreadClass(index=thread_index)
            self.threads[thread_index].start()
            self.threads[thread_index].anySingal.connect(folder_btn_function)

        self.uic._02212folder_btn.clicked.connect(folder_btn_callback)
        #============== FOLDER BTN =====================================

    def hide_show_side_menu(self, is_hide=True):
        if is_hide:
            self.uic._021side_menu.setMinimumWidth(self.side_menu_min_height)
        else:
            self.uic._021side_menu.setMinimumWidth(self.side_menu_max_height)

    def side_menu_config(self):
        self.is_small_menu = True
        self.hide_show_side_menu(is_hide=True)
        def show_side_menu_btn_callback():
            if self.is_small_menu:
                self.is_small_menu = False
                self.hide_show_side_menu(is_hide=False)
            else:
                self.is_small_menu = True
                self.hide_show_side_menu(is_hide=True)

        self.uic._02111show_side_menu_btn.clicked.connect(show_side_menu_btn_callback)

        def start_btn_callback():
            thread_index = 'start_btn'
            def start_btn_function(check_pressed):
                index = self.sender().index
                if index == thread_index:
                    if check_pressed:
                        self.uic._02222start_btn.setDisabled(True)
                        self.uic._02222start_btn.setStyleSheet(self.style_border_bottom_green)
                        self.uic._02223stop_btn.setDisabled(False)
                        self.uic._02223stop_btn.setStyleSheet(self.style_border_bottom_red)
                        self.hide_show_main_content(is_hide=False)

            self.threads[thread_index] = ThreadClass(index=thread_index)
            self.threads[thread_index].start()
            self.threads[thread_index].anySingal.connect(start_btn_function)

        self.uic._02222start_btn.clicked.connect(start_btn_callback)

        def stop_btn_callback():
            thread_index = 'start_btn'
            self.uic._02222start_btn.setDisabled(False)
            self.uic._02222start_btn.setStyleSheet(self.style_border_bottom_red)
            self.uic._02223stop_btn.setDisabled(True)
            self.uic._02223stop_btn.setStyleSheet(self.style_border_bottom_green)
            self.threads[thread_index].stop()
        self.uic._02223stop_btn.clicked.connect(stop_btn_callback)

    def hide_show_folder_save(self, is_hide):
        if is_hide:
            self.uic._0221folder_save.setMaximumHeight(self.folder_save_min_height)
        else:
            self.uic._0221folder_save.setMaximumHeight(self.folder_save_max_height)

    def hide_show_wait_notification(self, is_hide):
        if is_hide:
            self.uic._0222wait_notification.setMaximumHeight(self.wait_notification_min_height)
        else:
            self.uic._0222wait_notification.setMaximumHeight(self.wait_notification_max_height)

    def hide_show_main_content(self, is_hide=True):
        if is_hide:
            self.uic._0223main_content.setMinimumHeight(self.main_content_min_height)
        else:
            self.uic._0223main_content.setMinimumHeight(self.main_content_max_height)

    def header_config(self):
        def minimize_btn_callback():
            self.showMinimized()

        def close_btn_callback():
            self.close()

        self.is_minimize_window = True
        def resize_window():
            if self.is_minimize_window:
                self.is_minimize_window = False
                self.showMaximized()
            else:
                self.is_minimize_window = True
                self.showNormal()

        def mousePress(event):
            self.oldPosition = event.globalPos()
        def mouseMove(event):
            delta = QPoint(event.globalPos() - self.oldPosition)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPosition = event.globalPos()

        def mouseDoubleClickEvent(event):
            resize_window()

        self.uic._01header.mousePressEvent = mousePress
        self.uic._01header.mouseMoveEvent = mouseMove
        self.uic._01header.mouseDoubleClickEvent = mouseDoubleClickEvent

        self.uic._0121minimize_btn.clicked.connect(minimize_btn_callback)
        self.uic._0122maximize_btn.clicked.connect(resize_window)
        self.uic._0123close_btn.clicked.connect(close_btn_callback)


    def hide_show_side_control(self, is_hide=True):
        if is_hide:
            self.uic._0222side_control.setMinimumWidth(self.side_control_min_height)
        else:
            self.uic._0222side_control.setMinimumWidth(self.side_control_max_height)

    def side_control_config(self):
        self.is_small_control = True
        self.hide_show_side_control(is_hide=True)
        def show_side_control_btn_callback():
            if self.is_small_control:
                self.is_small_control = False
                self.hide_show_side_control(is_hide=False)
            else:
                self.is_small_control = True
                self.hide_show_side_control(is_hide=True)

        self.uic._02221show_control_btn.clicked.connect(show_side_control_btn_callback)

    def get_root_dir(selef):
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
from PyQt5.QtCore import  (
    QThread,
    pyqtSignal
)

class ThreadClass(QThread):
    any_signal = pyqtSignal(str)
    def __init__(self, index=0):
        super().__init__()
        self.index = index
        self.isRunning = True
    
    def run(self):
        self.any_signal.emit(self.index);
        pass
        

    def stop(self):
        self.isRunning = False
        self.terminate()

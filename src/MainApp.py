import logging
from PyQt5 import QtCore, QtWidgets

from LocalStorage import LocalStorage
from MainWindow import MainWindow
import env

class MainApp(QtWidgets.QApplication):

    def __init__(self):
        super().__init__([])
        self.localStorage = LocalStorage.load(env.LOCAL_STORAGE)
        self.mainWindow = MainWindow()
        self.mainWindow.ui.actionExit.triggered.connect(self.exit)

    def start(self):
        self.mainWindow.show()
        super().exec()
        self.mainWindow.close()
        self.localStorage.save(env.LOCAL_STORAGE)

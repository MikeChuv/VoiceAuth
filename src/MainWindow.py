import logging
from PyQt5 import QtWidgets, QtCore, QtGui

import env
from NewUserWindow import NewUserWindow
from AboutWindow import AboutWindow
from UserAccount import Admin
from QRecorder import QRecorder
from MixtureChecker import MixtureChecker
from AdminWindow import AdminWindow
from LocalStorage import LocalStorage

from ui.ui_mainWindow import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.messageBox = QtWidgets.QMessageBox(self)

        # New User (change speech data) window
        self.newUserWindow = NewUserWindow(self)
        self.newUserWindow.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.newUserWindow.onExit.connect(self.updateLocalStorage)

        # About Window
        self.aboutWindow = AboutWindow(self)
        self.aboutWindow.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.ui.actionAbout.triggered.connect(self.aboutWindow.show)

        # Admin window
        self.adminWindow = AdminWindow(self)
        self.ui.actionEnterAdmin.triggered.connect(self.adminWindow.show)
        self.adminWindow.onExit.connect(self.updateLocalStorage)
        
        self.ui.recordBtn.setEnabled(False)
        self.ui.actionNewUser.triggered.connect(self.newUserWindow.enterCreate)
        self.ui.loginEdit.editingFinished.connect(self.processLogin)

        self._localStorage = LocalStorage()
        self._users = self._localStorage.users
        self._recorder = QRecorder(env.SECONDS)

        self.ui.recordBtn.clicked.connect(self.startRecordingWrapper)
        self._recorder.audioInput.notify.connect(self.updateProgress)
        self._recorder.onRecorded.connect(self.processRecorded)


    @QtCore.pyqtSlot()
    def updateLocalStorage(self):
        self._localStorage = LocalStorage()
        self._users = self._localStorage.users

    @QtCore.pyqtSlot()
    def startRecordingWrapper(self):
        self.processLogin()
        self._recorder.startRecording()

    @QtCore.pyqtSlot()
    def processLogin(self):
        _currentLogin = self.ui.loginEdit.text()
        logging.info(f'[MainWindow] Entered login: {_currentLogin}')
        if _currentLogin == '':
            return
        if _currentLogin not in self._users:
            self.ui.recordBtn.setEnabled(False)
            self.messageBox.setText(f'No user with login: {_currentLogin}')
            self.messageBox.show()
            self.ui.loginEdit.clear()
            return
        # and _currentLogin in self._users \
        if _currentLogin == env.DEFAULT_ADMIN \
                and isinstance(self._users[_currentLogin], Admin) \
                and not self._users[_currentLogin].hasSpeechData():
            logging.info(f'[MainWindow] ADMIN {_currentLogin} should record some voice!')
            self.adminWindow.enter(_currentLogin)
            return
        if _currentLogin in self._users and not self._users[_currentLogin].hasSpeechData():
            logging.info(f'[MainWindow] User {_currentLogin} should record some voice!')
            self.newUserWindow.enterUpdate(_currentLogin)
            return
        self._currentLogin = _currentLogin
        self.ui.recordBtn.setEnabled(True)

    @QtCore.pyqtSlot()
    def updateProgress(self):
        val = self._recorder.getProgressInPercents()
        self.ui.recordProgress.setValue(val)

    @QtCore.pyqtSlot(QtCore.QByteArray)
    def processRecorded(self, array: QtCore.QByteArray):
        self._checker = MixtureChecker()
        self.ui.recordProgress.setValue(100)
        logging.info(f'[MainWindow] Audio is recorded, processing...')
        self._checker.setUser(self._currentLogin)
        areSame = self._checker.compareWithPCM(array)
        array.clear()
        if areSame:
            if isinstance(self._users[self._currentLogin], Admin):
                self.adminWindow.enter(self._currentLogin)
            else:
                self.newUserWindow.enterUpdate(self._currentLogin)
            self.ui.loginEdit.clear()
            self.ui.recordProgress.setValue(0)
        else:
            self.messageBox.setText(f'Проверка голоса не пройдена!')
            self.messageBox.show()

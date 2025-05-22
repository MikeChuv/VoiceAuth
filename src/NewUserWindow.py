import typing
import numpy
import logging
import soundfile
import sklearn.mixture
from enum import IntEnum
import time

from PyQt5 import QtWidgets, QtCore, QtGui

from ui.ui_newUser import Ui_newUserWindow
from UserAccount import UserAccount
from Users import Users
from QRecorder import QRecorder
from Extractor import MFCCExtractor, DeltasExtractor
from LocalStorage import LocalStorage
import env


class NewUserWindow(QtWidgets.QMainWindow):

    class Mode(IntEnum):
        USER_NEW    = 0
        USER_UPDATE = 1

    onExit = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(NewUserWindow, self).__init__(parent)

        self.ui = Ui_newUserWindow()
        self.ui.setupUi(self)
        
        self.messageBox = QtWidgets.QMessageBox(self)

        self._remainingRecords = 3
        self._mfccsAcc = []
        self._deltasAcc = []

        self.ui.recordBtn.setEnabled(False)
        self.ui.loginEdit.editingFinished.connect(self.processLogin)
        # self.ui.remainingRecordsLabel.setText(str(self._remainingRecords))

        self._recorder = QRecorder(env.SECONDS)
        self._mfccsExtractor = MFCCExtractor()
        self._deltasExtractor = DeltasExtractor()

        self.btnSave = self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Save)
        self.ui.buttonBox.accepted.connect(self.saveAndClose)
        self.ui.buttonBox.rejected.connect(self.close)

        self.ui.recordBtn.clicked.connect(self._recorder.startRecording)
        self._recorder.audioInput.notify.connect(self.updateProgress)
        self._recorder.onRecorded.connect(self.processRecorded)

    @QtCore.pyqtSlot()
    def updateProgress(self):
        r'''visualize recording progress'''
        val = self._recorder.getProgressInPercents()
        self.ui.recordProgress.setValue(val)


    @QtCore.pyqtSlot()
    def enterCreate(self):
        self.mode = NewUserWindow.Mode.USER_NEW
        self._localStorage = LocalStorage()
        self._remainingRecords = self._localStorage.recordsCount
        self.ui.remainingRecordsLabel.setText(str(self._remainingRecords))
        self._users = self._localStorage.users
        self.btnSave.setEnabled(False)
        self.ui.loginEdit.setEnabled(True)
        self.show()

    
    @QtCore.pyqtSlot(str)
    def enterUpdate(self, login : str):
        self.mode = NewUserWindow.Mode.USER_UPDATE
        self._localStorage = LocalStorage()
        self._remainingRecords = self._localStorage.recordsCount
        self.ui.remainingRecordsLabel.setText(str(self._remainingRecords))
        self._users = self._localStorage.users
        self.btnSave.setEnabled(False)
        self.show()
        self.ui.loginEdit.setText(login)
        self.ui.loginEdit.setEnabled(False)
        self.processLogin()


    @QtCore.pyqtSlot()
    def saveAndClose(self):
        mfccsList = self.__trimFeatures(self._mfccsAcc)
        deltasList = self.__trimFeatures(self._deltasAcc)
        featuresList = [numpy.vstack(f) for f in zip(mfccsList, deltasList)]
        train = numpy.hstack(featuresList).T
        gmm = sklearn.mixture.GaussianMixture(n_components=1, max_iter=200, n_init=3)
        gmm.fit(train)
        means = numpy.squeeze(gmm.means_)
        cov = numpy.squeeze(gmm.covariances_)
        distList = [env.mahalanobis(x, means, numpy.linalg.inv(cov)) for x in train]
        trainMeanDist = numpy.mean(distList)
        logging.info(f'[NewUserWindow] Mean train err {trainMeanDist}')
        if self.mode == NewUserWindow.Mode.USER_NEW:
            self._users[self._currentLogin] = UserAccount(self._currentLogin, gmm, trainMeanDist)
        elif self.mode == NewUserWindow.Mode.USER_UPDATE:
            self._users[self._currentLogin].speechData = gmm
            self._users[self._currentLogin].trainMeanDistance = trainMeanDist
        self.onExit.emit()
        self.close()


    @QtCore.pyqtSlot()
    def processLogin(self):
        self._currentLogin = self.ui.loginEdit.text()
        logging.info(f'[NewUserWindow] Entered login: {self._currentLogin}')
        if self.mode == NewUserWindow.Mode.USER_NEW and self._currentLogin in self._users:
            self.messageBox.setText(f'User with login {self._currentLogin} already exists!')
            self.messageBox.show()
            return
        if self.mode == NewUserWindow.Mode.USER_UPDATE and self._currentLogin not in self._users:
            self.messageBox.setText(f'No user with login {self._currentLogin}')
            self.messageBox.show()
            return
        self.ui.recordBtn.setEnabled(True) # now we can record audio for a new user


    def __trimFeatures(self, featureList : typing.List[numpy.ndarray]) -> typing.List[numpy.ndarray]:
        r'''trims each feature matrix in `featureList` to make them have the same shape'''
        minLen = min([feature.shape[1] for feature in featureList])
        newFeatureList = [feature[:, :minLen] for feature in featureList]
        return newFeatureList


    @QtCore.pyqtSlot(QtCore.QByteArray)
    def processRecorded(self, array: QtCore.QByteArray):
        self.ui.recordProgress.setValue(100)
        logging.info(f'[NewUserWindow] Audio is recorded, processing...')
        # NOTE: debug
        # soundfile.write(
        #     f'./sounds/{self._currentLogin}_{id(array)}_{time.time_ns()}.wav', 
        #     numpy.frombuffer(array, dtype=numpy.int16), 
        #     env.SAMPLERATE, 
        #     'PCM_16'
        # )
        _mfccs = self._mfccsExtractor.extract(array)
        _deltas = self._deltasExtractor.extract(_mfccs)
        array.clear()

        if self._remainingRecords < 1:
            self._mfccsAcc.append(_mfccs)
            self._deltasAcc.append(_deltas)
            self.btnSave.setEnabled(True)
        else:
            self._remainingRecords -= 1
            self._mfccsAcc.append(_mfccs)
            self._deltasAcc.append(_deltas)
            self.ui.remainingRecordsLabel.setText(str(self._remainingRecords))
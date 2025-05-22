import logging
from PyQt5 import QtWidgets, QtCore, QtGui

from AboutWindow import AboutWindow
from UserAccount import UserAccount, Admin
from NewUserWindow import NewUserWindow
from Users import Users
from LocalStorage import LocalStorage


from ui.ui_admin import Ui_AdminWindow

class AdminWindow(QtWidgets.QMainWindow):
    
    onExit = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(AdminWindow, self).__init__(parent)

        self.ui = Ui_AdminWindow()
        self.ui.setupUi(self)

        self.ui.thresholdDoubleSpinBox.valueChanged.connect(self.changeThreshold)
        self.ui.totalRecordsSpinBox.valueChanged.connect(self.changeRecordsCount)

        self.aboutDialog = AboutWindow(self)
        self.changeRecordDialog = NewUserWindow(self)
        self.messageBox = QtWidgets.QMessageBox(self)

        self.ui.actionAbout.triggered.connect(self.aboutDialog.show)
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionChange_record.triggered.connect(self.changeRecord)
        self.ui.addNewUserButton.clicked.connect(self.addNewUser)
        self.ui.newUserLoginEdit.editingFinished.connect(self.addNewUser)

        self.changeRecordDialog.onExit.connect(self.__updateAdmin)

        self.ui.usersTableWidget.itemChanged.connect(self.tableInput)
        self.ui.usersTableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    @QtCore.pyqtSlot(QtWidgets.QTableWidgetItem)
    def tableInput(self, item : QtWidgets.QTableWidgetItem):
        row = item.row()
        col = item.column()
        if col == 1:
            key = list(self._users.keys())[row]
            user = self._users[key]
            if user.isAdmin() \
                and user.login != self._currentAdmin.login \
                and item.checkState() == QtCore.Qt.CheckState.Unchecked:
                logging.info(f'[AdminWindow] Changing admin {user.login} to ordinary user')
                self._users[key] = UserAccount(user.login, user.speechData, user.trainMeanDistance)
            elif not user.isAdmin() and item.checkState() == QtCore.Qt.CheckState.Checked:
                logging.info(f'[AdminWindow] Changing ordinary user {user.login} to admin')
                self._users[key] = Admin(user.login, user.speechData, user.trainMeanDistance)

    @QtCore.pyqtSlot(float)
    def changeThreshold(self, threshold : float):
        logging.info(f'[AdminWindow] Threshold changed to {threshold}')
        self._localStorage.threshold = threshold

    @QtCore.pyqtSlot(int)
    def changeRecordsCount(self, count : int):
        logging.info(f'[AdminWindow] Min records count changed to {count}')
        self._localStorage.recordsCount = count
        
    @QtCore.pyqtSlot(str)
    def enter(self, adminLogin : str):
        self._localStorage = LocalStorage()
        self._users : Users = self._localStorage.users
        self._currentAdmin : Admin = self._users[adminLogin]
        self.ui.thresholdDoubleSpinBox.setValue(self._localStorage.threshold)
        self.ui.totalRecordsSpinBox.setValue(self._localStorage.recordsCount)
        self.updateTable()
        self.show()

    @QtCore.pyqtSlot()
    def __updateAdmin(self):
        assert hasattr(self, '_currentAdmin')
        self._localStorage = LocalStorage()
        self._users = self._localStorage.users
        self._currentAdmin : Admin = self._users[self._currentAdmin.login]

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self._currentAdmin.hasSpeechData():
            if self.aboutDialog.isVisible(): 
                self.aboutDialog.close()
            self.onExit.emit()
            return a0.accept()
        else:
            self.messageBox.setText(f'Создайте профиль голоса перед выходом!')
            self.messageBox.show()
            return a0.ignore()

    def changeRecord(self):
        self.changeRecordDialog.enterUpdate(self._currentAdmin.login)

    def addNewUser(self):
        login = self.ui.newUserLoginEdit.text().strip()
        if not len(login):
            return
        if self._users.hasAccountWithLogin(login):
            self.messageBox.setText(f'Пользователь [{login}] уже задан!')
            self.messageBox.show()
        else:
            self._users.addAccountByLogin(login)
            self.updateTable()
        self.ui.newUserLoginEdit.clear()

    def updateTable(self):
        self.ui.usersTableWidget.setRowCount(len(self._users))
        for i, login in enumerate(self._users):
            user : UserAccount = self._users[login]
            loginItem = QtWidgets.QTableWidgetItem(user.login)
            self.ui.usersTableWidget.setItem(i, 0, loginItem)
            adminItem = QtWidgets.QTableWidgetItem()
            if user.isAdmin():
                checkState = QtCore.Qt.CheckState.Checked
            else:
                checkState = QtCore.Qt.CheckState.Unchecked
            adminItem.setCheckState(checkState)
            if user.login == self._currentAdmin.login:
                # disabe this checkbox
                flags = adminItem.flags()
                adminItem.setFlags(flags & ~32) #QtCore.Qt.ItemFlag.ItemIsEditable) # & ~32
            self.ui.usersTableWidget.setItem(i, 1, adminItem)
        
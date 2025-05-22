from PyQt5 import QtWidgets, QtCore, QtGui
from ui.ui_about import Ui_aboutDialog

class AboutWindow(QtWidgets.QDialog):

	def __init__(self, parent=None):
		super(AboutWindow, self).__init__(parent)

		self.ui = Ui_aboutDialog()
		self.ui.setupUi(self)
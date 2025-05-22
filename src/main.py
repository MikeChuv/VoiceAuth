import sys
import logging
from PyQt5 import QtCore

from MainApp import MainApp

def main(*args, **kwargs):
    if(sys.flags.interactive != 1) or not hasattr(QtCore, "PYQT_VERSION"):
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
        app = MainApp()
        app.start()


if __name__ == '__main__':
    main()
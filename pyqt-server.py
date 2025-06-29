import gui
import sys
from PyQt5 import QtWidgets

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = gui.Window()
    window.show()
    sys.exit(app.exec_())

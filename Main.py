import sys

# Imported PySide6 For The UI
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtUiTools import QUiLoader

app = QApplication(sys.argv)
loader = QUiLoader()
CurrentSelectedProcess = "Overall"
Width = 800
Height = 550

ui_file = QFile("interface.ui")
ui_file.open(QFile.ReadOnly)

window = loader.load(ui_file)
ui_file.close()

window.setWindowTitle("NetNinja")
window.setWindowIcon(QIcon("icons/icon.png"))
window.setFixedSize(Width, Height)
window.show()

screen_center = QScreen.availableGeometry(QApplication.primaryScreen()).center()
window_frame = window.frameGeometry()
window_frame.moveCenter(screen_center)
window.move(window_frame.topLeft())

sys.exit(app.exec())

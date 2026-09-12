import sys
import psutil

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

PList = window.findChild(QListWidget, "PList")
Packets = window.findChild(QTableView, "Packets")
SearchButton = window.findChild(QPushButton, "SearchButton")
StopMonitorButton = window.findChild(QPushButton, "StopMonitorButton")

HiddenProcesses = {
    "System",
    "System Idle Process",
    "Registry",
    "smss.exe",
    "csrss.exe",
    "wininit.exe",
    "services.exe",
    "lsass.exe",
    "svchost.exe",
    "winlogon.exe",
    "fontdrvhost.exe",
    "dwm.exe",
    "conhost.exe",
    "sihost.exe",
    "ctfmon.exe",
    "RuntimeBroker.exe",
    "SearchHost.exe",
    "StartMenuExperienceHost.exe",
    "ShellExperienceHost.exe",
    "TextInputHost.exe",
    "explorer.exe"
}

Processes = []

for Process in psutil.process_iter(["pid", "name"]):
    try:
        PID = Process.info["pid"]
        Name = Process.info["name"]

        if not Name or Name in HiddenProcesses:
            continue

        Processes.append({
            "name": Name,
            "pid": PID
        })

    except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue

Processes.sort(key=lambda Process: Process["name"].lower())


def LoadProcesses(Search=""):
    PList.clear()

    PList.addItem("Overall")
    PList.addItem("Reset")

    Search = Search.strip().lower()

    for Process in Processes:
        Name = Process["name"]
        PID = Process["pid"]

        if Search == "":
            Match = True
        elif Search in Name.lower():
            Match = True
        elif Search in str(PID):
            Match = True
        else:
            Match = False

        if Match:
            PList.addItem(f"{Name}  (PID: {PID})")


def ProcessSelected(Item):
    global CurrentSelectedProcess

    Text = Item.text()

    if Text == "Overall":
        CurrentSelectedProcess = "Overall"
        print("Selected Process: Overall")
        return

    if Text == "Reset":
        CurrentSelectedProcess = "Overall"
        LoadProcesses()
        PList.setCurrentRow(0)
        print("Process list reset")
        return

    CurrentSelectedProcess = Text
    print("Selected Process:", CurrentSelectedProcess)


def SearchProcesses():
    Search, OK = QInputDialog.getText(
        window,
        "Search Processes",
        "Process name or PID:"
    )

    if OK:
        LoadProcesses(Search)
        PList.setCurrentRow(0)


PList.itemClicked.connect(ProcessSelected)
SearchButton.clicked.connect(SearchProcesses)

LoadProcesses()

window.setWindowTitle("NetNinja")
window.setWindowIcon(QIcon("icons/icon.png"))
window.setFixedSize(Width, Height)
window.show()

ScreenCenter = QScreen.availableGeometry(
    QApplication.primaryScreen()
).center()

WindowFrame = window.frameGeometry()
WindowFrame.moveCenter(ScreenCenter)
window.move(WindowFrame.topLeft())

sys.exit(app.exec())

import sys, os, json, psutil
from PySide6.QtCore import QFile, QAbstractTableModel, QModelIndex, Qt, QTime, QTimer
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QListWidget, QPushButton, QTableView, QAbstractItemView, QInputDialog, QMessageBox, QMenu, QFileDialog
from PySide6.QtUiTools import QUiLoader

BASE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
UI = os.path.join(BASE, "interface.ui")
ICON = os.path.join(BASE, "icons", "icon.png")

class Model(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.headers = ["Time", "Process", "PID", "Protocol", "Local", "Remote", "State", "JSON"]
        self.rows = []

    def rowCount(self, parent=QModelIndex()):
        return len(self.rows)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            return self.rows[index.row()][index.column()]
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        return self.headers[section] if orientation == Qt.Horizontal else str(section + 1)

    def add(self, row):
        n = len(self.rows)
        self.beginInsertRows(QModelIndex(), n, n)
        self.rows.append(row)
        self.endInsertRows()

app = QApplication(sys.argv)

loader = QUiLoader()
ui_file = QFile(UI)

if not ui_file.open(QFile.ReadOnly):
    print("Could not open:", UI)
    sys.exit(1)

window = loader.load(ui_file)
ui_file.close()

if not window:
    print("Could not load interface.ui")
    sys.exit(1)

window.setWindowTitle("NetNinja")
window.setWindowIcon(QIcon(ICON))
window.setFixedSize(800, 550)

title = window.findChild(QLabel, "Title")
if title:
    title.setGeometry(90, 25, 220, 41)
    title.setText("NETNINJA")

icon_label = window.findChild(QLabel, "label")
if icon_label:
    icon_label.setGeometry(5, 8, 75, 75)
    icon_label.setAlignment(Qt.AlignCenter)
    pixmap = QPixmap(ICON)

    if pixmap.isNull():
        print("Could not load icon:", ICON)
    else:
        icon_label.setPixmap(
            pixmap.scaled(
                75,
                75,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

PList = window.findChild(QListWidget, "PList")
Packets = window.findChild(QTableView, "Packets")
Search = window.findChild(QPushButton, "SearchButton")
Stop = window.findChild(QPushButton, "StopMonitorButton")

if not all((PList, Packets, Search, Stop)):
    print("Missing widget in interface.ui")
    sys.exit(1)

model = Model()
Packets.setModel(model)
Packets.setAlternatingRowColors(True)
Packets.setWordWrap(False)
Packets.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
Packets.verticalHeader().setDefaultSectionSize(30)

column_widths = [80, 150, 70, 80, 180, 180, 70, 70]

for i, width in enumerate(column_widths):
    Packets.setColumnWidth(i, width)

hidden = {
    "System", "System Idle Process", "Registry",
    "smss.exe", "csrss.exe", "wininit.exe",
    "services.exe", "lsass.exe", "svchost.exe",
    "winlogon.exe", "fontdrvhost.exe", "dwm.exe",
    "conhost.exe", "sihost.exe", "ctfmon.exe",
    "RuntimeBroker.exe", "SearchHost.exe",
    "StartMenuExperienceHost.exe",
    "ShellExperienceHost.exe", "TextInputHost.exe",
    "explorer.exe"
}

processes = []

for process in psutil.process_iter(["pid", "name"]):
    try:
        name = process.info["name"]
        pid = process.info["pid"]

        if name and name not in hidden:
            processes.append((name, pid))
    except:
        pass

processes.sort(key=lambda x: x[0].lower())

selected = "Overall"
running = True
old_connections = set()

def load_processes(search=""):
    PList.clear()
    PList.addItem("Overall")
    PList.addItem("Reset")

    search = search.lower().strip()

    for name, pid in processes:
        if not search or search in name.lower() or search in str(pid):
            PList.addItem(f"{name}  (PID: {pid})")

def update_packets():
    if selected == "Overall":
        Packets.setModel(model)
        return

    pid = selected.split("(PID: ")[-1].rstrip(")")
    filtered = Model()
    filtered.rows = [row for row in model.rows if row[2] == pid]

    Packets.setModel(filtered)

    for i, width in enumerate(column_widths):
        Packets.setColumnWidth(i, width)

def select_process(item):
    global selected

    text = item.text()

    if text == "Reset":
        selected = "Overall"
        load_processes()
        PList.setCurrentRow(0)
    elif text == "Overall":
        selected = "Overall"
    else:
        selected = text

    update_packets()

def search_processes():
    text, ok = QInputDialog.getText(
        window,
        "Search Processes",
        "Process name or PID:"
    )

    if ok:
        load_processes(text)
        PList.setCurrentRow(0)

def packet_json(row):
    return json.dumps({
        "time": row[0],
        "process": row[1],
        "pid": row[2],
        "protocol": row[3],
        "local": row[4],
        "remote": row[5],
        "state": row[6]
    }, indent=4)

def packet_menu(position):
    index = Packets.indexAt(position)

    if not index.isValid():
        return

    table_model = Packets.model()

    if not hasattr(table_model, "rows"):
        return

    if index.row() >= len(table_model.rows):
        return

    packet = table_model.rows[index.row()]
    data = packet_json(packet)

    menu = QMenu(Packets)

    view_json = menu.addAction("View JSON")
    download_json = menu.addAction("Download JSON")
    copy = menu.addAction("Copy")

    menu.addSeparator()
    cancel = menu.addAction("Cancel")

    action = menu.exec(
        Packets.viewport().mapToGlobal(position)
    )

    if action == view_json:
        QMessageBox.information(
            window,
            "Packet JSON",
            data
        )

    elif action == download_json:
        path, _ = QFileDialog.getSaveFileName(
            window,
            "Download JSON",
            f"packet_{packet[2]}.json",
            "JSON Files (*.json)"
        )

        if path:
            with open(path, "w", encoding="utf-8") as file:
                file.write(data)

    elif action == copy:
        QApplication.clipboard().setText(" | ".join(packet))

def monitor_connections():
    global old_connections

    if not running:
        return

    current = set()

    try:
        for connection in psutil.net_connections("inet"):
            if not connection.laddr or connection.pid is None:
                continue

            local = f"{connection.laddr.ip}:{connection.laddr.port}"

            remote = (
                f"{connection.raddr.ip}:{connection.raddr.port}"
                if connection.raddr
                else "*"
            )

            protocol = "UDP" if connection.type == 2 else "TCP"

            key = (
                connection.pid,
                protocol,
                local,
                remote,
                connection.status
            )

            current.add(key)

            if key in old_connections:
                continue

            try:
                name = psutil.Process(connection.pid).name()
            except:
                name = "Unknown"

            model.add([
                QTime.currentTime().toString("HH:mm:ss"),
                name,
                str(connection.pid),
                protocol,
                local,
                remote,
                connection.status,
                "No"
            ])

            if selected == "Overall":
                Packets.scrollToBottom()
            else:
                update_packets()

    except Exception as error:
        print("Monitor:", error)

    old_connections = current

def set_monitor_style():
    color = "green" if running else "red"

    Stop.setStyleSheet(f"""
        QPushButton#StopMonitorButton {{
            background-color: #2A2A2A;
            color: {color};
            border: 1px solid #3A3A3A;
            border-radius: 5px;
            padding: 6px 12px;
        }}

        QPushButton#StopMonitorButton:hover {{
            background-color: #3A3A3A;
            border: 1px solid #555555;
        }}

        QPushButton#StopMonitorButton:pressed {{
            background-color: #222222;
        }}
    """)

def toggle_monitor():
    global running

    running = not running
    set_monitor_style()

PList.setSpacing(4)
PList.setUniformItemSizes(True)

load_processes()

PList.itemClicked.connect(select_process)
Search.clicked.connect(search_processes)
Stop.clicked.connect(toggle_monitor)

Packets.setContextMenuPolicy(Qt.CustomContextMenu)
Packets.customContextMenuRequested.connect(packet_menu)

set_monitor_style()

timer = QTimer()
timer.timeout.connect(monitor_connections)
timer.start(250)

screen = QApplication.primaryScreen()
frame = window.frameGeometry()
frame.moveCenter(screen.availableGeometry().center())
window.move(frame.topLeft())

window.show()
sys.exit(app.exec())

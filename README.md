[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/markitdown.svg)](https://pypi.org/project/markitdown/)

> **A Python Tool For Monitoring Network Traffic**

**Warning**: Currently, this project works only on Windows 8 or later

# Libraries

This Project Uses

**PySide6**: https://pypi.org/project/PySide6/

**psutil**: https://pypi.org/project/psutil/

**pyinstaller**: https://pypi.org/project/pyinstaller/

---

# Installation

### Requirements

At Least **Python 3** or higher

---

## Installing From Zip

Download the latest Zip from the **Releases** section

1. Extract the ZIP file

2. Open the extracted `NetNinja` folder

3. Run `NetNinja.exe`

---

## Compiling From Source

First Begin By Installing Required Libs By:
```bash
pip install -r requirements.txt
```

Compile Command:

```bash
pyinstaller --clean --noconsole --onefile --name NetNinja --icon "icons\icon.ico" --add-data "interface.ui;." --add-data "icons;icons" main.py
```

The compiled executable will be located at:

```text
dist\NetNinja.exe
```

> **Note**: Run Theses commands In Project's Root Dir
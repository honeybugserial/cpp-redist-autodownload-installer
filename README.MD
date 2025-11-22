# Visual C++ Redistributable Auto-Downloader & Installer

![Visual 01](https://github.com/honeybugserial/cpp-redist-autodownload-installer/blob/main/Visual01.png)
![Visual 02](https://github.com/honeybugserial/cpp-redist-autodownload-installer/blob/main/visual02.png)

---

## Features

- Automatic Administrator elevation
- Random US TechPowerUp mirror selection
- Full ZIP download with progress bar
- Extraction of all redistributable installers
- Ordered installation (2005 → 2022)
- Architecture-aware filtering (x64 on 64-bit only)
- Rich-styled console output (`[ # ]`, `[ + ]`, `[WARN]`, `[ERROR]`)
- Disables Windows QuickEdit mode to prevent accidental pauses
- Automatic cleanup of ZIP and extraction directory
- Works as a Python script or PyInstaller/Nuitka/CX-Freeze frozen EXE
- **Supports `--auto-accept` flag for unattended, non-interactive installation**

---

## Download Binary

**PyInstaller (single EXE)**  
[Google Drive PyInstaller Single EXE](https://drive.google.com)

**CX-Freeze (folder build)**  
[Google Drive CX Freeze Folder](https://drive.google.com)



---

## Requirements

- Windows 10 or later
- Administrator privileges (auto-elevates if needed)
- Python 3.8+ if running as a script
- Required Python packages:
  - `requests`
  - `rich`
  - `tqdm`

Install dependencies:

```bash
pip install requests rich tqdm
```

---

## Usage

### Run as a Python script

```bash
python vcredist_auto.py
```

### Run as a frozen EXE

Double-click or:

```bash
vcredist_auto.exe
```

### Unattended / silent-style mode

To skip:

- the initial “Proceed?” confirmation
- the final “Press ENTER to exit”

Use:

```bash
vcredist_auto.exe --auto-accept
```

Or when running as a Python script:

```bash
python vcredist_auto.py --auto-accept
```

This suppresses all interactive prompts while still showing normal installation output.

---

## Directory Structure

When running:

```
<working_dir>/
    vcredist_auto.py or vcredist_auto.exe
    vcredist_xxx.zip       (downloaded)
    vcredist_xxx/          (extracted installers)
```

After cleanup, only the original script or EXE remains.

---

## Notes

- The script relies on TechPowerUp’s redirect to locate the download URL.
- Installation switches differ per redistributable version (handled internally).
- x64 installers are skipped on 32-bit systems.

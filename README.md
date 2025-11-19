```
# Visual C++ Redistributable Auto-Downloader & Installer

This script automates downloading, extracting, installing, and cleaning up all Microsoft Visual C++ Redistributable packages using a TechPowerUp mirror.
It includes automatic elevation, a Rich-formatted console UI, QuickEdit-disable, and progress-aware downloads via `tqdm`.

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
- Works as a Python script or PyInstaller/Nuitka-frozen EXE

---

## Requirements

- Windows 10 or later
- Administrator privileges (auto-elevates if needed)
- Python 3.8+ if running as a script
- Required Python packages:
  - \`requests\`
  - \`rich\`
  - \`tqdm\`

Install dependencies:

\`\`\`bash
pip install requests rich tqdm
\`\`\`

---

## Usage

### Run as a Python script

\`\`\`bash
python vcredist_auto.py
\`\`\`

### Run as a frozen EXE

If bundled with PyInstaller/Nuitka, no Python installation is required.

Double-click the executable, or run:

\`\`\`bash
vcredist_auto.exe
\`\`\`

The tool will:

1. Request elevation (if not already elevated)
2. Download the latest TechPowerUp VC++ redistributable bundle
3. Extract all installers
4. Execute them in proper version order
5. Remove temporary files
6. Present a final confirmation screen

---

## Directory Structure

When running:

\`\`\`
<working_dir>/
    vcredist_auto.py or vcredist_auto.exe
    vcredist_xxx.zip       (downloaded)
    vcredist_xxx/          (extracted installers)
\`\`\`

After cleanup, only the original script or EXE remains.

---

## Notes

- The script relies on TechPowerUp’s posted redirect to locate the actual download URL.
- Installation switches differ per redistributable version (handled internally).
- x64 installers are skipped on 32-bit systems by design.

---

## License

MIT License (optional — replace or remove as needed).
```

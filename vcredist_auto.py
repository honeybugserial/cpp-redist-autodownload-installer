import os
import sys
import ctypes
import random
import requests
import zipfile
import shutil
import subprocess
import time
import ctypes
import ctypes.wintypes as wt
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule
from tqdm import tqdm

# ------------------------------
# Flag verification
# ------------------------------
VALID_FLAGS = {"--auto-accept"}

def parse_flags():
    flags = set()
    for arg in sys.argv[1:]:
        if arg.startswith("--"):
            if arg not in VALID_FLAGS:
                print(f"Invalid flag: {arg}")
                sys.exit(1)
            flags.add(arg)
    return flags


# ------------------------------
# QuickEdit disable
# ------------------------------
def disable_quickedit():
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    GetStdHandle = kernel32.GetStdHandle
    GetStdHandle.argtypes = [wt.DWORD]
    GetStdHandle.restype = wt.HANDLE

    GetConsoleMode = kernel32.GetConsoleMode
    GetConsoleMode.argtypes = [wt.HANDLE, wt.LPDWORD]
    GetConsoleMode.restype = wt.BOOL

    SetConsoleMode = kernel32.SetConsoleMode
    SetConsoleMode.argtypes = [wt.HANDLE, wt.DWORD]
    SetConsoleMode.restype = wt.BOOL

    STD_INPUT_HANDLE = -10
    ENABLE_QUICK_EDIT = 0x40

    h_stdin = GetStdHandle(STD_INPUT_HANDLE)
    mode = wt.DWORD()

    if not GetConsoleMode(h_stdin, ctypes.byref(mode)):
        return

    new_mode = mode.value & ~ENABLE_QUICK_EDIT
    SetConsoleMode(h_stdin, new_mode)


console = Console(highlight=False, soft_wrap=False)

# ------------------------------
# Determine EXE/script directory
# ------------------------------
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent


# ------------------------------
# Rich helpers
# ------------------------------
def info(msg):
    console.print(f"[bold cyan][ # ] [/bold cyan] {msg}")

def ok(msg):
    console.print(f"[bold green][ + ] [/bold green] {msg}")

def warn(msg):
    console.print(f"[bold yellow][WARN] [/bold yellow] {msg}")

def error(msg):
    console.print(f"[bold red][ERROR] [/bold red] {msg}")

def fatal(msg, code=1):
    error(msg)
    sys.exit(code)

# ------------------------------
# Elevation
# ------------------------------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def relaunch_as_admin():
    params = " ".join(f'"{a}"' for a in sys.argv)
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, params, None, 1
        )
    except Exception as e:
        fatal(f"Elevation failed: {e}")
    sys.exit(0)

if not is_admin():
    print("Requesting Administrator privileges…")
    relaunch_as_admin()

# ------------------------------
# Config
# ------------------------------
US_MIRRORS = [
    "16", "24", "26", "11", "12", "21", "19", "3", "20"
]

TPU_URL = "https://www.techpowerup.com/download/visual-c-redistributable-runtime-package-all-in-one/"
BATCH_NAME = "install_all.bat"

# ------------------------------
# Console width
# ------------------------------
def widen_console():
    if os.name != "nt":
        return
    try:
        os.system("mode con: cols=132 lines=40")
    except Exception:
        pass

# ------------------------------
# Download
# ------------------------------
def download_vcredist():
    console.print(Rule("[bold blue]--- Downloading Visual C++ Runtimes ---[/bold blue]"))

    mirror = random.choice(US_MIRRORS)
    info(f"Using random US mirror: {mirror}")

    payload = {"id": "3002", "server_id": mirror}

    try:
        r = requests.post(TPU_URL, data=payload, allow_redirects=False, timeout=15)
    except Exception as e:
        fatal(f"POST request failed: {e}")

    if "Location" not in r.headers:
        fatal("TechPowerUp did not return a redirect.")

    download_url = r.headers["Location"]
    info(f"URL: {download_url}")

    filename = download_url.split("/")[-1]
    file_path = BASE_DIR / filename

    try:
        s = requests.get(download_url, stream=True, timeout=20)
        s.raise_for_status()
    except Exception as e:
        fatal(f"Download failed: {e}")

    total = s.headers.get("Content-Length")
    total = int(total) if total else None

    info(f"Saving as: {file_path}")

    chunk_size = 16384

    if total:
        pbar = tqdm(
            total=total,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc="Downloading",
            ncols=70,
            bar_format="{l_bar}{bar} {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        )
    else:
        pbar = None

    with open(file_path, "wb") as f:
        for chunk in s.iter_content(chunk_size=chunk_size):
            if not chunk:
                continue
            f.write(chunk)
            if pbar:
                pbar.update(len(chunk))

    if pbar:
        pbar.close()

    console.print()
    ok("Download complete.")

    return file_path

# ------------------------------
# Extract
# ------------------------------
def extract_zip(zip_path: Path):
    console.print(Rule("[bold blue]--- Extracting ZIP ---[/bold blue]"))

    if not zip_path.exists():
        fatal(f"ZIP file missing: {zip_path}")

    out_dir = zip_path.with_suffix("")

    if out_dir.exists():
        warn(f"Output directory exists: {out_dir}")
        shutil.rmtree(out_dir)

    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(out_dir)
    except Exception as e:
        fatal(f"ZIP extraction failed: {e}")

    ok(f"Extracted to: {out_dir}")
    return out_dir

# ------------------------------
# Install redistributables
# ------------------------------
def run_vcredists(out_dir: Path):
    console.print(Rule("[bold blue]--- Installing VC++ Runtimes ---[/bold blue]"))

    files = sorted(out_dir.glob("*.exe"))
    if not files:
        fatal("No redistributable installers found.")

    import platform
    IS_X64 = platform.architecture()[0] == "64bit"

    SWITCHES = {
        "2005": "/q",
        "2008": "/qb",
        "2010": "/passive /norestart",
        "2012": "/passive /norestart",
        "2013": "/passive /norestart",
        "2015": "/passive /norestart",
        "2017": "/passive /norestart",
        "2019": "/passive /norestart",
        "2022": "/passive /norestart",
    }

    ORDER = ["2005", "2008", "2010", "2012", "2013", "2015", "2017", "2019", "2022"]

    def classify(fname: str):
        lower = fname.lower()
        version = None
        for key in ORDER:
            if key in lower:
                version = key
                break
        arch = "x64" if "x64" in lower else "x86"
        return version, arch

    def sort_key(path: Path):
        ver, arch = classify(path.name)
        if ver in ORDER:
            return (ORDER.index(ver), arch == "x64")
        return (999, path.name)

    installers = sorted(files, key=sort_key)

    for exe in installers:
        ver, arch = classify(exe.name)

        if arch == "x64" and not IS_X64:
            continue

        switches = SWITCHES.get(ver, "/passive /norestart")

        info(f"Installing {exe.name} (v={ver}, arch={arch})")

        try:
            rc = subprocess.run(
                [str(exe), *switches.split()],
                cwd=str(out_dir),
                shell=False
            ).returncode
        except Exception as e:
            fatal(f"Failed to run {exe.name}: {e}")

        if rc != 0:
            warn(f"{exe.name} exited with code {rc}")
        else:
            ok(f"{exe.name} installed.")

# ------------------------------
# Cleanup
# ------------------------------
def cleanup(zip_path: Path, extract_dir: Path):
    console.print(Rule("[bold blue]--- Cleanup ---[/bold blue]"))

    if zip_path.exists():
        try:
            zip_path.unlink()
            ok(f"Deleted ZIP: {zip_path.name}")
        except Exception as e:
            warn(f"Could not delete ZIP ({e})")
    else:
        warn(f"ZIP not found: {zip_path.name}")

    if extract_dir.exists():
        try:
            shutil.rmtree(extract_dir)
            ok(f"Deleted extracted directory: {extract_dir}")
        except Exception as e:
            warn(f"Failed to delete extracted directory ({e})")
    else:
        warn(f"Extracted directory not found: {extract_dir}")


# ------------------------------
# MAIN
# ------------------------------
def main():
    flags = parse_flags()
    auto = ("--auto-accept" in flags)

    disable_quickedit()
    widen_console()

    console.print(Panel("[bold cyan]Visual C++ Runtime Auto-Downloader[/bold cyan]", border_style="cyan"))

    if not auto:
        console.print(Panel(
            "[bold yellow]This will download, extract, install, and clean up all VC++ runtimes.\nProceed? (Y/N)[/bold yellow]",
            border_style="yellow"
        ))
        choice = input().strip().lower()
        if choice not in ("y", "yes"):
            sys.exit(0)

    zip_file = download_vcredist()
    out_dir = extract_zip(zip_file)
    run_vcredists(out_dir)
    time.sleep(0.5)
    cleanup(zip_file, out_dir)

    console.line()
    console.print(Panel("[bold green]Installation Finished![/bold green]", border_style="green"))

    if not auto:
        console.print("\n[bold cyan]Press ENTER to exit…[/bold cyan]")
        input()


if __name__ == "__main__":
    main()

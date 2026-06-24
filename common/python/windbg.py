import os
import subprocess


def find_windbg() -> str | None:
    """Find WinDbg executable via the WindowsApps alias directory."""
    alias_dir = os.path.join(
        os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WindowsApps"
    )
    for name in ("windbg.exe", "WinDbgX.exe"):
        path = os.path.join(alias_dir, name)
        if os.path.exists(path):
            return path
    return None


def run_with_windbg(exe: str, *args: str) -> None:
    """Launch exe under WinDbg if available, otherwise run directly."""
    windbg = find_windbg()
    if windbg:
        subprocess.run([windbg, exe, *args])
    else:
        print("[!] windbg.exe not found, running without debugger")
        subprocess.run([exe, *args])

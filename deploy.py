"""
Build artifacts staging script.

Scans build/<preset>/ for all .exe files, maps them back to the source
tree, and copies exe + pdb + exploit.py (if present) into work/ with
the same directory structure. Multiple presets are merged into the same
work/ tree so x86 and x64 binaries coexist in the same project folder.

Usage:
    python deploy.py [--preset x86-debug [x64-debug ...]]
"""

import argparse
import glob
import os
import shutil

OUTPUT_DIR = "work"

_BUILD_SKIP = {"CMakeFiles", "Testing"}


def iter_exes(build_dir: str):
    for exe in glob.glob(os.path.join(build_dir, "**", "*.exe"), recursive=True):
        parts = exe.replace("\\", "/").split("/")
        if any(s in parts for s in _BUILD_SKIP):
            continue
        yield exe


def resolve_build_dirs(presets: list[str]) -> list[str] | None:
    build_dirs = []
    for preset in presets:
        build_dir = os.path.join("build", preset)
        if not os.path.isdir(build_dir):
            print(f"[!] Build directory not found: {build_dir}")
            print(f"    Run: cmake --preset {preset} && cmake --build build/{preset}")
            return None
        build_dirs.append(build_dir)
    return build_dirs


def deploy_exe(exe: str, out_dir: str) -> list[str]:
    pdb = os.path.splitext(exe)[0] + ".pdb"
    shutil.copy2(exe, out_dir)
    files = [os.path.basename(exe)]
    if os.path.exists(pdb):
        shutil.copy2(pdb, out_dir)
        files.append(os.path.basename(pdb))
    return files


def copy_scripts(project_rel: str, out_dir: str, common_py_files: list[str]) -> list[str]:
    exploit_py = os.path.join(project_rel, "exploit.py")
    if not os.path.exists(exploit_py):
        return []
    shutil.copy2(exploit_py, out_dir)
    files = ["exploit.py"]
    for f in common_py_files:
        shutil.copy2(f, out_dir)
        files.append(os.path.basename(f))
    return files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", nargs="+", default=["x86-debug"], metavar="PRESET",
                        help="CMake preset(s) to deploy (default: x86-debug)")
    args = parser.parse_args()

    build_dirs = resolve_build_dirs(args.preset)
    if build_dirs is None:
        return

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    common_py_files = glob.glob(os.path.join("common", "python", "*.py"))
    deployed = 0
    deployed_script_dirs: set[str] = set()

    for build_dir in build_dirs:
        for exe in sorted(iter_exes(build_dir)):
            project_rel = os.path.dirname(os.path.relpath(exe, build_dir))
            out_dir = os.path.join(OUTPUT_DIR, project_rel)
            os.makedirs(out_dir, exist_ok=True)

            files = deploy_exe(exe, out_dir)

            if project_rel not in deployed_script_dirs:
                files += copy_scripts(project_rel, out_dir, common_py_files)
                deployed_script_dirs.add(project_rel)

            print(f"[+] {project_rel}/ <- {', '.join(files)}")
            deployed += 1

    print(f"\n{deployed} artifact(s) deployed to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()

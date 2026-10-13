"""
Build and Release Automation Script for Markdown Studio.
Creates:
1. Compiled Application (dist/MarkdownStudio/)
2. Portable ZIP Package (dist/MarkdownStudio-1.0.0-Portable.zip)
3. Windows Setup Installer (dist/MarkdownStudio-1.0.0-Setup.exe)
"""

import os
import sys
import shutil
import zipfile
import subprocess


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")
BUILD_DIR = os.path.join(BASE_DIR, "build")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
APP_DIR = os.path.join(DIST_DIR, "MarkdownStudio")


def find_iscc() -> str:
    """Finds Inno Setup Compiler executable."""
    candidates = [
        r"C:\Users\z261218\AppData\Local\Programs\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        shutil.which("ISCC.exe")
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def run_pyinstaller():
    print("=" * 60)
    print("1. Starte PyInstaller Build...")
    print("=" * 60)

    icon_path = os.path.join(ASSETS_DIR, "app_icon.ico")
    main_py = os.path.join(BASE_DIR, "src", "main.py")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--name", "MarkdownStudio",
        "--icon", icon_path,
        f"--add-data={ASSETS_DIR};assets",
        "--clean",
        "--noconfirm",
        main_py
    ]

    print("Kommando:", " ".join(cmd))
    res = subprocess.run(cmd, cwd=BASE_DIR)
    if res.returncode != 0:
        raise RuntimeError("PyInstaller build fehlgeschlagen!")

    print("\nPyInstaller erfolgreich abgeschlossen.")


def make_portable_zip():
    print("=" * 60)
    print("2. Erstelle Portable ZIP-Paket...")
    print("=" * 60)

    zip_filename = os.path.join(DIST_DIR, "MarkdownStudio-1.0.0-Portable.zip")
    if os.path.exists(zip_filename):
        os.remove(zip_filename)

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(APP_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, DIST_DIR)
                zipf.write(full_path, rel_path)

    zip_size_mb = os.path.getsize(zip_filename) / (1024 * 1024)
    print(f"Portable ZIP erstellt: {zip_filename} ({zip_size_mb:.2f} MB)")


def make_inno_setup():
    print("=" * 60)
    print("3. Erstelle Windows Setup Installer (Inno Setup)...")
    print("=" * 60)

    iscc = find_iscc()
    if not iscc:
        print("WARNUNG: ISCC.exe nicht gefunden! Setup.exe konnte nicht erstellt werden.")
        return

    iss_file = os.path.join(BASE_DIR, "installer", "setup.iss")
    cmd = [iscc, iss_file]
    print(f"Kompiliere Setup mit: {iscc}")
    res = subprocess.run(cmd, cwd=os.path.join(BASE_DIR, "installer"))
    if res.returncode != 0:
        raise RuntimeError("Inno Setup Kompilierung fehlgeschlagen!")

    setup_exe = os.path.join(DIST_DIR, "MarkdownStudio-1.0.0-Setup.exe")
    if os.path.exists(setup_exe):
        setup_size_mb = os.path.getsize(setup_exe) / (1024 * 1024)
        print(f"Setup Installer erstellt: {setup_exe} ({setup_size_mb:.2f} MB)")


def main():
    run_pyinstaller()
    make_portable_zip()
    make_inno_setup()

    print("=" * 60)
    print("BUILD & RELEASE ERFOLGREICH ABGESCHLOSSEN!")
    print("=" * 60)
    print("Bereitgestellte Release-Dateien im Verzeichnis dist/:")
    for f in os.listdir(DIST_DIR):
        fp = os.path.join(DIST_DIR, f)
        if os.path.isfile(fp):
            size_mb = os.path.getsize(fp) / (1024 * 1024)
            print(f" - {f} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()

"""
File Association Manager for Markdown Studio on Windows.
Supports registering/unregistering file associations for .md and .markdown
both for the Current User (HKCU - no admin required) and All Users (HKLM - admin).
"""

import sys
import os
import winreg
import ctypes
from typing import Tuple, Optional


PROG_ID = "MarkdownStudio.Document"
PROG_DESCRIPTION = "Markdown-Dokument"
EXTENSIONS = [".md", ".markdown"]


def get_default_executable() -> str:
    """Returns the executable path of Markdown Studio."""
    if getattr(sys, "frozen", False):
        return sys.executable
    # Running from source: python.exe pointing to main.py
    main_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))
    python_exe = sys.executable
    if python_exe.endswith("python.exe"):
        pythonw = python_exe.replace("python.exe", "pythonw.exe")
        if os.path.exists(pythonw):
            python_exe = pythonw
    return f'"{python_exe}" "{main_py}"'


def refresh_shell():
    """Notifies Windows Explorer of file association changes."""
    try:
        SHCNE_ASSOCCHANGED = 0x08000000
        SHCNF_IDLIST = 0x0000
        ctypes.windll.shell32.SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_IDLIST, None, None)
    except Exception as e:
        print(f"Shell refresh notification warning: {e}", file=sys.stderr)


def is_associated(all_users: bool = False) -> bool:
    """
    Checks if .md extension is associated with MarkdownStudio.Document.
    """
    root_key = winreg.HKEY_LOCAL_MACHINE if all_users else winreg.HKEY_CURRENT_USER
    classes_sub = r"Software\Classes\.md"

    try:
        with winreg.OpenKey(root_key, classes_sub, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, "")
            return val == PROG_ID
    except OSError:
        return False


def register_association(exe_path: Optional[str] = None, all_users: bool = False) -> Tuple[bool, str]:
    """
    Registers .md and .markdown associations for Current User or All Users.
    """
    if exe_path is None:
        exe_path = get_default_executable()

    root_key = winreg.HKEY_LOCAL_MACHINE if all_users else winreg.HKEY_CURRENT_USER
    scope_name = "Alle Benutzer (System)" if all_users else "Aktueller Benutzer"

    # Command string: Ensure "%1" is passed
    if getattr(sys, "frozen", False):
        clean_exe = os.path.abspath(sys.executable)
        open_cmd = f'"{clean_exe}" "%1"'
        icon_path = f'"{clean_exe}",0'
    else:
        main_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))
        open_cmd = f'"{sys.executable}" "{main_py}" "%1"'
        icon_path = f'"{sys.executable}",0'

    try:
        # 1. Create ProgID
        prog_key_path = rf"Software\Classes\{PROG_ID}"
        with winreg.CreateKey(root_key, prog_key_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, PROG_DESCRIPTION)
            winreg.SetValueEx(key, "FriendlyTypeName", 0, winreg.REG_SZ, PROG_DESCRIPTION)

        # Default Icon
        with winreg.CreateKey(root_key, rf"{prog_key_path}\DefaultIcon") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, icon_path)

        # Shell Open Command
        with winreg.CreateKey(root_key, rf"{prog_key_path}\shell\open\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, open_cmd)

        with winreg.CreateKey(root_key, rf"{prog_key_path}\shell\open") as key:
            winreg.SetValueEx(key, "FriendlyAppName", 0, winreg.REG_SZ, "Markdown Studio")

        # Shell Edit Command
        with winreg.CreateKey(root_key, rf"{prog_key_path}\shell\edit\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, open_cmd)

        # 2. Associate Extensions
        for ext in EXTENSIONS:
            ext_key_path = rf"Software\Classes\{ext}"
            with winreg.CreateKey(root_key, ext_key_path) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, PROG_ID)
                winreg.SetValueEx(key, "Content Type", 0, winreg.REG_SZ, "text/markdown")
                winreg.SetValueEx(key, "PerceivedType", 0, winreg.REG_SZ, "text")

                # OpenWithProgids
                with winreg.CreateKey(key, "OpenWithProgids") as ow_key:
                    winreg.SetValueEx(ow_key, PROG_ID, 0, winreg.REG_NONE, b"")

        # 3. Register Application Capabilities (helps Windows Settings 'Default Apps')
        app_cap_path = r"Software\MarkdownStudio\Capabilities"
        with winreg.CreateKey(root_key, app_cap_path) as key:
            winreg.SetValueEx(key, "ApplicationDescription", 0, winreg.REG_SZ, "Markdown Studio Viewer & Editor")
            winreg.SetValueEx(key, "ApplicationName", 0, winreg.REG_SZ, "Markdown Studio")

        with winreg.CreateKey(root_key, rf"{app_cap_path}\FileAssociations") as key:
            for ext in EXTENSIONS:
                winreg.SetValueEx(key, ext, 0, winreg.REG_SZ, PROG_ID)

        with winreg.CreateKey(root_key, r"Software\RegisteredApplications") as key:
            winreg.SetValueEx(key, "MarkdownStudio", 0, winreg.REG_SZ, app_cap_path)

        refresh_shell()
        return True, f"Erfolgreich für {scope_name} verknüpft!"

    except PermissionError:
        return False, f"Fehler: Administratorrechte erforderlich für Installation unter '{scope_name}'."
    except Exception as e:
        return False, f"Fehler bei der Registrierung: {e}"


def unregister_association(all_users: bool = False) -> Tuple[bool, str]:
    """
    Removes .md and .markdown associations from Current User or All Users.
    """
    root_key = winreg.HKEY_LOCAL_MACHINE if all_users else winreg.HKEY_CURRENT_USER
    scope_name = "Alle Benutzer (System)" if all_users else "Aktueller Benutzer"

    def delete_key_recursive(root, subkey):
        try:
            with winreg.OpenKey(root, subkey, 0, winreg.KEY_ALL_ACCESS) as key:
                info = winreg.QueryInfoKey(key)
                for _ in range(info[0]):
                    child = winreg.EnumKey(key, 0)
                    delete_key_recursive(root, f"{subkey}\\{child}")
            winreg.DeleteKey(root, subkey)
        except OSError:
            pass

    try:
        for ext in EXTENSIONS:
            try:
                with winreg.OpenKey(root_key, rf"Software\Classes\{ext}", 0, winreg.KEY_ALL_ACCESS) as key:
                    val, _ = winreg.QueryValueEx(key, "")
                    if val == PROG_ID:
                        winreg.DeleteValue(key, "")
            except OSError:
                pass

        delete_key_recursive(root_key, rf"Software\Classes\{PROG_ID}")
        delete_key_recursive(root_key, r"Software\MarkdownStudio")
        try:
            with winreg.OpenKey(root_key, r"Software\RegisteredApplications", 0, winreg.KEY_ALL_ACCESS) as key:
                winreg.DeleteValue(key, "MarkdownStudio")
        except OSError:
            pass

        refresh_shell()
        return True, f"Verknüpfung für {scope_name} erfolgreich aufgehoben."
    except PermissionError:
        return False, f"Fehler: Administratorrechte erforderlich, um Registrierung für {scope_name} zu entfernen."
    except Exception as e:
        return False, f"Fehler beim Entfernen: {e}"

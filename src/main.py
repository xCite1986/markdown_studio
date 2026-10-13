"""
Markdown Studio - Entry Point.
A modern, native Markdown Viewer and Editor for Windows.
"""

import sys
import os
import argparse
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from src.main_window import MainWindow
from src.file_association import register_association, unregister_association


def parse_args():
    parser = argparse.ArgumentParser(description="Markdown Studio - Viewer & Editor")
    parser.add_argument("file", nargs="?", default=None, help="Markdown file to open")
    parser.add_argument("--register-assoc-user", action="store_true", help="Register .md file association for current user")
    parser.add_argument("--register-assoc-admin", action="store_true", help="Register .md file association for all users (requires admin)")
    parser.add_argument("--unregister-assoc", action="store_true", help="Unregister .md file association")
    return parser.parse_args()


def main():
    args = parse_args()

    # Silent command-line registration modes (useful for scripted deployments or installers)
    if args.register_assoc_user:
        ok, msg = register_association(all_users=False)
        print(msg)
        sys.exit(0 if ok else 1)

    if args.register_assoc_admin:
        ok, msg = register_association(all_users=True)
        print(msg)
        sys.exit(0 if ok else 1)

    if args.unregister_assoc:
        ok_u, msg_u = unregister_association(all_users=False)
        ok_a, msg_a = unregister_association(all_users=True)
        print(f"User: {msg_u}\nAdmin: {msg_a}")
        sys.exit(0)

    # Launch GUI Application
    app = QApplication(sys.argv)
    app.setApplicationName("Markdown Studio")
    app.setApplicationDisplayName("Markdown Studio")
    app.setOrganizationName("MarkdownStudio")

    # Set icon
    icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "app_icon.ico"))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow(initial_file=args.file)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

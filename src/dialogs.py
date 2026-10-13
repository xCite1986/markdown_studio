"""
Dialogs and tool panels for Markdown Studio.
Includes Insert Link, Insert Image, Insert Table, Find & Replace, and File Association Dialogs.
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSpinBox, QFileDialog, QMessageBox, QGroupBox, QCheckBox, QWidget
)
from PyQt6.QtGui import QTextCursor, QTextDocument
from PyQt6.QtCore import Qt, pyqtSignal

from src.file_association import (
    is_associated, register_association, unregister_association
)


class InsertLinkDialog(QDialog):
    """Dialog for inserting markdown hyperlink."""

    def __init__(self, parent=None, initial_text=""):
        super().__init__(parent)
        self.setWindowTitle("Link einfügen")
        self.resize(380, 150)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Link-Text / Titel:"))
        self.text_input = QLineEdit(initial_text)
        layout.addWidget(self.text_input)

        layout.addWidget(QLabel("Web-Adresse (URL) oder Zieldatei:"))
        self.url_input = QLineEdit("https://")
        layout.addWidget(self.url_input)

        btn_box = QHBoxLayout()
        self.ok_btn = QPushButton("Einfügen")
        self.ok_btn.setDefault(True)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Abbrechen")
        self.cancel_btn.clicked.connect(self.reject)
        btn_box.addStretch()
        btn_box.addWidget(self.cancel_btn)
        btn_box.addWidget(self.ok_btn)
        layout.addLayout(btn_box)

    def get_data(self):
        text = self.text_input.text().strip() or "Link"
        url = self.url_input.text().strip() or "https://"
        return text, url


class InsertImageDialog(QDialog):
    """Dialog for inserting markdown image with file browser."""

    def __init__(self, parent=None, base_dir=""):
        super().__init__(parent)
        self.base_dir = base_dir
        self.setWindowTitle("Bild einfügen")
        self.resize(450, 180)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Alternativtext (Alt-Text):"))
        self.alt_input = QLineEdit("Bildbeschreibung")
        layout.addWidget(self.alt_input)

        layout.addWidget(QLabel("Bild-Pfad oder URL:"))
        path_box = QHBoxLayout()
        self.url_input = QLineEdit()
        self.browse_btn = QPushButton("Datei auswählen...")
        self.browse_btn.clicked.connect(self._browse_file)
        path_box.addWidget(self.url_input)
        path_box.addWidget(self.browse_btn)
        layout.addLayout(path_box)

        btn_box = QHBoxLayout()
        self.ok_btn = QPushButton("Einfügen")
        self.ok_btn.setDefault(True)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Abbrechen")
        self.cancel_btn.clicked.connect(self.reject)
        btn_box.addStretch()
        btn_box.addWidget(self.cancel_btn)
        btn_box.addWidget(self.ok_btn)
        layout.addLayout(btn_box)

    def _browse_file(self):
        start_dir = self.base_dir if (self.base_dir and os.path.exists(self.base_dir)) else os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Bilddatei auswählen",
            start_dir,
            "Bilder (*.png *.jpg *.jpeg *.gif *.svg *.webp *.bmp);;Alle Dateien (*.*)"
        )
        if path:
            if self.base_dir:
                try:
                    rel_path = os.path.relpath(path, self.base_dir).replace("\\", "/")
                    self.url_input.setText(rel_path)
                    return
                except ValueError:
                    pass
            self.url_input.setText(path.replace("\\", "/"))

    def get_data(self):
        alt = self.alt_input.text().strip() or "Bild"
        url = self.url_input.text().strip()
        return alt, url


class InsertTableDialog(QDialog):
    """Dialog for inserting markdown table."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tabelle einfügen")
        self.resize(300, 160)

        layout = QVBoxLayout(self)

        row_box = QHBoxLayout()
        row_box.addWidget(QLabel("Zeilen (inkl. Kopfzeile):"))
        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(2, 50)
        self.rows_spin.setValue(4)
        row_box.addWidget(self.rows_spin)
        layout.addLayout(row_box)

        col_box = QHBoxLayout()
        col_box.addWidget(QLabel("Spalten:"))
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, 20)
        self.cols_spin.setValue(3)
        col_box.addWidget(self.cols_spin)
        layout.addLayout(col_box)

        btn_box = QHBoxLayout()
        self.ok_btn = QPushButton("Einfügen")
        self.ok_btn.setDefault(True)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Abbrechen")
        self.cancel_btn.clicked.connect(self.reject)
        btn_box.addStretch()
        btn_box.addWidget(self.cancel_btn)
        btn_box.addWidget(self.ok_btn)
        layout.addLayout(btn_box)

    def get_data(self):
        return self.rows_spin.value(), self.cols_spin.value()


class FileAssociationDialog(QDialog):
    """
    Dialog for configuring Windows OS file associations for .md and .markdown.
    Allows user-level or system-wide admin association and removal.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Windows Dateiverknüpfung verwalten")
        self.resize(480, 260)

        layout = QVBoxLayout(self)

        info_lbl = QLabel(
            "Verknüpfen Sie Markdown-Dateien (.md, .markdown) direkt mit Markdown Studio,\n"
            "sodass diese per Doppelklick in Windows automatisch geöffnet werden."
        )
        info_lbl.setWordWrap(True)
        layout.addWidget(info_lbl)

        # Status Group
        status_group = QGroupBox("Aktueller Status")
        status_layout = QVBoxLayout(status_group)

        self.user_status_lbl = QLabel()
        self.admin_status_lbl = QLabel()
        status_layout.addWidget(self.user_status_lbl)
        status_layout.addWidget(self.admin_status_lbl)
        layout.addWidget(status_group)

        self._refresh_status()

        # Action buttons
        btn_user = QPushButton("📌 Für aktuellen Benutzer verknüpfen (Keine Admin-Rechte erforderlich)")
        btn_user.clicked.connect(self._register_user)
        layout.addWidget(btn_user)

        btn_admin = QPushButton("🛡️ Für alle Benutzer verknüpfen (Benötigt Admin-Rechte)")
        btn_admin.clicked.connect(self._register_admin)
        layout.addWidget(btn_admin)

        btn_remove = QPushButton("❌ Verknüpfung entfernen")
        btn_remove.clicked.connect(self._unregister)
        layout.addWidget(btn_remove)

        close_btn = QPushButton("Schließen")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _refresh_status(self):
        is_user = is_associated(all_users=False)
        is_admin = is_associated(all_users=True)

        user_text = "✅ Verknüpft" if is_user else "⚪ Nicht verknüpft"
        admin_text = "✅ Verknüpft" if is_admin else "⚪ Nicht verknüpft"

        self.user_status_lbl.setText(f"Aktueller Benutzer (HKCU):  <b>{user_text}</b>")
        self.admin_status_lbl.setText(f"Alle Benutzer (HKLM):  <b>{admin_text}</b>")

    def _register_user(self):
        success, msg = register_association(all_users=False)
        if success:
            QMessageBox.information(self, "Dateiverknüpfung", msg)
        else:
            QMessageBox.warning(self, "Hinweis", msg)
        self._refresh_status()

    def _register_admin(self):
        success, msg = register_association(all_users=True)
        if success:
            QMessageBox.information(self, "Dateiverknüpfung", msg)
        else:
            QMessageBox.warning(self, "Admin-Rechte erforderlich", msg)
        self._refresh_status()

    def _unregister(self):
        # Try unregistering both
        ok_u, msg_u = unregister_association(all_users=False)
        ok_a, msg_a = unregister_association(all_users=True)
        QMessageBox.information(
            self, "Verknüpfung",
            f"Ergebnis Benutzer: {msg_u}\nErgebnis Alle Benutzer: {msg_a}"
        )
        self._refresh_status()


class FindReplaceBar(QWidget):
    """Inline dockable Find & Replace bar at the bottom of the editor."""

    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setVisible(False)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)

        # Find row
        find_box = QHBoxLayout()
        find_box.addWidget(QLabel("Suchen:"))
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Suchbegriff...")
        self.find_input.returnPressed.connect(self.find_next)
        find_box.addWidget(self.find_input)

        self.btn_next = QPushButton("Nächstes")
        self.btn_next.clicked.connect(self.find_next)
        find_box.addWidget(self.btn_next)

        self.btn_prev = QPushButton("Vorheriges")
        self.btn_prev.clicked.connect(self.find_prev)
        find_box.addWidget(self.btn_prev)

        self.case_check = QCheckBox("Groß-/Kleinschreibung")
        find_box.addWidget(self.case_check)

        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedWidth(30)
        self.btn_close.clicked.connect(self.close_bar)
        find_box.addWidget(self.btn_close)

        main_layout.addLayout(find_box)

        # Replace row
        replace_box = QHBoxLayout()
        replace_box.addWidget(QLabel("Ersetzen:"))
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Ersetzen durch...")
        replace_box.addWidget(self.replace_input)

        self.btn_replace = QPushButton("Ersetzen")
        self.btn_replace.clicked.connect(self.replace_one)
        replace_box.addWidget(self.btn_replace)

        self.btn_replace_all = QPushButton("Alle ersetzen")
        self.btn_replace_all.clicked.connect(self.replace_all)
        replace_box.addWidget(self.btn_replace_all)

        main_layout.addLayout(replace_box)

    def show_find(self):
        self.setVisible(True)
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            self.find_input.setText(cursor.selectedText())
        self.find_input.setFocus()
        self.find_input.selectAll()

    def close_bar(self):
        self.setVisible(False)
        self.editor.setFocus()

    def _get_find_flags(self, backwards=False):
        flags = QTextDocument.FindFlag(0)
        if self.case_check.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if backwards:
            flags |= QTextDocument.FindFlag.FindBackward
        return flags

    def find_next(self):
        query = self.find_input.text()
        if not query:
            return
        flags = self._get_find_flags(backwards=False)
        found = self.editor.find(query, flags)
        if not found:
            # Wrap around to start
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.editor.setTextCursor(cursor)
            self.editor.find(query, flags)

    def find_prev(self):
        query = self.find_input.text()
        if not query:
            return
        flags = self._get_find_flags(backwards=True)
        found = self.editor.find(query, flags)
        if not found:
            # Wrap around to end
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.editor.setTextCursor(cursor)
            self.editor.find(query, flags)

    def replace_one(self):
        cursor = self.editor.textCursor()
        query = self.find_input.text()
        replacement = self.replace_input.text()

        if cursor.hasSelection() and (
            cursor.selectedText() == query or
            (not self.case_check.isChecked() and cursor.selectedText().lower() == query.lower())
        ):
            cursor.insertText(replacement)
            self.find_next()
        else:
            self.find_next()

    def replace_all(self):
        query = self.find_input.text()
        replacement = self.replace_input.text()
        if not query:
            return

        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.editor.setTextCursor(cursor)

        flags = self._get_find_flags()
        count = 0
        self.editor.document().undoStack()  # group undos
        while self.editor.find(query, flags):
            c = self.editor.textCursor()
            c.insertText(replacement)
            count += 1

        QMessageBox.information(self, "Ersetzen", f"{count} Vorkommen ersetzt.")

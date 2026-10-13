"""
Main Application Window for Markdown Studio.
Features visual preview-mode editing as primary workspace,
a collapsible right-hand code view, and clean toolbars.
"""

import os
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QToolBar, QStatusBar, QLabel, QFileDialog, QMessageBox,
    QToolButton, QPushButton, QFrame
)
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QFont, QCloseEvent, QDragEnterEvent, QDropEvent
from PyQt6.QtCore import Qt, QTimer, QSettings

from src.visual_editor import VisualEditor
from src.editor import MarkdownEditor
from src.print_manager import PrintManager
from src.dialogs import (
    InsertLinkDialog, InsertImageDialog, InsertTableDialog,
    FileAssociationDialog, FindReplaceBar
)


DEFAULT_DOCUMENT = """# Willkommen bei Markdown Studio!

Markdown Studio ist ein schneller, moderner **Markdown Viewer und Editor** für Windows.

---

## ✨ Features im Überblick
- 📝 **Vorschau-Bearbeitung:** Schreiben und formatieren Sie direkt im gestalteten Vorschaumodus
- 💻 **Ausklappbare Code-Ansicht:** Blenden Sie den Markdown-Quellcode bei Bedarf rechts ein
- 🖨️ **Drucken & PDF:** Professionelles Drucken und hochauflösender PDF-Export direkt über die Steuerelementleiste
- ⚙️ **Windows-Integration:** Automatische `.md`-Dateiverknüpfung für alle Benutzer (Admin) oder den aktuellen Benutzer
- 🎨 **Formatierungsleiste:** Fett, Kursiv, Überschriften, Listen, Tabellen, Checkboxen und Code

---

## 📋 Aufgabenliste / Checkliste
- [x] Markdown Studio installieren
- [x] Dateiverknüpfung für .md Dateien aktivieren
- [ ] Erstes Dokument erstellen und drucken

---

## 📊 Beispieltabelle

| Funktion | Status | Tastenkürzel |
| :--- | :--- | :--- |
| Speichern | Unterstützt | `Strg + S` |
| Drucken | Unterstützt | `Strg + P` |
| Suchen & Ersetzen | Unterstützt | `Strg + F` |
| Fett / Kursiv | Unterstützt | `Strg + B` / `Strg + I` |

---

## 💻 Code-Beispiel

```python
def begruessung(name):
    print(f"Hallo {name}, viel Spaß mit Markdown Studio!")

begruessung("Benutzer")
```

> **Hinweis:** Die Code-Ansicht rechts kann jederzeit über die Schaltfläche **Code-Ansicht** in der Leiste ein- oder ausgeklappt werden.
"""


class MainWindow(QMainWindow):
    """Main window of Markdown Studio."""

    def _get_bool_setting(self, key: str, default: bool = False) -> bool:
        val = self.settings.value(key, default)
        if isinstance(val, bool):
            return val
        return str(val).lower() in ("true", "1", "yes")

    def __init__(self, initial_file=None):
        super().__init__()

        self.current_file_path = None
        self.is_modified = False
        self.dark_mode = False
        self._is_syncing = False
        self.settings = QSettings("MarkdownStudio", "Settings")

        # Load saved preferences
        self.dark_mode = self._get_bool_setting("dark_mode", False)
        show_code_saved = self._get_bool_setting("show_code_panel", False)

        self.setWindowTitle("Markdown Studio")
        self.resize(1150, 750)
        self.setAcceptDrops(True)

        # Set application icon if available
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "app_icon.ico"))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Core Components
        self._init_ui()
        self._init_menus()
        self._init_toolbars()
        self._init_statusbar()

        # Timers for smooth two-way sync
        self.sync_to_code_timer = QTimer(self)
        self.sync_to_code_timer.setSingleShot(True)
        self.sync_to_code_timer.setInterval(120)
        self.sync_to_code_timer.timeout.connect(self._sync_visual_to_code)

        self.sync_to_visual_timer = QTimer(self)
        self.sync_to_visual_timer.setSingleShot(True)
        self.sync_to_visual_timer.setInterval(150)
        self.sync_to_visual_timer.timeout.connect(self._sync_code_to_visual)

        # Connect text changes
        self.visual_editor.textChanged.connect(self._on_visual_text_changed)
        self.code_editor.textChanged.connect(self._on_code_text_changed)

        # Initial code panel visibility
        self.set_code_panel_visible(show_code_saved)

        # Load initial file or default sample text
        if initial_file and os.path.exists(initial_file):
            self.load_file(initial_file)
        else:
            self._is_syncing = True
            self.visual_editor.set_markdown_content(DEFAULT_DOCUMENT)
            self.code_editor.setPlainText(DEFAULT_DOCUMENT)
            self._is_syncing = False
            self.set_modified(False)
            self._update_window_title()

    def _init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Splitter: Left = Visual Editor (Preview Mode), Right = Collapsible Code View
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # 1. Left container: Visual Preview Editor + Find Bar
        visual_container = QWidget()
        visual_layout = QVBoxLayout(visual_container)
        visual_layout.setContentsMargins(0, 0, 0, 0)
        visual_layout.setSpacing(0)

        self.visual_editor = VisualEditor(self, dark_mode=self.dark_mode)
        visual_layout.addWidget(self.visual_editor)

        self.find_bar = FindReplaceBar(self.visual_editor, self)
        visual_layout.addWidget(self.find_bar)

        # 2. Right container: Collapsible Code Panel
        self.code_panel = QWidget()
        code_layout = QVBoxLayout(self.code_panel)
        code_layout.setContentsMargins(0, 0, 0, 0)
        code_layout.setSpacing(0)

        # Code panel header
        code_header = QFrame()
        code_header.setStyleSheet("""
            QFrame {
                background-color: #f1f3f5;
                border-bottom: 1px solid #d0d7de;
                padding: 4px 8px;
            }
        """)
        header_layout = QHBoxLayout(code_header)
        header_layout.setContentsMargins(8, 4, 6, 4)

        header_lbl = QLabel("💻 Markdown-Quellcode")
        header_lbl.setStyleSheet("font-weight: 600; color: #24292f;")
        header_layout.addWidget(header_lbl)
        header_layout.addStretch()

        btn_close_panel = QPushButton("✕")
        btn_close_panel.setToolTip("Code-Ansicht zuklappen")
        btn_close_panel.setFixedSize(22, 22)
        btn_close_panel.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 3px;
                color: #57606a;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e1e4e8;
                color: #24292f;
            }
        """)
        btn_close_panel.clicked.connect(lambda: self.set_code_panel_visible(False))
        header_layout.addWidget(btn_close_panel)

        code_layout.addWidget(code_header)

        # Code editor (with line numbers & syntax highlighter)
        self.code_editor = MarkdownEditor(self, dark_mode=self.dark_mode)
        code_layout.addWidget(self.code_editor)

        # Assemble Splitter
        self.splitter.addWidget(visual_container)
        self.splitter.addWidget(self.code_panel)
        self.splitter.setSizes([750, 400])

        main_layout.addWidget(self.splitter)

        # Connect cursor position
        self.visual_editor.cursor_position_changed_info.connect(self._on_cursor_pos_changed)

    def _init_menus(self):
        menu_bar = self.menuBar()

        # --- DATEI ---
        file_menu = menu_bar.addMenu("&Datei")

        self.act_new = QAction("📄 Neu", self)
        self.act_new.setShortcut(QKeySequence.StandardKey.New)
        self.act_new.triggered.connect(self.new_file)
        file_menu.addAction(self.act_new)

        self.act_open = QAction("📂 Öffnen...", self)
        self.act_open.setShortcut(QKeySequence.StandardKey.Open)
        self.act_open.triggered.connect(self.open_file)
        file_menu.addAction(self.act_open)

        self.recent_menu = file_menu.addMenu("🕒 Zuletzt geöffnet")
        self._update_recent_files_menu()

        file_menu.addSeparator()

        self.act_save = QAction("💾 Speichern", self)
        self.act_save.setShortcut(QKeySequence.StandardKey.Save)
        self.act_save.triggered.connect(self.save_file)
        file_menu.addAction(self.act_save)

        self.act_save_as = QAction("💾 Speichern unter...", self)
        self.act_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.act_save_as.triggered.connect(self.save_file_as)
        file_menu.addAction(self.act_save_as)

        file_menu.addSeparator()

        self.act_print = QAction("🖨️ Drucken...", self)
        self.act_print.setShortcut(QKeySequence.StandardKey.Print)
        self.act_print.triggered.connect(self.print_document)
        file_menu.addAction(self.act_print)

        self.act_print_preview = QAction("🔍 Druckvorschau...", self)
        self.act_print_preview.setShortcut("Ctrl+Shift+P")
        self.act_print_preview.triggered.connect(self.print_preview)
        file_menu.addAction(self.act_print_preview)

        self.act_export_pdf = QAction("📑 Als PDF exportieren...", self)
        self.act_export_pdf.triggered.connect(self.export_pdf)
        file_menu.addAction(self.act_export_pdf)

        file_menu.addSeparator()

        act_exit = QAction("Beenden", self)
        act_exit.setShortcut("Ctrl+Q")
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        # --- BEARBEITEN ---
        edit_menu = menu_bar.addMenu("&Bearbeiten")

        act_undo = QAction("Rückgängig", self)
        act_undo.setShortcut(QKeySequence.StandardKey.Undo)
        act_undo.triggered.connect(self.visual_editor.undo)
        edit_menu.addAction(act_undo)

        act_redo = QAction("Wiederholen", self)
        act_redo.setShortcut(QKeySequence.StandardKey.Redo)
        act_redo.triggered.connect(self.visual_editor.redo)
        edit_menu.addAction(act_redo)

        edit_menu.addSeparator()

        act_cut = QAction("Ausschneiden", self)
        act_cut.setShortcut(QKeySequence.StandardKey.Cut)
        act_cut.triggered.connect(self.visual_editor.cut)
        edit_menu.addAction(act_cut)

        act_copy = QAction("Kopieren", self)
        act_copy.setShortcut(QKeySequence.StandardKey.Copy)
        act_copy.triggered.connect(self.visual_editor.copy)
        edit_menu.addAction(act_copy)

        act_paste = QAction("Einfügen", self)
        act_paste.setShortcut(QKeySequence.StandardKey.Paste)
        act_paste.triggered.connect(self.visual_editor.paste)
        edit_menu.addAction(act_paste)

        act_select_all = QAction("Alles auswählen", self)
        act_select_all.setShortcut(QKeySequence.StandardKey.SelectAll)
        act_select_all.triggered.connect(self.visual_editor.selectAll)
        edit_menu.addAction(act_select_all)

        edit_menu.addSeparator()

        self.act_find = QAction("🔍 Suchen & Ersetzen...", self)
        self.act_find.setShortcut(QKeySequence.StandardKey.Find)
        self.act_find.triggered.connect(self.find_bar.show_find)
        edit_menu.addAction(self.act_find)

        # --- FORMATIEREN ---
        format_menu = menu_bar.addMenu("&Formatieren")

        self.act_bold = QAction("Fett (Bold)", self)
        self.act_bold.setShortcut(QKeySequence.StandardKey.Bold)
        self.act_bold.triggered.connect(self.visual_editor.apply_bold)
        format_menu.addAction(self.act_bold)

        self.act_italic = QAction("Kursiv (Italic)", self)
        self.act_italic.setShortcut(QKeySequence.StandardKey.Italic)
        self.act_italic.triggered.connect(self.visual_editor.apply_italic)
        format_menu.addAction(self.act_italic)

        self.act_strike = QAction("Durchgestrichen", self)
        self.act_strike.triggered.connect(self.visual_editor.apply_strikethrough)
        format_menu.addAction(self.act_strike)

        format_menu.addSeparator()

        self.act_h1 = QAction("Überschrift 1 (#)", self)
        self.act_h1.setShortcut("Ctrl+1")
        self.act_h1.triggered.connect(lambda: self.visual_editor.apply_heading(1))
        format_menu.addAction(self.act_h1)

        self.act_h2 = QAction("Überschrift 2 (##)", self)
        self.act_h2.setShortcut("Ctrl+2")
        self.act_h2.triggered.connect(lambda: self.visual_editor.apply_heading(2))
        format_menu.addAction(self.act_h2)

        self.act_h3 = QAction("Überschrift 3 (###)", self)
        self.act_h3.setShortcut("Ctrl+3")
        self.act_h3.triggered.connect(lambda: self.visual_editor.apply_heading(3))
        format_menu.addAction(self.act_h3)

        format_menu.addSeparator()

        self.act_bullet_list = QAction("Aufzählungsliste (-)", self)
        self.act_bullet_list.triggered.connect(self.visual_editor.apply_bullet_list)
        format_menu.addAction(self.act_bullet_list)

        self.act_num_list = QAction("Nummerierte Liste (1.)", self)
        self.act_num_list.triggered.connect(self.visual_editor.apply_numbered_list)
        format_menu.addAction(self.act_num_list)

        self.act_task_list = QAction("Checkliste (- [ ])", self)
        self.act_task_list.setShortcut("Ctrl+Shift+C")
        self.act_task_list.triggered.connect(self.visual_editor.apply_task_list)
        format_menu.addAction(self.act_task_list)

        self.act_quote = QAction("Zitat (>)", self)
        self.act_quote.triggered.connect(self.visual_editor.apply_quote)
        format_menu.addAction(self.act_quote)

        format_menu.addSeparator()

        self.act_code_inline = QAction("Inline-Code (`)", self)
        self.act_code_inline.triggered.connect(self.visual_editor.apply_code_inline)
        format_menu.addAction(self.act_code_inline)

        self.act_code_block = QAction("Code-Block (```)", self)
        self.act_code_block.triggered.connect(lambda: self.visual_editor.apply_code_block("python"))
        format_menu.addAction(self.act_code_block)

        format_menu.addSeparator()

        self.act_link = QAction("Link einfügen...", self)
        self.act_link.setShortcut("Ctrl+K")
        self.act_link.triggered.connect(self._dialog_insert_link)
        format_menu.addAction(self.act_link)

        self.act_image = QAction("Bild einfügen...", self)
        self.act_image.triggered.connect(self._dialog_insert_image)
        format_menu.addAction(self.act_image)

        self.act_table = QAction("Tabelle einfügen...", self)
        self.act_table.triggered.connect(self._dialog_insert_table)
        format_menu.addAction(self.act_table)

        self.act_hr = QAction("Horizontale Trennlinie (---)", self)
        self.act_hr.triggered.connect(self.visual_editor.insert_horizontal_rule)
        format_menu.addAction(self.act_hr)

        # --- ANSICHT ---
        view_menu = menu_bar.addMenu("&Ansicht")

        self.act_toggle_code = QAction("💻 Code-Ansicht rechts (F12)", self, checkable=True)
        self.act_toggle_code.setShortcut("F12")
        self.act_toggle_code.toggled.connect(self.set_code_panel_visible)
        view_menu.addAction(self.act_toggle_code)

        view_menu.addSeparator()

        self.act_theme = QAction("🌙 Dunkelmodus umschalten", self)
        self.act_theme.triggered.connect(self.toggle_dark_mode)
        view_menu.addAction(self.act_theme)

        # --- EXTRAS ---
        tools_menu = menu_bar.addMenu("&Extras")

        self.act_assoc = QAction("⚙️ Windows .md-Dateiverknüpfung verwalten...", self)
        self.act_assoc.triggered.connect(self.manage_file_association)
        tools_menu.addAction(self.act_assoc)

        act_load_sample = QAction("Beispielvorlage laden", self)
        act_load_sample.triggered.connect(self._load_sample_template)
        tools_menu.addAction(act_load_sample)

        # --- HILFE ---
        help_menu = menu_bar.addMenu("&Hilfe")

        act_syntax = QAction("Markdown-Syntax Hilfe", self)
        act_syntax.triggered.connect(self._show_syntax_help)
        help_menu.addAction(act_syntax)

        act_about = QAction("Über Markdown Studio", self)
        act_about.triggered.connect(self._show_about)
        help_menu.addAction(act_about)

    def _init_toolbars(self):
        # 1. Haupt-Toolbar (Datei, Speichern, Drucken, Ausklappbare Code-Ansicht)
        self.main_toolbar = QToolBar("Haupt-Steuerelemente", self)
        self.main_toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.main_toolbar)

        self.main_toolbar.addAction(self.act_new)
        self.main_toolbar.addAction(self.act_open)
        self.main_toolbar.addAction(self.act_save)
        self.main_toolbar.addAction(self.act_save_as)
        self.main_toolbar.addSeparator()

        # DRUCKEN UND PDF - Prominent in der Leiste
        self.main_toolbar.addAction(self.act_print)
        self.main_toolbar.addAction(self.act_print_preview)
        self.main_toolbar.addAction(self.act_export_pdf)
        self.main_toolbar.addSeparator()

        # AUSKLAPPBARE CODE-ANSICHT (Toggle-Button)
        self.btn_toggle_code = QToolButton()
        self.btn_toggle_code.setText("💻 Code-Ansicht")
        self.btn_toggle_code.setToolTip("Markdown-Quellcode rechts ein- oder ausblenden (F12)")
        self.btn_toggle_code.setCheckable(True)
        self.btn_toggle_code.toggled.connect(self.set_code_panel_visible)
        self.main_toolbar.addWidget(self.btn_toggle_code)

        # 2. Formatierungs-Toolbar (Markdown Standardformatierungen)
        self.format_toolbar = QToolBar("Formatierung", self)
        self.format_toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.format_toolbar)

        # Text Style
        btn_bold = self.format_toolbar.addAction("𝐁")
        btn_bold.setToolTip("Fett (Strg+B)")
        btn_bold.triggered.connect(self.visual_editor.apply_bold)

        btn_italic = self.format_toolbar.addAction("𝐼")
        btn_italic.setToolTip("Kursiv (Strg+I)")
        btn_italic.triggered.connect(self.visual_editor.apply_italic)

        btn_strike = self.format_toolbar.addAction("S̶")
        btn_strike.setToolTip("Durchgestrichen")
        btn_strike.triggered.connect(self.visual_editor.apply_strikethrough)

        self.format_toolbar.addSeparator()

        # Headings
        btn_h1 = self.format_toolbar.addAction("H1")
        btn_h1.setToolTip("Überschrift 1 (Strg+1)")
        btn_h1.triggered.connect(lambda: self.visual_editor.apply_heading(1))

        btn_h2 = self.format_toolbar.addAction("H2")
        btn_h2.setToolTip("Überschrift 2 (Strg+2)")
        btn_h2.triggered.connect(lambda: self.visual_editor.apply_heading(2))

        btn_h3 = self.format_toolbar.addAction("H3")
        btn_h3.setToolTip("Überschrift 3 (Strg+3)")
        btn_h3.triggered.connect(lambda: self.visual_editor.apply_heading(3))

        self.format_toolbar.addSeparator()

        # Lists & Tasks
        btn_bullet = self.format_toolbar.addAction("• Liste")
        btn_bullet.setToolTip("Aufzählungsliste")
        btn_bullet.triggered.connect(self.visual_editor.apply_bullet_list)

        btn_num = self.format_toolbar.addAction("1. Liste")
        btn_num.setToolTip("Nummerierte Liste")
        btn_num.triggered.connect(self.visual_editor.apply_numbered_list)

        btn_task = self.format_toolbar.addAction("☑ Checkliste")
        btn_task.setToolTip("Checkliste / Aufgabenliste (Strg+Umschalt+C)")
        btn_task.triggered.connect(self.visual_editor.apply_task_list)

        btn_quote = self.format_toolbar.addAction("❝ Zitat")
        btn_quote.setToolTip("Blockquote / Zitat")
        btn_quote.triggered.connect(self.visual_editor.apply_quote)

        self.format_toolbar.addSeparator()

        # Code
        btn_code = self.format_toolbar.addAction("<> Code")
        btn_code.setToolTip("Inline-Code (`)")
        btn_code.triggered.connect(self.visual_editor.apply_code_inline)

        btn_block = self.format_toolbar.addAction("📦 Block")
        btn_block.setToolTip("Code-Block (```)")
        btn_block.triggered.connect(lambda: self.visual_editor.apply_code_block("python"))

        self.format_toolbar.addSeparator()

        # Media & Tables
        btn_link = self.format_toolbar.addAction("🔗 Link")
        btn_link.setToolTip("Link einfügen (Strg+K)")
        btn_link.triggered.connect(self._dialog_insert_link)

        btn_img = self.format_toolbar.addAction("🖼 Bild")
        btn_img.setToolTip("Bild einfügen")
        btn_img.triggered.connect(self._dialog_insert_image)

        btn_table = self.format_toolbar.addAction("📊 Tabelle")
        btn_table.setToolTip("Tabelle einfügen")
        btn_table.triggered.connect(self._dialog_insert_table)

        btn_hr = self.format_toolbar.addAction("➖ Linie")
        btn_hr.setToolTip("Horizontale Trennlinie")
        btn_hr.triggered.connect(self.visual_editor.insert_horizontal_rule)

        self.format_toolbar.addSeparator()

        btn_find = self.format_toolbar.addAction("🔍 Suchen")
        btn_find.setToolTip("Suchen und Ersetzen (Strg+F)")
        btn_find.triggered.connect(self.find_bar.show_find)

    def _init_statusbar(self):
        status = QStatusBar(self)
        self.setStatusBar(status)

        self.status_file_info = QLabel("Unbenannt")
        self.status_file_info.setStyleSheet("padding-left: 8px;")
        status.addWidget(self.status_file_info, stretch=1)

        self.status_modified = QLabel("● Gespeichert")
        self.status_modified.setStyleSheet("color: #107c41; font-weight: bold; padding: 0 10px;")
        status.addPermanentWidget(self.status_modified)

        self.status_cursor = QLabel("Zeile: 1, Spalte: 1")
        self.status_cursor.setStyleSheet("padding: 0 10px;")
        status.addPermanentWidget(self.status_cursor)

        self.status_stats = QLabel("Wörter: 0 | Zeichen: 0")
        self.status_stats.setStyleSheet("padding: 0 10px;")
        status.addPermanentWidget(self.status_stats)

        self.status_encoding = QLabel("UTF-8")
        self.status_encoding.setStyleSheet("padding: 0 10px;")
        status.addPermanentWidget(self.status_encoding)

    # --- Collapsible Code View Control ---
    def set_code_panel_visible(self, visible: bool):
        self.code_panel.setVisible(visible)
        self.btn_toggle_code.blockSignals(True)
        self.btn_toggle_code.setChecked(visible)
        self.btn_toggle_code.blockSignals(False)

        self.act_toggle_code.blockSignals(True)
        self.act_toggle_code.setChecked(visible)
        self.act_toggle_code.blockSignals(False)

        self.settings.setValue("show_code_panel", visible)

        if visible:
            # Sync content immediately when opened
            self._sync_visual_to_code()
            self.splitter.setSizes([750, 400])

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.settings.setValue("dark_mode", self.dark_mode)
        self.visual_editor.set_dark_mode(self.dark_mode)
        self.code_editor.set_dark_mode(self.dark_mode)
        self.act_theme.setText("☀️ Hellmodus" if self.dark_mode else "🌙 Dunkelmodus umschalten")

    # --- Text Synchronization ---
    def _on_visual_text_changed(self):
        if self._is_syncing:
            return
        if not self.is_modified:
            self.set_modified(True)
        self._update_stats()
        if self.code_panel.isVisible():
            self.sync_to_code_timer.start()

    def _on_code_text_changed(self):
        if self._is_syncing:
            return
        if not self.is_modified:
            self.set_modified(True)
        self._update_stats()
        self.sync_to_visual_timer.start()

    def _sync_visual_to_code(self):
        if self._is_syncing:
            return
        self._is_syncing = True
        md = self.visual_editor.get_markdown_content()
        self.code_editor.setPlainText(md)
        self._is_syncing = False

    def _sync_code_to_visual(self):
        if self._is_syncing:
            return
        self._is_syncing = True
        md = self.code_editor.toPlainText()
        self.visual_editor.set_markdown_content(md)
        self._is_syncing = False

    def _update_stats(self):
        text = self.visual_editor.toPlainText()
        chars = len(text)
        words = len(text.split())
        self.status_stats.setText(f"Wörter: {words} | Zeichen: {chars}")

    def _on_cursor_pos_changed(self, line: int, col: int):
        self.status_cursor.setText(f"Zeile: {line}, Spalte: {col}")

    def set_modified(self, modified: bool):
        self.is_modified = modified
        if modified:
            self.status_modified.setText("● Geändert")
            self.status_modified.setStyleSheet("color: #d83b01; font-weight: bold; padding: 0 10px;")
        else:
            self.status_modified.setText("● Gespeichert")
            self.status_modified.setStyleSheet("color: #107c41; font-weight: bold; padding: 0 10px;")
        self._update_window_title()

    def _update_window_title(self):
        name = os.path.basename(self.current_file_path) if self.current_file_path else "Unbenannt.md"
        prefix = "* " if self.is_modified else ""
        self.setWindowTitle(f"{prefix}{name} - Markdown Studio")
        self.status_file_info.setText(self.current_file_path or "Unbenannt (nicht gespeichert)")

    # --- File Operations ---
    def new_file(self):
        if not self._maybe_save_changes():
            return
        self._is_syncing = True
        self.visual_editor.clear()
        self.code_editor.clear()
        self._is_syncing = False
        self.current_file_path = None
        self.set_modified(False)
        self._update_window_title()

    def open_file(self):
        if not self._maybe_save_changes():
            return
        start_dir = os.path.dirname(self.current_file_path) if self.current_file_path else os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Markdown-Datei öffnen",
            start_dir,
            "Markdown-Dateien (*.md *.markdown *.mdown *.mkd);;Textdateien (*.txt);;Alle Dateien (*.*)"
        )
        if path:
            self.load_file(path)

    def load_file(self, path: str):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(path, "r", encoding="latin-1") as f:
                    content = f.read()
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Datei konnte nicht gelesen werden:\n{e}")
                return
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Öffnen der Datei:\n{e}")
            return

        self.current_file_path = os.path.abspath(path)
        self._is_syncing = True
        self.visual_editor.set_markdown_content(content)
        self.code_editor.setPlainText(content)
        self._is_syncing = False
        self.set_modified(False)
        self._update_window_title()
        self._add_recent_file(self.current_file_path)

    def save_file(self) -> bool:
        if not self.current_file_path:
            return self.save_file_as()

        try:
            content = self.visual_editor.get_markdown_content()
            with open(self.current_file_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.set_modified(False)
            self._add_recent_file(self.current_file_path)
            self.statusBar().showMessage("Datei erfolgreich gespeichert.", 3000)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Fehler beim Speichern", f"Datei konnte nicht gespeichert werden:\n{e}")
            return False

    def save_file_as(self) -> bool:
        start_dir = self.current_file_path or os.path.expanduser("~/Dokument.md")
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Markdown-Datei speichern unter",
            start_dir,
            "Markdown-Dateien (*.md);;Markdown (*.markdown);;Alle Dateien (*.*)"
        )
        if not path:
            return False

        if not (path.endswith(".md") or path.endswith(".markdown")):
            path += ".md"

        self.current_file_path = os.path.abspath(path)
        return self.save_file()

    def _maybe_save_changes(self) -> bool:
        """Prompt to save changes before closing or opening new file."""
        if not self.is_modified:
            return True

        filename = os.path.basename(self.current_file_path) if self.current_file_path else "Unbenannt"
        reply = QMessageBox.question(
            self,
            "Änderungen speichern?",
            f"Möchten Sie die Änderungen an '{filename}' speichern?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save
        )

        if reply == QMessageBox.StandardButton.Save:
            return self.save_file()
        elif reply == QMessageBox.StandardButton.Discard:
            return True
        else:
            return False

    def _add_recent_file(self, path: str):
        recents = self.settings.value("recent_files", [], type=list)
        if path in recents:
            recents.remove(path)
        recents.insert(0, path)
        recents = recents[:10]
        self.settings.setValue("recent_files", recents)
        self._update_recent_files_menu()

    def _update_recent_files_menu(self):
        self.recent_menu.clear()
        recents = self.settings.value("recent_files", [], type=list)
        if not recents:
            act = self.recent_menu.addAction("Keine Einträge")
            act.setEnabled(False)
            return

        for p in recents:
            if os.path.exists(p):
                act = self.recent_menu.addAction(os.path.basename(p))
                act.setToolTip(p)
                act.triggered.connect(lambda checked, file_path=p: self._open_recent(file_path))

    def _open_recent(self, file_path: str):
        if self._maybe_save_changes():
            self.load_file(file_path)

    # --- Print & PDF Operations ---
    def print_document(self):
        title = os.path.basename(self.current_file_path) if self.current_file_path else "Markdown-Dokument"
        PrintManager.print_document(self, self.visual_editor, title=title)

    def print_preview(self):
        title = os.path.basename(self.current_file_path) if self.current_file_path else "Markdown-Dokument"
        PrintManager.print_preview(self, self.visual_editor, title=title)

    def export_pdf(self):
        default_name = os.path.splitext(self.current_file_path)[0] + ".pdf" if self.current_file_path else "Dokument.pdf"
        PrintManager.export_pdf(self, self.visual_editor, default_filename=default_name)

    # --- Formatting Dialogs ---
    def _dialog_insert_link(self):
        cursor = self.visual_editor.textCursor()
        sel = cursor.selectedText()
        dlg = InsertLinkDialog(self, initial_text=sel)
        if dlg.exec() == InsertLinkDialog.DialogCode.Accepted:
            text, url = dlg.get_data()
            self.visual_editor.insert_link(text, url)

    def _dialog_insert_image(self):
        base_dir = os.path.dirname(self.current_file_path) if self.current_file_path else ""
        dlg = InsertImageDialog(self, base_dir=base_dir)
        if dlg.exec() == InsertImageDialog.DialogCode.Accepted:
            alt, url = dlg.get_data()
            self.visual_editor.insert_image(alt, url)

    def _dialog_insert_table(self):
        dlg = InsertTableDialog(self)
        if dlg.exec() == InsertTableDialog.DialogCode.Accepted:
            rows, cols = dlg.get_data()
            self.visual_editor.insert_table(rows, cols)

    def manage_file_association(self):
        dlg = FileAssociationDialog(self)
        dlg.exec()

    def _load_sample_template(self):
        if self._maybe_save_changes():
            self._is_syncing = True
            self.visual_editor.set_markdown_content(DEFAULT_DOCUMENT)
            self.code_editor.setPlainText(DEFAULT_DOCUMENT)
            self._is_syncing = False
            self.set_modified(True)

    def _show_syntax_help(self):
        help_text = """### Markdown Syntax Kurzreferenz:
- `# Überschrift 1` bis `###### Überschrift 6`
- `**Fett**` oder `__Fett__`
- `*Kursiv*` oder `_Kursiv_`
- `~~Durchgestrichen~~`
- `- Aufzählung` oder `* Aufzählung`
- `1. Nummerierte Liste`
- `- [ ] Offene Aufgabe` / `- [x] Erledigte Aufgabe`
- `> Zitatblock`
- `` `Inline-Code` ``
- ```` ```python \n Code-Block \n ``` ````
- `[Link Text](https://url)`
- `![Bildbeschreibung](pfad/bild.png)`
- `| Tabelle | Spalte |`
- `---` (Trennlinie)
"""
        QMessageBox.information(self, "Markdown Syntax Hilfe", help_text)

    def _show_about(self):
        QMessageBox.about(
            self,
            "Über Markdown Studio",
            "<h2>Markdown Studio</h2>"
            "<p>Version 1.0.0</p>"
            "<p>Ein eleganter, schneller und funktionsreicher Markdown Viewer und Editor für Windows.</p>"
            "<ul>"
            "<li>Bearbeitung direkt im gerenderten Vorschaumodus (WYSIWYG)</li>"
            "<li>Rechts ausklappbare Quellcode-Ansicht mit 2-Wege-Synchronisation</li>"
            "<li>Drucken, Druckvorschau und PDF-Export direkt in der Steuerelementleiste</li>"
            "<li>OS-weite Dateiverknüpfung (.md) für Admin oder Benutzer</li>"
            "</ul>"
        )

    # --- Drag & Drop Support ---
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path and os.path.exists(file_path):
                if self._maybe_save_changes():
                    self.load_file(file_path)
                break
        event.acceptProposedAction()

    def closeEvent(self, event: QCloseEvent):
        if self._maybe_save_changes():
            event.accept()
        else:
            event.ignore()

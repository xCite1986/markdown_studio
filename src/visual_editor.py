"""
WYSIWYG Visual Markdown Editor Widget.
Allows editing directly in rendered Preview Mode while maintaining
full two-way synchronization with standard Markdown.
"""

import re
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import (
    QTextCursor, QTextBlockFormat, QTextCharFormat, QTextListFormat,
    QTextTableFormat, QFont, QColor, QWheelEvent, QKeyEvent
)
from PyQt6.QtCore import Qt, pyqtSignal


class VisualEditor(QTextEdit):
    """
    Rich text editor formatted as live Markdown preview.
    Edits directly in preview mode and serializes to/from clean Markdown.
    """
    cursor_position_changed_info = pyqtSignal(int, int)  # line, col

    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent)
        self.dark_mode = dark_mode
        self.setAcceptRichText(True)
        self.setTabChangesFocus(False)

        # Connect cursor changes
        self.cursorPositionChanged.connect(self._emit_cursor_info)

        self._apply_theme()

    def set_dark_mode(self, dark_mode: bool):
        self.dark_mode = dark_mode
        self._apply_theme()

    def _apply_theme(self):
        if self.dark_mode:
            bg_color = "#1e1e1e"
            text_color = "#e6edf3"
            selection_bg = "#264f78"
            self.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {bg_color};
                    color: {text_color};
                    selection-background-color: {selection_bg};
                    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
                    font-size: 11pt;
                    line-height: 1.6;
                    padding: 20px 28px;
                    border: none;
                }}
            """)
        else:
            bg_color = "#ffffff"
            text_color = "#1f2328"
            selection_bg = "#b4d5fe"
            self.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {bg_color};
                    color: {text_color};
                    selection-background-color: {selection_bg};
                    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
                    font-size: 11pt;
                    line-height: 1.6;
                    padding: 20px 28px;
                    border: none;
                }}
            """)

    def _emit_cursor_info(self):
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.positionInBlock() + 1
        self.cursor_position_changed_info.emit(line, col)

    def set_markdown_content(self, md_text: str):
        """Loads Markdown string into formatted visual document."""
        self.setMarkdown(md_text)

    def get_markdown_content(self) -> str:
        """Serializes current visual document to clean Markdown."""
        return self.toMarkdown()

    # --- Formatting Actions ---

    def apply_bold(self):
        fmt = self.currentCharFormat()
        is_bold = fmt.fontWeight() == QFont.Weight.Bold
        new_weight = QFont.Weight.Normal if is_bold else QFont.Weight.Bold
        fmt.setFontWeight(new_weight)
        self.mergeCurrentCharFormat(fmt)

    def apply_italic(self):
        fmt = self.currentCharFormat()
        fmt.setFontItalic(not fmt.fontItalic())
        self.mergeCurrentCharFormat(fmt)

    def apply_strikethrough(self):
        fmt = self.currentCharFormat()
        fmt.setFontStrikeOut(not fmt.fontStrikeOut())
        self.mergeCurrentCharFormat(fmt)

    def apply_heading(self, level: int = 1):
        cursor = self.textCursor()
        bf = cursor.blockFormat()
        current_level = bf.headingLevel()

        if current_level == level:
            # Toggle back to normal paragraph
            bf.setHeadingLevel(0)
            cursor.setBlockFormat(bf)
            cf = QTextCharFormat()
            cf.setFontPointSize(11)
            cf.setFontWeight(QFont.Weight.Normal)
            cf.setForeground(QColor("#e6edf3" if self.dark_mode else "#1f2328"))
            cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
            cursor.mergeBlockCharFormat(cf)
        else:
            bf.setHeadingLevel(level)
            cursor.setBlockFormat(bf)
            cf = QTextCharFormat()
            sizes = {1: 20, 2: 16, 3: 13, 4: 12, 5: 11, 6: 11}
            cf.setFontPointSize(sizes.get(level, 14))
            cf.setFontWeight(QFont.Weight.Bold)
            heading_color = QColor("#58a6ff" if self.dark_mode else "#0969da")
            cf.setForeground(heading_color)
            cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
            cursor.mergeBlockCharFormat(cf)

    def apply_bullet_list(self):
        cursor = self.textCursor()
        current_list = cursor.currentList()
        if current_list:
            # Remove list format
            bf = cursor.blockFormat()
            bf.setIndent(0)
            cursor.setBlockFormat(bf)
        else:
            list_fmt = QTextListFormat()
            list_fmt.setStyle(QTextListFormat.Style.ListDisc)
            cursor.createList(list_fmt)

    def apply_numbered_list(self):
        cursor = self.textCursor()
        current_list = cursor.currentList()
        if current_list:
            bf = cursor.blockFormat()
            bf.setIndent(0)
            cursor.setBlockFormat(bf)
        else:
            list_fmt = QTextListFormat()
            list_fmt.setStyle(QTextListFormat.Style.ListDecimal)
            cursor.createList(list_fmt)

    def apply_task_list(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        line = cursor.block().text()
        if line.startswith("- [ ] "):
            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 6)
            cursor.insertText("- [x] ")
        elif line.startswith("- [x] "):
            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 6)
            cursor.removeSelectedText()
        else:
            cursor.insertText("- [ ] ")

    def apply_quote(self):
        cursor = self.textCursor()
        bf = cursor.blockFormat()
        current_indent = bf.indent()
        if current_indent > 0:
            bf.setIndent(0)
        else:
            bf.setIndent(1)
        cursor.setBlockFormat(bf)

    def apply_code_inline(self):
        fmt = self.currentCharFormat()
        font = fmt.font()
        if font.family() == "Cascadia Code":
            # Toggle off
            fmt.setFontFamily("Segoe UI")
            fmt.setBackground(QColor(0, 0, 0, 0))
            fmt.setForeground(QColor("#e6edf3" if self.dark_mode else "#1f2328"))
        else:
            fmt.setFontFamily("Cascadia Code")
            fmt.setBackground(QColor("#2b3036" if self.dark_mode else "#f2f4f7"))
            fmt.setForeground(QColor("#f0883e" if self.dark_mode else "#bc4c00"))
        self.mergeCurrentCharFormat(fmt)

    def apply_code_block(self, language: str = ""):
        cursor = self.textCursor()
        cursor.insertBlock()
        bf = QTextBlockFormat()
        bf.setIndent(1)
        cursor.setBlockFormat(bf)

        cf = QTextCharFormat()
        cf.setFontFamily("Cascadia Code")
        cf.setFontPointSize(10)
        cf.setBackground(QColor("#161b22" if self.dark_mode else "#f6f8fa"))
        cf.setForeground(QColor("#79c0ff" if self.dark_mode else "#0550ae"))
        cursor.insertText("```" + language + "\n# Dein Code hier\n```\n", cf)

    def insert_link(self, title: str = "Link-Text", url: str = "https://example.com"):
        cursor = self.textCursor()
        if cursor.hasSelection():
            title = cursor.selectedText()
        cf = QTextCharFormat()
        cf.setAnchor(True)
        cf.setAnchorHref(url)
        cf.setFontUnderline(True)
        cf.setForeground(QColor("#58a6ff" if self.dark_mode else "#0969da"))
        cursor.insertText(title, cf)

    def insert_image(self, alt: str = "Bild", url: str = "bild.png"):
        cursor = self.textCursor()
        cursor.insertText(f"![{alt}]({url})")

    def insert_table(self, rows: int = 3, cols: int = 3):
        cursor = self.textCursor()
        table_fmt = QTextTableFormat()
        table_fmt.setBorder(1)
        table_fmt.setCellPadding(6)
        table_fmt.setCellSpacing(0)
        table_fmt.setBorderCollapse(True)
        table = cursor.insertTable(rows, cols, table_fmt)

        # Header row placeholders
        for c in range(cols):
            table.cellAt(0, c).firstCursorPosition().insertText(f"Spalte {c+1}")

    def insert_horizontal_rule(self):
        cursor = self.textCursor()
        cursor.insertBlock()
        cursor.insertText("---\n")

    def keyPressEvent(self, event: QKeyEvent):
        # Handle Tab
        if event.key() == Qt.Key.Key_Tab:
            self.insertPlainText("    ")
            return
        super().keyPressEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoomIn(1)
            elif delta < 0:
                self.zoomOut(1)
            event.accept()
            return
        super().wheelEvent(event)

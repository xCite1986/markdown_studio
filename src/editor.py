"""
Markdown Source Code Editor Widget.
Includes Line Numbers, Syntax Highlighting, Smart Auto-Indent,
and helper methods for all standard Markdown formatting components.
"""

from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PyQt6.QtGui import (
    QColor, QPainter, QTextFormat, QTextCursor, QFont, QKeyEvent, QWheelEvent
)
from PyQt6.QtCore import Qt, QRect, QSize, pyqtSignal

from src.highlighter import MarkdownHighlighter


class LineNumberArea(QWidget):
    """Line number gutter widget on the left side of the editor."""

    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)


class MarkdownEditor(QPlainTextEdit):
    """
    Enhanced plain text editor with Markdown formatting capabilities.
    """
    cursor_position_changed_info = pyqtSignal(int, int)  # line, col

    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent)
        self.dark_mode = dark_mode
        self.show_line_numbers = True

        # Set clean monospace coding font
        font = QFont("Cascadia Code", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)

        # Tab stop = 4 spaces
        font_metrics = self.fontMetrics()
        self.setTabStopDistance(4 * font_metrics.horizontalAdvance(' '))

        # Line number area
        self.line_number_area = LineNumberArea(self)

        # Syntax highlighter
        self.highlighter = MarkdownHighlighter(self.document(), dark_mode=self.dark_mode)

        # Signals
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.cursorPositionChanged.connect(self._emit_cursor_info)

        self.update_line_number_area_width(0)
        self.highlight_current_line()
        self._apply_theme()

    def set_dark_mode(self, dark_mode: bool):
        self.dark_mode = dark_mode
        self.highlighter.set_dark_mode(dark_mode)
        self._apply_theme()
        self.highlight_current_line()

    def _apply_theme(self):
        if self.dark_mode:
            bg_color = "#1e1e1e"
            text_color = "#d4d4d4"
            selection_bg = "#264f78"
            self.setStyleSheet(f"""
                QPlainTextEdit {{
                    background-color: {bg_color};
                    color: {text_color};
                    selection-background-color: {selection_bg};
                    border: none;
                }}
            """)
        else:
            bg_color = "#ffffff"
            text_color = "#1f2328"
            selection_bg = "#b4d5fe"
            self.setStyleSheet(f"""
                QPlainTextEdit {{
                    background-color: {bg_color};
                    color: {text_color};
                    selection-background-color: {selection_bg};
                    border: none;
                }}
            """)

    def _emit_cursor_info(self):
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.positionInBlock() + 1
        self.cursor_position_changed_info.emit(line, col)

    # --- Line Number Gutter Logic ---
    def line_number_area_width(self) -> int:
        if not self.show_line_numbers:
            return 0
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        space = 20 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        if not self.show_line_numbers:
            return

        painter = QPainter(self.line_number_area)
        gutter_bg = QColor("#252526" if self.dark_mode else "#f5f5f5")
        gutter_fg = QColor("#858585" if self.dark_mode else "#a0a0a0")
        current_fg = QColor("#ffffff" if self.dark_mode else "#000000")

        painter.fillRect(event.rect(), gutter_bg)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        current_block_num = self.textCursor().blockNumber()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                if block_number == current_block_num:
                    painter.setPen(current_fg)
                    f = painter.font()
                    f.setBold(True)
                    painter.setFont(f)
                else:
                    painter.setPen(gutter_fg)
                    f = painter.font()
                    f.setBold(False)
                    painter.setFont(f)

                painter.drawText(
                    0, top, self.line_number_area.width() - 8,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight, number
                )

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#282828" if self.dark_mode else "#f8f9fa")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    def set_line_numbers_visible(self, visible: bool):
        self.show_line_numbers = visible
        self.line_number_area.setVisible(visible)
        self.update_line_number_area_width(0)

    # --- Key Events & Smart Editing ---
    def keyPressEvent(self, event: QKeyEvent):
        cursor = self.textCursor()

        # Handle Enter for smart continuation of lists
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            line_text = cursor.block().text()
            stripped = line_text.strip()

            # Empty list item -> clear it on enter
            if stripped in ("-", "*", "+", "-", "- [ ]", "- [x]", "1."):
                cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                cursor.removeSelectedText()
                cursor.insertBlock()
                return

            # Check for list patterns
            indent = len(line_text) - len(line_text.lstrip())
            indent_str = " " * indent

            # Tasks
            if stripped.startswith("- [ ] ") or stripped.startswith("- [x] "):
                super().keyPressEvent(event)
                self.insertPlainText(f"{indent_str}- [ ] ")
                return

            # Bullet list
            if stripped.startswith(("- ", "* ", "+ ")):
                bullet = stripped[0]
                super().keyPressEvent(event)
                self.insertPlainText(f"{indent_str}{bullet} ")
                return

            # Numbered list
            import re
            m = re.match(r"^(\d+)\.\s", stripped)
            if m:
                num = int(m.group(1)) + 1
                super().keyPressEvent(event)
                self.insertPlainText(f"{indent_str}{num}. ")
                return

            # Blockquote
            if stripped.startswith("> "):
                super().keyPressEvent(event)
                self.insertPlainText(f"{indent_str}> ")
                return

            # Preserve generic indentation
            if indent > 0:
                super().keyPressEvent(event)
                self.insertPlainText(indent_str)
                return

        # Tab key: Insert 4 spaces or indent selected block
        if event.key() == Qt.Key.Key_Tab:
            if cursor.hasSelection():
                self._indent_selection(unindent=False)
            else:
                self.insertPlainText("    ")
            return

        # Shift+Tab: Unindent block
        if event.key() == Qt.Key.Key_Backtab:
            self._indent_selection(unindent=True)
            return

        super().keyPressEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        # Ctrl + Mouse Wheel Zoom
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoomIn(1)
            elif delta < 0:
                self.zoomOut(1)
            event.accept()
            return
        super().wheelEvent(event)

    def _indent_selection(self, unindent=False):
        cursor = self.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()

        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.beginEditBlock()

        while cursor.position() <= end:
            if unindent:
                block_text = cursor.block().text()
                if block_text.startswith("    "):
                    cursor.deleteChar()
                    cursor.deleteChar()
                    cursor.deleteChar()
                    cursor.deleteChar()
                elif block_text.startswith("\t"):
                    cursor.deleteChar()
            else:
                cursor.insertText("    ")

            if not cursor.movePosition(QTextCursor.MoveOperation.NextBlock):
                break

        cursor.endEditBlock()

    # --- Markdown Formatting Component Actions ---

    def wrap_selection(self, prefix: str, suffix: str, placeholder: str = ""):
        """Wraps selected text or inserts placeholder surrounded by prefix/suffix."""
        cursor = self.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText()
            cursor.insertText(f"{prefix}{selected}{suffix}")
        else:
            pos = cursor.position()
            cursor.insertText(f"{prefix}{placeholder}{suffix}")
            cursor.setPosition(pos + len(prefix))
            if placeholder:
                cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, len(placeholder))
            self.setTextCursor(cursor)

    def prefix_lines(self, prefix: str):
        """Prefixes each selected line or current line with the given prefix."""
        cursor = self.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()

        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.beginEditBlock()

        while True:
            cursor.insertText(prefix)
            if not cursor.movePosition(QTextCursor.MoveOperation.NextBlock) or cursor.position() > end + len(prefix):
                break

        cursor.endEditBlock()

    def apply_bold(self):
        self.wrap_selection("**", "**", "Fetter Text")

    def apply_italic(self):
        self.wrap_selection("*", "*", "Kursiver Text")

    def apply_strikethrough(self):
        self.wrap_selection("~~", "~~", "Durchgestrichen")

    def apply_heading(self, level: int = 1):
        """Applies #, ##, or ### to the beginning of the current block."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        line = cursor.block().text()

        # Remove existing heading hashes if present
        import re
        stripped = re.sub(r"^#{1,6}\s*", "", line)
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        hashes = "#" * level
        cursor.insertText(f"{hashes} {stripped}")

    def apply_bullet_list(self):
        self.prefix_lines("- ")

    def apply_numbered_list(self):
        cursor = self.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()

        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.beginEditBlock()

        num = 1
        while True:
            cursor.insertText(f"{num}. ")
            num += 1
            if not cursor.movePosition(QTextCursor.MoveOperation.NextBlock) or cursor.position() > end + (num * 3):
                break

        cursor.endEditBlock()

    def apply_task_list(self):
        self.prefix_lines("- [ ] ")

    def apply_quote(self):
        self.prefix_lines("> ")

    def apply_code_inline(self):
        self.wrap_selection("`", "`", "code")

    def apply_code_block(self, language: str = ""):
        cursor = self.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText().replace("\u2029", "\n")
            cursor.insertText(f"```{language}\n{selected}\n```\n")
        else:
            cursor.insertText(f"```{language}\n// Dein Code hier\n```\n")

    def insert_link(self, title: str = "Link-Text", url: str = "https://example.com"):
        cursor = self.textCursor()
        if cursor.hasSelection():
            title = cursor.selectedText()
        cursor.insertText(f"[{title}]({url})")

    def insert_image(self, alt: str = "Bildbeschreibung", url: str = "image.png"):
        cursor = self.textCursor()
        cursor.insertText(f"![{alt}]({url})")

    def insert_table(self, rows: int = 3, cols: int = 3):
        header_row = "| " + " | ".join([f"Spalte {i+1}" for i in range(cols)]) + " |\n"
        separator_row = "| " + " | ".join(["---" for _ in range(cols)]) + " |\n"
        data_rows = ""
        for r in range(rows - 1):
            data_rows += "| " + " | ".join([f"Wert {r+1}.{c+1}" for c in range(cols)]) + " |\n"

        table_md = "\n" + header_row + separator_row + data_rows + "\n"
        self.textCursor().insertText(table_md)

    def insert_horizontal_rule(self):
        self.textCursor().insertText("\n---\n\n")

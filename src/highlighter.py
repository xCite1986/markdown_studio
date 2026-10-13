"""
Markdown Syntax Highlighter for QPlainTextEdit.
Provides clean and readable syntax highlighting for Markdown text in both Light and Dark themes.
"""

import re
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression


class MarkdownHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter for Markdown documents.
    """

    def __init__(self, document, dark_mode=False):
        super().__init__(document)
        self.dark_mode = dark_mode
        self.highlighting_rules = []
        self._init_formats()
        self._build_rules()

    def set_dark_mode(self, dark_mode: bool):
        self.dark_mode = dark_mode
        self._init_formats()
        self._build_rules()
        self.rehighlight()

    def _init_formats(self):
        # Base colors depending on theme
        if self.dark_mode:
            h1_color = QColor("#58a6ff")
            h2_color = QColor("#79c0ff")
            h3_color = QColor("#a5d6ff")
            bold_color = QColor("#f0f6fc")
            italic_color = QColor("#d29922")
            strike_color = QColor("#8b949e")
            quote_color = QColor("#8b949e")
            list_color = QColor("#ff7b72")
            task_box_color = QColor("#7ee787")
            link_text_color = QColor("#58a6ff")
            link_url_color = QColor("#8b949e")
            code_inline_bg = QColor("#2d333b")
            code_inline_fg = QColor("#f0883e")
            code_block_fg = QColor("#79c0ff")
            code_block_bg = QColor("#1c2128")
            table_color = QColor("#79c0ff")
            hr_color = QColor("#484f58")
            tag_color = QColor("#7ee787")
        else:
            h1_color = QColor("#0969da")
            h2_color = QColor("#0550ae")
            h3_color = QColor("#0a3069")
            bold_color = QColor("#1f2328")
            italic_color = QColor("#9a6700")
            strike_color = QColor("#6e7781")
            quote_color = QColor("#57606a")
            list_color = QColor("#cf222e")
            task_box_color = QColor("#1a7f37")
            link_text_color = QColor("#0969da")
            link_url_color = QColor("#6e7781")
            code_inline_bg = QColor("#f6f8fa")
            code_inline_fg = QColor("#bc4c00")
            code_block_fg = QColor("#0550ae")
            code_block_bg = QColor("#f6f8fa")
            table_color = QColor("#1f2328")
            hr_color = QColor("#d0d7de")
            tag_color = QColor("#116329")

        # Headings
        self.h1_format = QTextCharFormat()
        self.h1_format.setFontWeight(QFont.Weight.Bold)
        self.h1_format.setForeground(h1_color)

        self.h2_format = QTextCharFormat()
        self.h2_format.setFontWeight(QFont.Weight.Bold)
        self.h2_format.setForeground(h2_color)

        self.h3_format = QTextCharFormat()
        self.h3_format.setFontWeight(QFont.Weight.Bold)
        self.h3_format.setForeground(h3_color)

        # Bold
        self.bold_format = QTextCharFormat()
        self.bold_format.setFontWeight(QFont.Weight.Bold)
        self.bold_format.setForeground(bold_color)

        # Italic
        self.italic_format = QTextCharFormat()
        self.italic_format.setFontItalic(True)
        self.italic_format.setForeground(italic_color)

        # Strikethrough
        self.strike_format = QTextCharFormat()
        self.strike_format.setFontStrikeOut(True)
        self.strike_format.setForeground(strike_color)

        # Quotes
        self.quote_format = QTextCharFormat()
        self.quote_format.setFontItalic(True)
        self.quote_format.setForeground(quote_color)

        # Lists
        self.list_format = QTextCharFormat()
        self.list_format.setFontWeight(QFont.Weight.Bold)
        self.list_format.setForeground(list_color)

        # Task Box
        self.task_format = QTextCharFormat()
        self.task_format.setFontWeight(QFont.Weight.Bold)
        self.task_format.setForeground(task_box_color)

        # Links
        self.link_text_format = QTextCharFormat()
        self.link_text_format.setFontUnderline(True)
        self.link_text_format.setForeground(link_text_color)

        self.link_url_format = QTextCharFormat()
        self.link_url_format.setForeground(link_url_color)

        # Inline Code
        self.code_inline_format = QTextCharFormat()
        self.code_inline_format.setForeground(code_inline_fg)
        self.code_inline_format.setBackground(code_inline_bg)

        # Code Block
        self.code_block_format = QTextCharFormat()
        self.code_block_format.setForeground(code_block_fg)
        self.code_block_format.setBackground(code_block_bg)

        # Table
        self.table_format = QTextCharFormat()
        self.table_format.setForeground(table_color)

        # Horizontal Rule
        self.hr_format = QTextCharFormat()
        self.hr_format.setForeground(hr_color)
        self.hr_format.setFontWeight(QFont.Weight.Bold)

        # HTML Tags
        self.tag_format = QTextCharFormat()
        self.tag_format.setForeground(tag_color)

    def _build_rules(self):
        self.highlighting_rules = [
            # Headings
            (QRegularExpression(r"^#\s[^\n]*"), self.h1_format),
            (QRegularExpression(r"^##\s[^\n]*"), self.h2_format),
            (QRegularExpression(r"^###\s[^\n]*"), self.h3_format),
            (QRegularExpression(r"^#{4,6}\s[^\n]*"), self.h3_format),

            # Bold
            (QRegularExpression(r"\*\*[^*\n]+\*\*"), self.bold_format),
            (QRegularExpression(r"__[^_\n]+__"), self.bold_format),

            # Italic
            (QRegularExpression(r"(?<!\*)\*[^*\n]+(?<!\*)\*"), self.italic_format),
            (QRegularExpression(r"(?<!_)_[^_\n]+(?<!_)_"), self.italic_format),

            # Strikethrough
            (QRegularExpression(r"~~[^~\n]+~~"), self.strike_format),

            # Quotes
            (QRegularExpression(r"^>\s?[^\n]*"), self.quote_format),

            # Task lists: - [ ] or - [x]
            (QRegularExpression(r"^\s*[-*+]\s+\[[ xX]\]"), self.task_format),

            # Bullet and Numbered lists
            (QRegularExpression(r"^\s*[-*+]\s+"), self.list_format),
            (QRegularExpression(r"^\s*\d+\.\s+"), self.list_format),

            # Horizontal Rule
            (QRegularExpression(r"^([-*_]\s*){3,}$"), self.hr_format),

            # Inline Code: `code`
            (QRegularExpression(r"`[^`\n]+`"), self.code_inline_format),

            # Links: [text](url)
            (QRegularExpression(r"!?\[[^\]]+\]"), self.link_text_format),
            (QRegularExpression(r"\([^)]+\)"), self.link_url_format),

            # Tables
            (QRegularExpression(r"^\|.*\|$"), self.table_format),

            # HTML Tags
            (QRegularExpression(r"</?[a-zA-Z0-9]+[^>]*>"), self.tag_format),
        ]

        # Multi-line Code Block regex
        self.code_block_start = QRegularExpression(r"^```")
        self.code_block_end = QRegularExpression(r"^```")

    def highlightBlock(self, text: str):
        # 1. Apply single line rules
        for pattern, fmt in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        # 2. Handle Multi-line Code Blocks (state = 1: inside code block, 0: normal)
        self.setCurrentBlockState(0)

        start_index = 0
        if self.previousBlockState() != 1:
            start_match = self.code_block_start.match(text)
            if start_match.hasMatch():
                start_index = start_match.capturedStart()
                self.setFormat(start_index, len(text) - start_index, self.code_block_format)
                self.setCurrentBlockState(1)
        else:
            # We are continuing inside a code block
            end_match = self.code_block_end.match(text)
            if end_match.hasMatch():
                # Ends on this block
                self.setFormat(0, len(text), self.code_block_format)
                self.setCurrentBlockState(0)
            else:
                self.setFormat(0, len(text), self.code_block_format)
                self.setCurrentBlockState(1)

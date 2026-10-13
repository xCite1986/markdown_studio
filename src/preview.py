"""
Live Markdown Preview Widget.
Renders Markdown to HTML using python-markdown and Pygments,
with professional GitHub-like styling for Light, Dark, and Print modes.
"""

import os
import re
import markdown
from PyQt6.QtWidgets import QTextBrowser
from PyQt6.QtGui import QDesktopServices, QWheelEvent
from PyQt6.QtCore import QUrl, Qt


LIGHT_CSS = """
body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #1f2328;
    background-color: #ffffff;
    margin: 16px 24px;
}
h1, h2, h3, h4, h5, h6 {
    color: #0969da;
    font-weight: 600;
    margin-top: 24px;
    margin-bottom: 12px;
}
h1 {
    font-size: 20pt;
    border-bottom: 2px solid #eaecef;
    padding-bottom: 8px;
}
h2 {
    font-size: 16pt;
    border-bottom: 1px solid #eaecef;
    padding-bottom: 6px;
}
h3 { font-size: 13pt; }
h4 { font-size: 11pt; }
p {
    margin-top: 0;
    margin-bottom: 12px;
}
a {
    color: #0969da;
    text-decoration: underline;
}
blockquote {
    border-left: 4px solid #0969da;
    background-color: #f6f8fa;
    padding: 8px 16px;
    margin: 12px 0;
    color: #57606a;
}
code {
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 10pt;
    background-color: #f2f4f7;
    color: #bc4c00;
    padding: 2px 5px;
    border-radius: 4px;
}
pre {
    background-color: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 12px;
    margin: 14px 0;
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 10pt;
    line-height: 1.45;
    overflow-x: auto;
}
pre code {
    background-color: transparent;
    color: #1f2328;
    padding: 0;
    border: none;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;
}
th, td {
    border: 1px solid #d0d7de;
    padding: 8px 14px;
    text-align: left;
}
th {
    background-color: #f6f8fa;
    font-weight: 600;
}
tr:nth-child(even) {
    background-color: #fbfcfd;
}
ul, ol {
    padding-left: 24px;
    margin-top: 0;
    margin-bottom: 12px;
}
li {
    margin-bottom: 4px;
}
hr {
    border: 0;
    height: 1px;
    background-color: #d0d7de;
    margin: 20px 0;
}
img {
    max-width: 100%;
    height: auto;
    border-radius: 4px;
    margin: 8px 0;
}
.task-item {
    font-family: 'Segoe UI Symbol', sans-serif;
    font-size: 1.15em;
    margin-right: 6px;
}
.task-checked {
    color: #1a7f37;
    font-weight: bold;
}
.task-unchecked {
    color: #6e7781;
}
"""

DARK_CSS = """
body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #e6edf3;
    background-color: #1e1e1e;
    margin: 16px 24px;
}
h1, h2, h3, h4, h5, h6 {
    color: #58a6ff;
    font-weight: 600;
    margin-top: 24px;
    margin-bottom: 12px;
}
h1 {
    font-size: 20pt;
    border-bottom: 2px solid #30363d;
    padding-bottom: 8px;
}
h2 {
    font-size: 16pt;
    border-bottom: 1px solid #30363d;
    padding-bottom: 6px;
}
h3 { font-size: 13pt; }
h4 { font-size: 11pt; }
p {
    margin-top: 0;
    margin-bottom: 12px;
}
a {
    color: #58a6ff;
    text-decoration: underline;
}
blockquote {
    border-left: 4px solid #388bfd;
    background-color: #161b22;
    padding: 8px 16px;
    margin: 12px 0;
    color: #8b949e;
}
code {
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 10pt;
    background-color: #2b3036;
    color: #f0883e;
    padding: 2px 5px;
    border-radius: 4px;
}
pre {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 12px;
    margin: 14px 0;
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 10pt;
    line-height: 1.45;
    overflow-x: auto;
}
pre code {
    background-color: transparent;
    color: #e6edf3;
    padding: 0;
    border: none;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;
}
th, td {
    border: 1px solid #30363d;
    padding: 8px 14px;
    text-align: left;
}
th {
    background-color: #21262d;
    font-weight: 600;
}
tr:nth-child(even) {
    background-color: #1c2128;
}
ul, ol {
    padding-left: 24px;
    margin-top: 0;
    margin-bottom: 12px;
}
li {
    margin-bottom: 4px;
}
hr {
    border: 0;
    height: 1px;
    background-color: #30363d;
    margin: 20px 0;
}
img {
    max-width: 100%;
    height: auto;
    border-radius: 4px;
    margin: 8px 0;
}
.task-item {
    font-family: 'Segoe UI Symbol', sans-serif;
    font-size: 1.15em;
    margin-right: 6px;
}
.task-checked {
    color: #7ee787;
    font-weight: bold;
}
.task-unchecked {
    color: #8b949e;
}
"""

PRINT_CSS = """
body {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.5;
    color: #000000;
    background-color: #ffffff;
    margin: 10mm;
}
h1, h2, h3, h4 {
    color: #113366;
    page-break-after: avoid;
}
h1 { font-size: 18pt; border-bottom: 1.5pt solid #333; padding-bottom: 4pt; }
h2 { font-size: 14pt; border-bottom: 1pt solid #666; padding-bottom: 3pt; }
h3 { font-size: 12pt; }
table {
    border-collapse: collapse;
    width: 100%;
    margin: 12pt 0;
    page-break-inside: avoid;
}
th, td {
    border: 1pt solid #444;
    padding: 5pt 8pt;
}
th { background-color: #eee; font-weight: bold; }
blockquote {
    border-left: 3pt solid #113366;
    padding-left: 8pt;
    margin: 8pt 0;
    color: #444;
}
pre {
    background-color: #f5f5f5;
    border: 1pt solid #ccc;
    padding: 6pt;
    font-family: 'Consolas', monospace;
    font-size: 9pt;
    page-break-inside: avoid;
}
code {
    font-family: 'Consolas', monospace;
    font-size: 9pt;
    background-color: #eee;
}
"""


class MarkdownPreview(QTextBrowser):
    """
    Renders Markdown documents to HTML with live styling and print optimization.
    """

    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent)
        self.dark_mode = dark_mode
        self.current_markdown = ""
        self.base_dir = ""

        self.setOpenExternalLinks(False)
        self.anchorClicked.connect(self._on_anchor_clicked)

        self._apply_widget_style()

    def set_dark_mode(self, dark_mode: bool):
        self.dark_mode = dark_mode
        self._apply_widget_style()
        self.render_markdown(self.current_markdown, self.base_dir)

    def _apply_widget_style(self):
        if self.dark_mode:
            self.setStyleSheet("""
                QTextBrowser {
                    background-color: #1e1e1e;
                    color: #e6edf3;
                    border: none;
                }
            """)
        else:
            self.setStyleSheet("""
                QTextBrowser {
                    background-color: #ffffff;
                    color: #1f2328;
                    border: none;
                }
            """)

    def _on_anchor_clicked(self, url: QUrl):
        # Open web links in default browser
        if url.scheme() in ("http", "https", "mailto"):
            QDesktopServices.openUrl(url)
        else:
            # Local file or relative anchor
            super().setSource(url)

    def _preprocess_markdown(self, text: str) -> str:
        """Preprocesses markdown for task lists, strikethrough, etc."""
        # Strikethrough ~~text~~ -> <del>text</del>
        text = re.sub(r"~~([^~\n]+)~~", r"<del>\1</del>", text)

        # Task list checked: - [x] or - [X]
        text = re.sub(
            r"^(\s*[-*+]\s+)\[[xX]\]\s+(.*)$",
            r'\1<span class="task-item task-checked">&#x2611;</span> \2',
            text,
            flags=re.MULTILINE
        )

        # Task list unchecked: - [ ]
        text = re.sub(
            r"^(\s*[-*+]\s+)\[\s\]\s+(.*)$",
            r'\1<span class="task-item task-unchecked">&#x2610;</span> \2',
            text,
            flags=re.MULTILINE
        )

        return text

    def render_markdown(self, md_text: str, base_dir: str = ""):
        """Converts Markdown to HTML and updates the browser content."""
        self.current_markdown = md_text
        self.base_dir = base_dir

        if base_dir and os.path.exists(base_dir):
            self.document().setBaseUrl(QUrl.fromLocalFile(os.path.abspath(base_dir) + "/"))
        else:
            self.document().setBaseUrl(QUrl())

        processed_md = self._preprocess_markdown(md_text)

        extensions = [
            'tables',
            'fenced_code',
            'toc',
            'nl2br',
            'sane_lists',
            'attr_list',
        ]

        try:
            html_body = markdown.markdown(processed_md, extensions=extensions)
        except Exception as e:
            html_body = f"<p style='color:red;'><b>Fehler beim Parsen von Markdown:</b> {e}</p>"

        css = DARK_CSS if self.dark_mode else LIGHT_CSS

        full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{css}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

        # Preserve scroll position if re-rendering
        scroll_bar = self.verticalScrollBar()
        current_scroll = scroll_bar.value()

        self.setHtml(full_html)
        scroll_bar.setValue(current_scroll)

    def get_printable_html(self, title: str = "") -> str:
        """Returns clean HTML formatted specifically for printers and PDF exports."""
        processed_md = self._preprocess_markdown(self.current_markdown)
        extensions = ['tables', 'fenced_code', 'toc', 'nl2br', 'sane_lists', 'attr_list']
        try:
            html_body = markdown.markdown(processed_md, extensions=extensions)
        except Exception:
            html_body = f"<pre>{self.current_markdown}</pre>"

        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
{PRINT_CSS}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

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

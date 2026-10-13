"""
Print and PDF Export Manager.
Provides native Windows print dialogs, interactive print preview,
and direct high-resolution PDF export for Markdown documents.
"""

import os
from PyQt6.QtWidgets import (
    QMessageBox, QFileDialog, QWidget
)
from PyQt6.QtPrintSupport import (
    QPrinter, QPrintDialog, QPrintPreviewDialog
)
from PyQt6.QtGui import QTextDocument, QDesktopServices, QPageLayout, QPageSize
from PyQt6.QtCore import QMarginsF, QUrl


class PrintManager:
    """
    Handles printing and PDF export operations.
    """

    @staticmethod
    def _create_print_document(preview_widget, title: str) -> QTextDocument:
        """Creates a dedicated QTextDocument formatted for paper printing."""
        doc = QTextDocument()
        if preview_widget.base_dir and os.path.exists(preview_widget.base_dir):
            doc.setBaseUrl(QUrl.fromLocalFile(os.path.abspath(preview_widget.base_dir) + "/"))

        printable_html = preview_widget.get_printable_html(title=title)
        doc.setHtml(printable_html)
        return doc

    @staticmethod
    def print_document(parent: QWidget, preview_widget, title: str = "Markdown-Dokument"):
        """Opens native Windows Print dialog and prints the rendered Markdown document."""
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setDocName(title)
        layout = printer.pageLayout()
        layout.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        layout.setMargins(QMarginsF(15, 15, 15, 15))
        printer.setPageLayout(layout)

        dialog = QPrintDialog(printer, parent)
        dialog.setWindowTitle("Dokument drucken")

        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            doc = PrintManager._create_print_document(preview_widget, title)
            doc.print(printer)
            QMessageBox.information(
                parent, "Drucken", "Der Druckauftrag wurde erfolgreich an den Drucker übergeben."
            )

    @staticmethod
    def print_preview(parent: QWidget, preview_widget, title: str = "Markdown-Dokument"):
        """Opens interactive Print Preview dialog with zoom and page layout controls."""
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setDocName(title)
        layout = printer.pageLayout()
        layout.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        layout.setMargins(QMarginsF(15, 15, 15, 15))
        printer.setPageLayout(layout)

        preview_dialog = QPrintPreviewDialog(printer, parent)
        preview_dialog.setWindowTitle(f"Druckvorschau - {title}")
        preview_dialog.resize(900, 750)

        doc = PrintManager._create_print_document(preview_widget, title)

        def handle_paint(target_printer):
            doc.print(target_printer)

        preview_dialog.paintRequested.connect(handle_paint)
        preview_dialog.exec()

    @staticmethod
    def export_pdf(parent: QWidget, preview_widget, default_filename: str = "Dokument.pdf", title: str = ""):
        """Exports the document directly to a clean PDF file."""
        if not default_filename.lower().endswith(".pdf"):
            default_filename += ".pdf"

        file_path, _ = QFileDialog.getSaveFileName(
            parent,
            "Als PDF exportieren",
            default_filename,
            "PDF-Dateien (*.pdf);;Alle Dateien (*.*)"
        )

        if not file_path:
            return

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(file_path)

        layout = printer.pageLayout()
        layout.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        layout.setMargins(QMarginsF(15, 15, 15, 15))
        printer.setPageLayout(layout)

        doc = PrintManager._create_print_document(preview_widget, title or os.path.basename(file_path))
        doc.print(printer)

        reply = QMessageBox.question(
            parent,
            "PDF erfolgreich exportiert",
            f"Die Datei wurde gespeichert unter:\n{file_path}\n\nMöchten Sie die PDF-Datei jetzt öffnen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

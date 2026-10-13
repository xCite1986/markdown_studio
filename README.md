# Markdown Studio

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6.svg)](https://microsoft.com/windows)
[![Release: v1.1.0](https://img.shields.io/badge/Release-v1.1.0-brightgreen.svg)](https://github.com)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Framework: PyQt6](https://img.shields.io/badge/Framework-PyQt6-success.svg)](https://riverbankcomputing.com/software/pyqt/)

Ein moderner, schneller und intuitiver **Markdown Viewer und WYSIWYG-Editor** für Windows.

<img width="1437" height="900" alt="image" src="https://github.com/user-attachments/assets/614628aa-dc49-42b8-a578-ccfca0954a06" />


---

## 🚀 Features

- **Bearbeitung im Vorschaumodus (WYSIWYG-Markdown):**
  - Schreiben und formatieren Sie direkt im gestalteten Vorschaumodus mit echter Typografie.
  - Änderungen werden live mit dem darunterliegenden Markdown synchronisiert.
- **Ausklappbare Code-Ansicht (rechts):**
  - Über die Schaltfläche **`💻 Code-Ansicht`** in der Steuerelementleiste (oder Tastenkürzel **`F12`**) kann der Markdown-Quellcode auf der rechten Seite ein- und ausgeklappt werden.
  - Vollständige **Zwei-Wege-Synchronisation**: Änderungen im Quellcode werden sofort in der Vorschau sichtbar und umgekehrt.
- **Aufgeräumte Steuerelementleiste mit Standardformatierungen:**
  - **Text:** Fett (`Strg+B`), Kursiv (`Strg+I`), Durchgestrichen
  - **Überschriften:** H1 (`Strg+1`), H2 (`Strg+2`), H3 (`Strg+3`)
  - **Listen & Aufgaben:** Aufzählungslisten, nummerierte Listen, interaktive Checklisten (`- [ ]`, `- [x]`, `Strg+Umschalt+C`)
  - **Zitate & Code:** Blockquotes, Inline-Code (`` ` ``) und Code-Blöcke (```` ``` ````)
  - **Elemente:** Hyperlinks (`Strg+K`), Bilder mit Dateiauswahl-Dialog, frei konfigurierbare Tabellen, horizontale Trennlinien
  - **Suchen & Ersetzen:** Vollwertige Leiste (`Strg+F`) mit Vor/Zurück, Groß-/Kleinschreibung und Ersetzen.
- **Drucken & Speichern direkt in der Steuerelementleiste:**
  - 🖨️ **Drucken (`Strg+P`):** Drucken des formatierten Dokuments über den nativen Windows-Druckdialog.
  - 🔍 **Druckvorschau (`Strg+Shift+P`):** Mehrseitige interaktive Druckvorschau mit Zoom und Randeinstellungen.
  - 📑 **Als PDF exportieren:** Hochauflösender PDF-Export mit professioneller Seitengestaltung.
  - 💾 **Schnellspeichern (`Strg+S`) & Speichern unter... (`Strg+Shift+S`)**
- **Windows OS-Integration & Setup:**
  - **Admin- oder Benutzer-Installation:** Der Installer fragt automatisch ab, ob die Installation für alle Benutzer (Admin) oder nur für den aktuellen Benutzer (ohne Admin-Rechte) erfolgen soll.
  - **Automatische Dateiverknüpfung:** Verknüpft `.md` und `.markdown` Dateien systemweit.
  - **In-App Verknüpfungs-Manager:** Über das Menü *Extras ➔ Windows .md-Dateiverknüpfung verwalten...* kann die Verknüpfung jederzeit per Klick aktiviert oder deaktiviert werden.
  - **Portable Version:** Als ZIP ohne Installation auf jedem Windows-PC sofort lauffähig.

---

## 📦 Download & Installation (Version 1.1.0)

### Option 1: Setup-Installer (Empfohlen)
Laden Sie `MarkdownStudio-1.1.0-Setup.exe` herunter und starten Sie die Datei:
- **Für aktuellen Benutzer (ohne Admin-Rechte):** Installiert nach `%LocalAppData%\Programs\MarkdownStudio`.
- **Für alle Benutzer (Admin):** Installiert nach `C:\Program Files\MarkdownStudio`.
- Aktivieren Sie im Setup die Option **„Markdown-Dateien (.md, .markdown) verknüpfen“**, um Dateien automatisch per Doppelklick in Windows zu öffnen.

### Option 2: Portable Version
1. Entpacken Sie `MarkdownStudio-1.1.0-Portable.zip` in ein beliebiges Verzeichnis oder auf einen USB-Stick.
2. Starten Sie `MarkdownStudio.exe`.
3. *(Optional)* Verknüpfen Sie `.md`-Dateien über die Menüleiste unter **Extras ➔ Windows .md-Dateiverknüpfung verwalten...**.

---

## 🛠️ Entwicklung & Build

### Voraussetzungen
- Python 3.10+
- Windows 10 / 11

### Abhängigkeiten installieren
```bash
pip install PyQt6 markdown pygments
```

### Anwendung starten
```bash
python src/main.py [optional_datei.md]
```

### Release-Build erstellen (Executable, Portable ZIP & Setup.exe)
```bash
python build_release.py
```
Die fertigen Binärdateien befinden sich anschließend im Verzeichnis `dist/`.

---

## ⌨️ Tastatur-Kurzbefehle

| Aktion | Tastenkürzel |
| :--- | :--- |
| Neue Datei | `Strg + N` |
| Datei öffnen | `Strg + O` |
| Speichern | `Strg + S` |
| Speichern unter... | `Strg + Umschalt + S` |
| Drucken | `Strg + P` |
| Druckvorschau | `Strg + Umschalt + P` |
| Code-Ansicht ein-/ausblenden | `F12` |
| Suchen & Ersetzen | `Strg + F` |
| Fett formatieren | `Strg + B` |
| Kursiv formatieren | `Strg + I` |
| Link einfügen | `Strg + K` |
| Checkliste einfügen | `Strg + Umschalt + C` |
| Überschrift 1 / 2 / 3 | `Strg + 1` / `Strg + 2` / `Strg + 3` |

---

## 📄 Lizenz

Dieses Projekt ist unter der **[MIT-Lizenz](LICENSE)** lizenziert. Siehe die Datei `LICENSE` für Details.

# Markdown Studio

Ein moderner, schneller und eleganter **Markdown Viewer und Editor** für Windows.

---

## 🚀 Features

- **Bearbeitung im Vorschaumodus (WYSIWYG-Markdown):**
  - Schreiben und formatieren Sie direkt im gestalteten Vorschaumodus mit echter Typografie.
  - Änderungen werden live mit dem darunterliegenden Markdown synchronisiert.
- **Ausklappbare Code-Ansicht (rechts):**
  - Über die Schaltfläche **💻 Code-Ansicht** in der Steuerelementleiste (oder `F12`) kann der Markdown-Quellcode auf der rechten Seite ein- und ausgeklappt werden.
  - Vollständige Zwei-Wege-Synchronisation: Änderungen im Quellcode werden sofort in der Vorschau sichtbar und umgekehrt.
- **Aufgeräumte Steuerelementleiste mit Standardformatierungen:**
  - **Text:** Fett (`Strg+B`), Kursiv (`Strg+I`), Durchgestrichen
  - **Überschriften:** H1 (`Strg+1`), H2 (`Strg+2`), H3 (`Strg+3`)
  - **Listen & Aufgaben:** Aufzählungslisten, nummerierte Listen, interaktive Checklisten (`- [ ]`, `- [x]`)
  - **Zitate & Code:** Blockquotes, Inline-Code (`` ` ``) und Code-Blöcke (```` ``` ````)
  - **Elemente:** Links (`Strg+K`), Bilder mit Dateiauswahl-Dialog, konfigurierbare Tabellen, horizontale Trennlinien
  - **Suchen & Ersetzen:** Vollwertige Leiste (`Strg+F`) mit Vor/Zurück, Groß-/Kleinschreibung und Ersetzen.
  - *Hinweis:* Systemeinstellungen wie Dunkelmodus und Dateiverknüpfung sind sauber in den Menüs *Ansicht* und *Extras* untergebracht.
- **Drucken & Speichern direkt in der Steuerelementleiste:**
  - 🖨️ **Drucken (`Strg+P`):** Drucken des gerenderten Dokuments über den nativen Windows-Druckdialog.
  - 🔍 **Druckvorschau (`Strg+Shift+P`):** Mehrseitige interaktive Druckvorschau mit Zoom und Randeinstellungen.
  - 📑 **Als PDF exportieren:** Hochauflösender PDF-Export mit professioneller Seitengestaltung.
  - 💾 **Schnellspeichern (`Strg+S`) & Speichern unter... (`Strg+Shift+S`)**
- **Windows OS-Integration & Setup:**
  - **Admin- oder Benutzer-Installation:** Der Installer (`MarkdownStudio-1.0.0-Setup.exe`) fragt automatisch ab, ob die Installation für alle Benutzer (Admin) oder nur für den aktuellen Benutzer (ohne Admin-Rechte) erfolgen soll.
  - **Automatische Dateiverknüpfung:** Verknüpft `.md` und `.markdown` Dateien systemweit.
  - **In-App Verknüpfungs-Manager:** Über das Menü *Extras -> Windows .md-Dateiverknüpfung verwalten...* kann die Verknüpfung jederzeit per Klick aktiviert oder deaktiviert werden.
  - **Portable Version:** Als ZIP (`MarkdownStudio-1.0.0-Portable.zip`) ohne Installation auf jedem Windows-PC sofort lauffähig.

---

## 📦 Download & Installation

### Option 1: Setup-Installer (Empfohlen)
Laden Sie `MarkdownStudio-1.0.0-Setup.exe` herunter und starten Sie die Datei:
- **Für aktuellen Benutzer (ohne Admin-Rechte):** Installiert nach `%LocalAppData%\Programs\MarkdownStudio`.
- **Für alle Benutzer (Admin):** Installiert nach `C:\Program Files\MarkdownStudio`.
- Aktivieren Sie im Setup die Option **„Markdown-Dateien (.md, .markdown) verknüpfen“**, um die Dateien automatisch im Explorer mit Markdown Studio zu öffnen.

### Option 2: Portable Version
1. Entpacken Sie `MarkdownStudio-1.0.0-Portable.zip` in ein beliebiges Verzeichnis oder auf einen USB-Stick.
2. Starten Sie `MarkdownStudio.exe`.
3. *(Optional)* Verknüpfen Sie `.md`-Dateien über die Schaltfläche **„Dateiverknüpfung verwalten“** in der Menüleiste.

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
Die fertigen Binärdateien befinden sich anschließend im Ordner `dist/`.

---

## ⌨️ Tastatur-Kurzbefehle

| Aktion | Tastenkürzel |
| :--- | :--- |
| Neue Datei | `Strg + N` |
| Datei öffnen | `Strg + O` |
| Speichern | `Strg + S` |
| Speichern unter | `Strg + Umschalt + S` |
| Drucken | `Strg + P` |
| Druckvorschau | `Strg + Umschalt + P` |
| Suchen & Ersetzen | `Strg + F` |
| Fett formatieren | `Strg + B` |
| Kursiv formatieren | `Strg + I` |
| Link einfügen | `Strg + K` |
| Checkliste einfügen | `Strg + Umschalt + C` |
| Überschrift 1 / 2 / 3 | `Strg + 1` / `Strg + 2` / `Strg + 3` |

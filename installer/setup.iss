; Inno Setup Script for Markdown Studio
; Supports both Administrative (All Users) and Non-Administrative (Current User) installations
; Configures automatic OS-wide file associations for .md and .markdown

#define MyAppName "Markdown Studio"
#define MyAppVersion "1.1.0"
#define MyAppPublisher "Markdown Studio"
#define MyAppExeName "MarkdownStudio.exe"
#define MyAppAssocName "Markdown-Dokument"
#define MyAppAssocExt ".md"
#define MyAppAssocKey "MarkdownStudio.Document"

#ifndef AppSourceDir
#define AppSourceDir "..\dist\MarkdownStudio"
#endif

[Setup]
AppId={{E68F5B71-9B5A-4B02-8DF6-48BD9D37283B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\MarkdownStudio
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Setup will ask the user if they want to install for All Users (Admin) or Current User
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\dist
OutputBaseFilename=MarkdownStudio-1.1.0-Setup
SetupIconFile=..\assets\app_icon.ico
SolidCompression=yes
Compression=lzma2/ultra64
ChangesAssociations=yes
DisableProgramGroupPage=auto

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "associate"; Description: "Markdown-Dateien (.md, .markdown) automatisch mit Markdown Studio verknüpfen"; GroupDescription: "Dateiverknüpfungen:"; Flags: checkedonce

[Files]
Source: "{#AppSourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\assets\app_icon.ico"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\app_icon.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\app_icon.ico"; Tasks: desktopicon

[Registry]
; File associations - Root: HKA targets HKLM in admin install and HKCU in user install
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocKey}"; Flags: uninsdeletevalue; Tasks: associate
Root: HKA; Subkey: "Software\Classes\.markdown"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocKey}"; Flags: uninsdeletevalue; Tasks: associate
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey; Tasks: associate
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"; Tasks: associate
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: associate
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\edit\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: associate

; Context Menu entry: "Mit Markdown Studio öffnen"
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.md\shell\OpenWithMarkdownStudio"; ValueType: string; ValueName: ""; ValueData: "Mit Markdown Studio öffnen"; Tasks: associate
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.md\shell\OpenWithMarkdownStudio"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\{#MyAppExeName}"""; Tasks: associate
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\.md\shell\OpenWithMarkdownStudio\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: associate

; Application Capabilities for Windows Settings "Default Apps"
Root: HKA; Subkey: "Software\{#MyAppName}\Capabilities"; ValueType: string; ValueName: "ApplicationDescription"; ValueData: "Markdown Studio Viewer und Editor"; Tasks: associate
Root: HKA; Subkey: "Software\{#MyAppName}\Capabilities"; ValueType: string; ValueName: "ApplicationName"; ValueData: "{#MyAppName}"; Tasks: associate
Root: HKA; Subkey: "Software\{#MyAppName}\Capabilities\FileAssociations"; ValueType: string; ValueName: ".md"; ValueData: "{#MyAppAssocKey}"; Tasks: associate
Root: HKA; Subkey: "Software\{#MyAppName}\Capabilities\FileAssociations"; ValueType: string; ValueName: ".markdown"; ValueData: "{#MyAppAssocKey}"; Tasks: associate
Root: HKA; Subkey: "Software\RegisteredApplications"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: "Software\{#MyAppName}\Capabilities"; Tasks: associate

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

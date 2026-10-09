#define MyAppName "YOLO训练引导工具"
#define MyAppVersion "1.0"
#define MyAppExeName "YOLO训练引导工具.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
VersionInfoVersion=1.0.0
AppPublisher=Kebeny
AppPublisherURL=https://github.com/Kebeny/Suitable-for-complete-beginners-in-YOLO
AppSupportURL=https://github.com/Kebeny/Suitable-for-complete-beginners-in-YOLO/issues
UninstallDisplayIcon={app}\{#MyAppExeName}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=.
OutputBaseFilename=YOLO训练引导工具_Setup
Compression=lzma2/fast
SolidCompression=yes
WizardStyle=modern
SetupIconFile=app.ico
DisableWelcomePage=no
DisableDirPage=no
DisableProgramGroupPage=no

[Languages]
Name: "chinesesimp"; MessagesFile: "installer\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加图标:"; Flags: checkablealone checkedonce

[Files]
Source: "dist\YOLO训练引导工具\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "启动 {#MyAppName}"; Flags: nowait postinstall skipifsilent unchecked

[Dirs]
Name: "{app}\datasets"
Name: "{app}\runs\train"
Name: "{app}\runs\predict"

[UninstallDelete]
Type: dirifempty; Name: "{app}\datasets"
Type: dirifempty; Name: "{app}\runs\train"
Type: dirifempty; Name: "{app}\runs\predict"
Type: dirifempty; Name: "{app}\runs"

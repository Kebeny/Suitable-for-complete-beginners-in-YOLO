; Inno Setup 简体中文语言文件
; 项目：YOLO 训练引导工具
;
; 重要：覆盖 Inno Setup 内建消息必须放在 [Messages] 段。
; [CustomMessages] 是给 {cm:Name} 自定义消息用的，放这里的条目不会生效。
; 本文件未定义的条目会自动回退到 Default.isl（英文）。

[LangOptions]
LanguageName=简体中文
LanguageID=$0804
LanguageCodePage=936
DialogFontName=Microsoft YaHei
DialogFontSize=9
WelcomeFontName=Microsoft YaHei
WelcomeFontSize=11
TitleFontName=Microsoft YaHei
TitleFontSize=14
CopyrightFontName=Microsoft YaHei
CopyrightFontSize=9
RightToLeft=no

[Messages]
; ---------- 标题与通用 ----------
SetupAppTitle=安装
SetupWindowTitle=安装 - %1
UninstallAppTitle=卸载
UninstallAppFullTitle=卸载 %1
InformationTitle=信息
ConfirmTitle=确认
ErrorTitle=错误
ExitSetupTitle=退出安装
ExitSetupMessage=安装尚未完成。如果现在退出，程序将不会被安装。%n%n你可以稍后重新运行安装程序来完成安装。%n%n确定要退出吗？
SetupAlreadyRunning=安装程序已在运行中。
UninstallAppRunningError=卸载程序已在运行中。
SetupAppRunningError=检测到 %1 正在运行。%n%n请先关闭它，然后单击"确定"继续，或单击"取消"退出。
WindowsVersionNotSupported=此程序不支持你的 Windows 版本。
WinVersionTooLowError=此程序需要 Windows %1 或更高版本。
WinVersionTooHighError=此程序无法在 Windows %1 或更高版本上运行。

; ---------- 按钮 ----------
ButtonBack=上一步(&B)
ButtonNext=下一步(&N)
ButtonInstall=安装(&I)
ButtonOK=确定
ButtonCancel=取消
ButtonYes=是(&Y)
ButtonYesToAll=全是(&A)
ButtonNo=否(&N)
ButtonNoToAll=全否(&O)
ButtonFinish=完成(&F)
ButtonBrowse=浏览(&R)...
ButtonWizardBrowse=浏览(&B)...
ButtonNewFolder=新建文件夹(&M)

; ---------- 欢迎页 ----------
WelcomeLabel1=欢迎使用 %1 安装向导
WelcomeLabel2=安装程序将在你的电脑上安装 %1。%n%n建议在继续之前关闭其他应用程序。

; ---------- 许可协议 ----------
WizardLicense=许可协议
LicenseLabel=请阅读以下重要信息，然后再继续。
LicenseLabel3=请在继续之前阅读许可协议。安装本程序前必须接受协议条款。
LicenseAccepted=我接受协议(&A)
LicenseNotAccepted=我不接受协议(&D)

; ---------- 密码页 ----------
WizardPassword=密码
PasswordLabel1=本安装程序受密码保护。
PasswordLabel3=请输入密码后继续。密码区分大小写。
PasswordEditLabel=密码(&P):
IncorrectPassword=密码错误，请重试。

; ---------- 信息页 ----------
WizardInfoBefore=信息
WizardInfoAfter=信息

; ---------- 安装目录 ----------
WizardSelectDir=选择目标位置
SelectDirDesc=选择目标位置
SelectDirLabel3=安装程序将把 %1 安装到下列文件夹。
SelectDirBrowseLabel=单击"下一步"继续。如需选择其他文件夹，请单击"浏览"。
DiskSpaceMBLabel=至少需要 [mb] MB 的可用磁盘空间。

; ---------- 组件 / 开始菜单 / 附加任务 ----------
WizardSelectComponents=选择组件
SelectComponentsDesc=选择组件
WizardSelectProgramGroup=选择开始菜单文件夹
SelectStartMenuFolderDesc=选择开始菜单文件夹
NoProgramGroupCheck2=不创建开始菜单文件夹(&N)
WizardSelectTasks=选择附加任务
SelectTasksDesc=选择附加任务
FullInstallation=完整安装
CustomInstallation=自定义安装

; ---------- 准备安装 ----------
WizardReady=准备安装
ReadyLabel1=安装程序现在已准备好在你的电脑上安装 %1。
ReadyLabel2a=单击"安装"开始安装，或单击"上一步"检查或修改设置。
ReadyMemoUserInfo=用户信息:
ReadyMemoDir=目标位置:
ReadyMemoType=安装类型:
ReadyMemoComponents=选定组件:
ReadyMemoGroup=开始菜单文件夹:
ReadyMemoTasks=附加任务:

; ---------- 安装过程 ----------
WizardPreparing=正在准备安装...
WizardInstalling=正在安装...
WizardUninstalling=正在卸载...
StatusCreateDirs=正在创建目录...
StatusExtractFiles=正在解压文件...
StatusCreateIcons=正在创建快捷方式...
StatusCreateIniEntries=正在创建配置文件...
StatusCreateRegistryEntries=正在创建注册表项...
StatusRegisterFiles=正在注册文件...
StatusSavingUninstall=正在创建卸载程序...
StatusRunProgram=正在完成安装...
StatusRollback=正在回滚更改...
StatusUninstalling=正在卸载...
BeveledLabel=
HelpTextNote=请选择安装选项，然后单击"下一步"继续。

; ---------- 完成页 ----------
FinishedLabel=安装程序已在你的电脑上完成 %1 的安装。%n%n单击"完成"退出安装程序。
FinishedLabelNoIcons=安装程序已在你的电脑上完成 %1 的安装。%n%n单击"完成"退出安装程序。
FinishedRestartLabel=要完成 %1 的安装，必须重新启动电脑。是否现在重新启动？
ClickFinish=安装完成。单击"完成"退出。
ClickNext=单击"下一步"继续。

; ---------- 卸载 ----------
ConfirmUninstall=确定要完全删除 %1 及其所有组件吗？%n%n注意：程序运行时生成的数据（datasets、runs 等）在卸载后仍会保留。
UninstalledAll=已完全卸载 %1。
UninstalledMost=已卸载 %1。%n%n部分组件无法自动删除，可手动删除。
NoUninstallWarning=安装程序已从你的电脑上删除以下组件:%n%n%1%n%n这些组件无法自动删除，可手动删除。
UninstallStatusLabel=正在从你的电脑上删除 %1，请稍候。

; ---------- 单选 ----------
YesRadio=是(&Y)
NoRadio=否(&N)

; ---------- 安装流程中其余可见消息 ----------
SetupLdrStartupMessage=即将安装 %1。是否继续？
SetupFileMissing=安装目录中缺少文件 %1。请修正此问题，或获取程序的新副本。
NotOnThisPlatform=此程序无法在 %1 上运行。
AboutSetupMenuItem=关于安装程序(&A)...
AboutSetupTitle=关于安装程序
AboutSetupMessage=%1 版本 %2%n%3%n%n%1 主页:%n%4
SelectLanguageTitle=选择安装语言
SelectLanguageLabel=请选择安装过程中使用的语言。
BrowseDialogTitle=浏览文件夹
BrowseDialogLabel=在下面的列表中选择一个文件夹，然后单击"确定"。
CannotInstallToNetworkDrive=安装程序无法安装到网络驱动器。
CannotInstallToUNCPath=安装程序无法安装到 UNC 路径。
DiskSpaceWarningTitle=磁盘空间不足
DiskSpaceWarning=安装至少需要 %1 KB 的可用空间，但所选驱动器仅有 %2 KB 可用。%n%n是否仍要继续？
BadDirName32=文件夹名称不能包含下列字符:%n%n%1
DirExistsTitle=文件夹已存在
DirExists=文件夹:%n%n%1%n%n已经存在。是否仍要安装到该文件夹？
DirDoesntExistTitle=文件夹不存在
DirDoesntExist=文件夹:%n%n%1%n%n不存在。是否创建该文件夹？
SelectComponentsLabel2=请选择要安装的组件；清除不需要安装的组件。准备好后单击"下一步"继续。
NoUninstallWarningTitle=组件仍然存在
SelectTasksLabel2=请选择安装 [name] 时要执行的附加任务，然后单击"下一步"。
SelectStartMenuFolderLabel3=安装程序将在下列开始菜单文件夹中创建程序的快捷方式。
SelectStartMenuFolderBrowseLabel=要继续，请单击"下一步"。如需选择其他文件夹，请单击"浏览"。
ReadyLabel2b=单击"安装"继续安装。
CannotContinue=安装程序无法继续。请单击"取消"退出。
CloseApplications=自动关闭这些应用程序(&A)
FinishedHeadingLabel=正在完成 [name] 安装向导
FinishedRestartMessage=要完成 [name] 的安装，安装程序必须重新启动你的电脑。%n%n是否现在重新启动？
ChangeDiskTitle=安装程序需要下一张磁盘
SelectDiskLabel2=请插入磁盘 %1 并单击"确定"。%n%n如果此磁盘上的文件位于下面显示的文件夹之外，请输入正确的路径或单击"浏览"。
SelectDirectoryLabel=请指定下一张磁盘的位置。
SetupAborted=安装未完成。%n%n请修正问题后重新运行安装程序。
StatusClosingApplications=正在关闭应用程序...
UninstalledAndNeedsRestart=要完成 %1 的卸载，必须重新启动电脑。%n%n是否现在重新启动？
ConfirmDeleteSharedFileTitle=删除共享文件？
; Example NSIS script for SoundSwitch and SoundSampleRecorder

!include "MUI2.nsh"

; General
Outfile "SoundSwitchInstaller.exe"
InstallDir $APPDATA\SoundSwitch

; Default section
Section

	; Set output path to the install directory
	SetOutPath $INSTDIR
	
	; Copy the executable and other files from dist for both SoundSwitch and SoundSampleRecorder
	File /r "dist\SoundSwitch\*.*"
	File "Icon.png"
	File "IconOn.png"
	File "config.ini"
	File /r "sound-samples"
	
	; Create a batch file to run the application as administrator
	StrCpy $1 'powershell -Command "Start-Process ''"$INSTDIR\SoundSwitch.exe"'' -Verb RunAs"$\r$\n'
	FileOpen $0 "$INSTDIR\RunAsAdmin.bat" "w"
	FileWrite $0 '@echo off$\r$\n'
	FileWrite $0 $1
	
	; Create shortcuts on the desktop
	CreateShortcut "$DESKTOP\SoundSwitch.lnk" "$INSTDIR\SoundSwitch.exe" 
	CreateShortcut "$DESKTOP\SoundSwitch-AsAdmin.lnk" "$INSTDIR\RunAsAdmin.bat" 
	CreateShortcut "$DESKTOP\SoundSampleRecorder.lnk" "$INSTDIR\SoundSampleRecorder.exe"

	CreateShortcut "$SMPROGRAMS\SoundSwitch.lnk" "$INSTDIR\SoundSwitch.exe"	 ; Modified to point to batch file
	CreateShortcut "$SMPROGRAMS\SoundSampleRecorder.lnk" "$INSTDIR\SoundSampleRecorder.exe"

	; Write uninstaller
	WriteUninstaller $INSTDIR\Uninstall.exe

SectionEnd

; Uninstaller section
Section "Uninstall"
	
	; Remove the installed files
	Delete $INSTDIR\SoundSwitch.exe
	Delete $INSTDIR\SoundSampleRecorder.exe
	Delete $INSTDIR\Icon.png
	Delete $INSTDIR\IconOn.png
	Delete $INSTDIR\config.ini
	RMDir /r $INSTDIR\sound-samples
	Delete $INSTDIR\config.ini
	Delete $INSTDIR\RunAsAdmin.bat	; Added this line to remove the batch file
	Delete $INSTDIR\Uninstall.exe
	
	; Remove the shortcuts
	Delete "$DESKTOP\SoundSwitch.lnk"
	Delete "$DESKTOP\SoundSwitch-AsAdmin.lnk"
	Delete "$SMPROGRAMS\SoundSwitch.lnk"
	Delete "$DESKTOP\SoundSampleRecorder.lnk"
	Delete "$SMPROGRAMS\SoundSampleRecorder.lnk"
	
	; Remove the install directory
	RMDir $INSTDIR
	
SectionEnd

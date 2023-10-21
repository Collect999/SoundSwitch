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
	; Write '@echo off' and a new line character to the file
	FileWrite $0 '@echo off$\r$\n'
	; Create the runas command string
	StrCpy $1 'runas /user:Administrator "$INSTDIR\SoundSwitch.exe"$\r$\n'
	; Write the runas command to the file
	FileWrite $0 $1
	; Close the file
	FileClose $0
	
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
	RMDir /r $INSTDIR\_internal
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

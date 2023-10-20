; Example NSIS script for SoundSwitch

!include "MUI2.nsh"

; General
Outfile "SoundSwitchInstaller.exe"
InstallDir $APPDATA\SoundSwitch

; Default section
Section

    ; Set output path to the install directory
    SetOutPath $INSTDIR
    
    # Copy the executable and other files from dist
    File /r "dist\SoundSwitch\*.*"
	File "Icon.png"    
	
    ; Create a shortcut on the desktop
    CreateShortcut "$DESKTOP\SoundSwitch.lnk" "$INSTDIR\SoundSwitch.exe"
    CreateShortcut "$SMPROGRAMS\SoundSwitch.lnk" "$INSTDIR\SoundSwitch.exe"

	; Write run as admin batch script
	; Create batch file for running the app as an admin
	FileOpen $0 "$INSTDIR\RunAsAdmin.bat" "w"
	FileWrite $0 '@echo off$\r$\n'
	FileWrite $0 'runas /user:Administrator "$INSTDIR\SoundSwitch.exe"$\r$\n'
	FileClose $0

	; Create a shortcut on the desktop to run as admin
	CreateShortcut "$DESKTOP\SoundSwitch (Run as Admin).lnk" "$INSTDIR\RunAsAdmin.bat"
    
    ; Write uninstaller
    WriteUninstaller $INSTDIR\Uninstall.exe

SectionEnd

; Uninstaller section
Section "Uninstall"
    
    ; Remove the installed files
    Delete $INSTDIR\SoundSwitch.exe
    RMDir /r $INSTDIR\sound-samples
    Delete $INSTDIR\config.ini
    Delete $INSTDIR\Uninstall.exe
    
    ; Remove the shortcut
    Delete "$DESKTOP\SoundSwitch.lnk"
    Delete "$SMPROGRAMS\SoundSwitch.lnk"
    Delete "$DESKTOP\SoundSwitch (Run as Admin).lnk"
    
    ; Remove the install directory
    RMDir $INSTDIR
    
SectionEnd

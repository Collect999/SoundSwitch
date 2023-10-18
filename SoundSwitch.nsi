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
    
    ; Create a shortcut on the desktop
    CreateShortcut "$DESKTOP\SoundSwitch.lnk" "$INSTDIR\SoundSwitch.exe"
    
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
    
    ; Remove the install directory
    RMDir $INSTDIR
    
SectionEnd

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
    
    ; Put your packaged EXE here
    File SoundSwitch.exe
    
    ; Create a directory for sound-samples
    CreateDirectory $INSTDIR\sound-samples
    
    ; Put sample audio files into the directory (assuming they are in a folder named 'sound-samples' in the same directory as this NSIS script)
    File /r sound-samples\*.*
    
    ; Write example config.ini
    File config.ini

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

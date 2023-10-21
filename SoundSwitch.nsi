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
    
    ; Create shortcuts on the desktop
    CreateShortcut "$DESKTOP\SoundSwitch.lnk" "$INSTDIR\SoundSwitch.exe"
    CreateShortcut "$DESKTOP\SoundSampleRecorder.lnk" "$INSTDIR\SoundSampleRecorder.exe"

    CreateShortcut "$SMPROGRAMS\SoundSwitch.lnk" "$INSTDIR\SoundSwitch.exe"
    CreateShortcut "$SMPROGRAMS\SoundSampleRecorder.lnk" "$INSTDIR\SoundSampleRecorder.exe"

    ; Write uninstaller
    WriteUninstaller $INSTDIR\Uninstall.exe

SectionEnd

; Uninstaller section
Section "Uninstall"
    
    ; Remove the installed files
    Delete $INSTDIR\SoundSwitch.exe
    Delete $INSTDIR\SoundSampleRecorder.exe
    RMDir /r $INSTDIR\sound-samples
    Delete $INSTDIR\config.ini
    Delete $INSTDIR\Uninstall.exe
    
    ; Remove the shortcuts
    Delete "$DESKTOP\SoundSwitch.lnk"
    Delete "$SMPROGRAMS\SoundSwitch.lnk"
    Delete "$DESKTOP\SoundSampleRecorder.lnk"
    Delete "$SMPROGRAMS\SoundSampleRecorder.lnk"
    
    ; Remove the install directory
    RMDir $INSTDIR
    
SectionEnd

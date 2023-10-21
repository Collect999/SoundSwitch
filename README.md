# Sound Switch 

![SoundSwitch Icon](./SoundSwitchImage.png)

This started out as a way of matching vocalisations in a really reliable way rather than just relying on amplitude 

We have a little app that listens to the mic and compares it to sound samples. So You need to get short, clean sound samples as wav files, put them in the sound-samples directory and run the system tray app.

It will then listen to the mic in the computer. 

You can have a look at some of the experiments that led to this in the directory. 

## Get up and running

1. You need to make sound samples of your vocalisations. Keep them short and as clean as possible using the same recording technique. Save them as wav's. You can use the 'SoundSampleRecoder' which is included if you wish - although you may need to trim the sound clips. 
2. [Download and install the app](https://github.com/AceCentre/SoundSwitch/releases/latest/download/SoundSwitchInstaller.exe)
3. Set the key stroke it is sending and other aspects in the config [See here](https://pyautogui.readthedocs.io/en/latest/keyboard.html#keyboard-keys)

Re: correlation_threshold

correlation_threshold is a critical parameter that determines the sensitivity of the audio detection algorithm. It sets the minimum value that the cross-correlation between the real-time audio and the audio samples must reach for a match to be considered valid.
A higher value makes the program less sensitive (fewer false positives), but it might miss some instances of the target sound. Conversely, a lower value makes the program more sensitive (more false positives) but increases the likelihood of detecting softer occurrences of the target sound. **It ranges from -1 0 1**. A typical value maybe 0.8

Re: Keys

It can be any of these characters in the config

-  \t
-  \r
-  !
-  "
-  $
-  %
-  &
-  ""
-  (
-  )
-  \*
-  \+
-  \-
-  .
-  /
-  0
-  1
-  2
-  3
-  4
-  5
-  6
-  7
-  8
-  9
-  :
-  ;
-  <
-  =
-  >
-  ?
-  @
-  [
-  \\
-  ]
-  ^
-  _
-  a
-  b
-  c
-  d
-  e
-  f
-  g
-  h
-  i
-  j
-  k
-  l
-  m
-  n
-  o
-  p
-  q
-  r
-  s
-  t
-  u
-  v
-  w
-  x
-  y
-  z
-  {
-  |
-  }
-  ~
-  accept
-  add
-  alt
-  altleft
-  altright
-  apps
-  backspace
-  browserback
-  browserfavorites
-  browserforward
-  browserhome
-  browserrefresh
-  browsersearch
-  browserstop
-  capslock
-  clear
-  convert
-  ctrl
-  ctrlleft
-  ctrlright
-  decimal
-  del
-  delete
-  divide
-  down
-  end
-  enter
-  esc
-  escape
-  execute
-  f1
-  f10
-  f11
-  f12
-  f13
-  f14
-  f15
-  f16
-  f17
-  f18
-  f19
-  f2
-  f20
-  f21
-  f22
-  f23
-  f24
-  f3
-  f4
-  f5
-  f6
-  f7
-  f8
-  f9
-  final
-  fn
-  hanguel
-  hangul
-  hanja
-  help
-  home
-  insert
-  junja
-  kana
-  kanji
-  launchapp1
-  launchapp2
-  launchmail
-  launchmediaselect
-  left
-  modechange
-  multiply
-  nexttrack
-  nonconvert
-  num0
-  num1
-  num2
-  num3
-  num4
-  num5
-  num6
-  num7
-  num8
-  num9
-  numlock
-  pagedown
-  pageup
-  pause
-  pgdn
-  pgup
-  playpause
-  prevtrack
-  print
-  printscreen
-  prntscrn
-  prtsc
-  prtscr
-  return
-  right
-  scrolllock
-  select
-  separator
-  shift
-  shiftleft
-  shiftright
-  sleep
-  space
-  stop
-  subtract
-  tab
-  up
-  volumedown
-  volumemute
-  volumeup
-  win
-  winleft
-  winright
-  yen
-  command
-  option
-  optionleft
-  optionright

## Code Structure


- load_samples(): Loads audio samples from a designated folder.
- findAudioDevices(): Lists available audio input devices.
- detect_ahh(): Performs cross-correlation to detect specific sounds.
- detection_loop(): Main loop where real-time audio is processed.




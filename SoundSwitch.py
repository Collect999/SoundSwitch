import pyaudio
import numpy as np
import librosa
import configparser
import os
import sys
import PySimpleGUI as sg
import threading
from scipy import signal
from scipy.signal import butter, filtfilt
import time
import pyautogui

# Determine application and config paths
if getattr(sys, 'frozen', False):
    home_directory = os.path.expanduser("~")
    application_path = os.path.join(home_directory, 'AppData', 'Roaming', 'SoundSwitch')
elif __file__:
    application_path = os.path.dirname(__file__)
config_path = os.path.join(application_path, 'settings.cfg')
sample_folder = os.path.join(application_path, 'sound-samples')

# Read config file
config = configparser.ConfigParser()
config.read('config.ini')
correlation_threshold = float(config['DEFAULT']['CorrelationThreshold'])
debug = bool(config.getboolean('DEFAULT', 'Debug'))
key_to_press = config['DEFAULT']['KeyToPress']
audioinput = int(config['DEFAULT']['AudioInput'])

# Load audio samples dynamically
ahh_templates = []
sample_files = [f for f in os.listdir(sample_folder) if f.endswith('.wav')]
for f in sample_files:
    audio, sr = librosa.load(os.path.join(sample_folder, f), sr=44100)
    ahh_templates.append(audio)

# Helper function to find the audio devices. 
def findAudioDevices():
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    device_info = ""
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            device_info += f"Input Device ID {i} - {p.get_device_info_by_host_api_device_index(0, i).get('name')}\n"
    sg.popup('Audio Devices', device_info)

# Function to perform cross-correlation
def detect_ahh(audio_signal, templates, threshold):
    max_correlations = []
    for template in templates:
        c = np.correlate(audio_signal, template, mode='valid')
        max_correlations.append(np.max(c))
    max_correlation = np.max(max_correlations)
    return max_correlation > threshold

# The function running the detection loop
def detection_loop(window):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=sr,
                    input=True,
                    input_device_index=audioinput,
                    frames_per_buffer=2048)
    last_triggered_time = 0  # Initialize to zero for first loop
    cooldown_time = 2.0  # Cooldown time in seconds

    while True:
        block = stream.read(2048, exception_on_overflow=False)
        audio_signal = np.frombuffer(block, dtype=np.float32)
        current_time = time.time()
        max_correlation_value = detect_ahh(audio_signal, ahh_templates, correlation_threshold)
        if debug:
            print(f"Max Correlation Value: {max_correlation_value}, Timestamp: {current_time}")
        if max_correlation_value > correlation_threshold:
            if current_time - last_triggered_time > cooldown_time:
                if debug:
                    print("Ahh sound detected!")
                pyautogui.press(key_to_press) 
                last_triggered_time = current_time
                # Here you can send a message to your GUI or trigger other actions

# PySimpleGUI setup
menu_def = ['File', ['Show Audio Devices', 'Open Config', 'Exit']]

# Initialize the tray
tray = sg.SystemTray(menu=menu_def, filename='SoundSwitchIcon.ico')
#tray = sg.SystemTray(menu=menu_def)

# Start detection loop in a separate thread
t = threading.Thread(target=detection_loop, args=(tray,))
t.start()

# Event loop
while True:
    menu_item = tray.read()
    if menu_item == 'Exit':
        break
    elif menu_item == 'Show Audio Devices':
        findAudioDevices()  # This function should probably be modified to display a popup instead of printing to console
    elif menu_item == 'Open Config':
        os.system(f"notepad {config_path}")

tray.close()

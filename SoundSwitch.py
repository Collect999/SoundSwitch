import pyaudio
import numpy as np
import librosa
import configparser
import os
from scipy import signal
from scipy.signal import butter, filtfilt
import time
import pyautogui

# Read config file
config = configparser.ConfigParser()
config.read('config.ini')
correlation_threshold = float(config['DEFAULT']['CorrelationThreshold'])
debug = config.getboolean('DEFAULT', 'Debug')

# Load audio samples dynamically
sample_folder = "path/to/your/folder/with/audio/samples"  # Replace with your folder path
ahh_templates = []
sample_files = [f for f in os.listdir(sample_folder) if f.endswith('.wav')]
for f in sample_files:
    audio, sr = librosa.load(os.path.join(sample_folder, f), sr=44100)
    ahh_templates.append(audio)

# Initialize PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=sr,
                input=True,
                input_device_index=1,
                frames_per_buffer=2048)

# Function to perform cross-correlation
def detect_ahh(audio_signal, templates, threshold):
    max_correlations = []
    for template in templates:
        c = np.correlate(audio_signal, template, mode='valid')
        max_correlations.append(np.max(c))
    max_correlation = np.max(max_correlations)
    return max_correlation > threshold

# Continuously read audio from the microphone and detect sounds
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
            last_triggered_time = current_time
            # Trigger key press here

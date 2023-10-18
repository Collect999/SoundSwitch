import pyaudio
import numpy as np
import librosa
from scipy import signal
from scipy.signal import butter, filtfilt
import time
import pyautogui


# find audio devices
def findAudioDevices():
	p = pyaudio.PyAudio()
	info = p.get_host_api_info_by_index(0)
	numdevices = info.get('deviceCount')
	for i in range(0, numdevices):
		if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
			print("Input Device ID ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

findAudioDevices()

# Simple high-pass filter

def butter_highpass(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

# Load the "ahhh" template
ahh_template, sr = librosa.load("heather.wav", sr=44100)
block_size = 2048
correlation_threshold = 0.8  # Set an arbitrary threshold 

# 1  Perfect positive correlation; the signals are identical.
# 0   No correlation; the signals are completely different.
# -1  Perfect negative correlation; one signal is an inverted version of the other.

# Initialize PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=sr,
                input=True,
                input_device_index=1,
                frames_per_buffer=block_size)

# Function to perform cross-correlation and check if "ahhh" sound is detected
def detect_ahh(audio_signal, template, threshold):
    c = signal.correlate(audio_signal, template, mode='valid', method='fft')
    peak = np.max(c)
    print("Max Correlation Value:", peak)  # <-- Debugging print statement
    return peak > threshold

# Continuously read audio from the microphone and detect sounds
last_triggered_time = 0.8  # The last time an "ahhh" was detected
cooldown_time = 2.0  # Cooldown time in seconds
# Continuously read audio from the microphone and detect sounds
while True:
    block = stream.read(block_size, exception_on_overflow=False)
    audio_signal = np.frombuffer(block, dtype=np.float32)

    # Apply the high-pass filter here
    filtered_signal = highpass_filter(audio_signal, cutoff=100.0, fs=sr)

    current_time = time.time()

    if detect_ahh(filtered_signal, ahh_template, correlation_threshold):
        if current_time - last_triggered_time > cooldown_time:
            print("Ahh sound detected!")
            last_triggered_time = current_time
            # Trigger key press here

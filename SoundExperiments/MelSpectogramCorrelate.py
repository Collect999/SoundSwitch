import pyaudio
import numpy as np
import librosa
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import time

# Load pre-recorded templates and compute their Mel spectrograms
audio1, sr = librosa.load("heather1.wav", sr=44100)
audio2, _ = librosa.load("heather2.wav", sr=44100)

S1 = librosa.feature.melspectrogram(y=audio1, sr=sr, n_mels=128)
S2 = librosa.feature.melspectrogram(y=audio2, sr=sr, n_mels=128)

templates = [S1, S2]

# Initialize PyAudio
block_size = 2048
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=sr,
                input=True,
                frames_per_buffer=block_size)

# Function to detect sound using Mel spectrogram and DTW
def detect_sound(audio_signal, templates, sr, threshold=1000):
    S = librosa.feature.melspectrogram(y=audio_signal, sr=sr, n_mels=128)
    min_distance = float('inf')

    for template in templates:
        distance, _ = fastdtw(S.T, template.T, dist=euclidean)
        min_distance = min(min_distance, distance)

    return min_distance < threshold

# Main loop
cooldown_time = 2.0
last_triggered_time = 0.0

while True:
    block = stream.read(block_size, exception_on_overflow=False)
    audio_signal = np.frombuffer(block, dtype=np.float32)
    current_time = time.time()

    if detect_sound(audio_signal, templates, sr):
        if current_time - last_triggered_time > cooldown_time:
            print("Sound detected!")
            last_triggered_time = current_time
            # Add your action here (e.g., key press)

import pyaudio
import numpy as np
import librosa

# Set the minimum and maximum frequencies of the "ahh" sound
ahh_fmin = 500
ahh_fmax = 1500

# Set the minimum and maximum frequencies of the "ssss" sound
ssss_fmin = 2000
ssss_fmax = 4000

# Set the threshold for detecting a sound
threshold = 0.5

# Set the sampling rate and block size for PyAudio
sr = 44100
block_size = 2048

# Initialize PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=sr,
                input=True,
                frames_per_buffer=block_size)

# Continuously read audio from the microphone and detect sounds
while True:
    # Read a block of audio from the microphone
    block = stream.read(block_size, exception_on_overflow=False)

    # Convert the block to a numpy array
    signal = np.frombuffer(block, dtype=np.float32)

    # Compute the mel spectrogram
    S = librosa.feature.melspectrogram(signal, sr=sr, n_mels=128)

    # Convert to decibels
    log_S = librosa.power_to_db(S, ref=np.max)

    # Find the peak frequency in each frame
    frequencies = librosa.core.time_frequency.mel_frequencies(n_mels=128, fmin=0, fmax=sr/2)
    peak_frequencies = frequencies[np.argmax(log_S, axis=0)]

    # Check if there is a peak frequency within the desired range for "ahh" sound
    if np.any((peak_frequencies >= ahh_fmin) & (peak_frequencies <= ahh_fmax)):
        print("Ahh sound detected!")
        # Simulate pressing F1 key
        # Use a library such as pyautogui to automate key presses
        # pyautogui.press('f1')

    # Check if there is a peak frequency within the desired range for "ssss" sound
    if np.any((peak_frequencies >= ssss_fmin) & (peak_frequencies <= ssss_fmax)):
        print("Ssss sound detected!")
        # Simulate pressing F2 key
        # Use a library such as pyautogui to automate key presses
        # pyautogui.press('f2')
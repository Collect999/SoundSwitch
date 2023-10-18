import numpy as np
import librosa
import sounddevice as sd

# define the number of samples per chunk
chunk_size = 1024

# define the sample rate and the number of audio channels
sample_rate = 44100
num_channels = 1

# define the minimum and maximum frequencies to detect
min_freq = 0
max_freq = 22050.0

# initialize the buffer to hold audio data
buffer = np.zeros(chunk_size * num_channels)

# function to process audio data
def process_audio(indata, frames, time, status):
    global buffer
    
    # append new audio data to the buffer
    buffer = np.concatenate((buffer, indata))
    
    # remove old audio data from the buffer
    buffer = buffer[-chunk_size * num_channels:]
    
    # compute the mel spectrogram
    S = librosa.feature.melspectrogram(buffer, sr=sample_rate, n_mels=128, fmin=min_freq, fmax=max_freq)
    
    # compute the logarithmic power spectrogram
    log_S = librosa.power_to_db(S, ref=np.max)
    
    # compute the mean of the spectrogram
    mean_S = np.mean(log_S)
    
    # check if the mean of the spectrogram exceeds a threshold
    if mean_S > -20:
        print('Ahh sound detected!')
    
# start the audio stream
with sd.InputStream(channels=num_channels, blocksize=chunk_size, samplerate=sample_rate, callback=process_audio):
    while True:
        pass

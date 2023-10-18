import scipy.io.wavfile as wavfile
import scipy.signal as signal

# Load the audio file
fs, data = wavfile.read('output.wav')

# Calculate the spectrogram
f, t, Sxx = signal.spectrogram(data, fs)

# Find the indices of the frequency bins that correspond to the minimum and maximum frequencies
min_idx = 0
max_idx = len(f) - 1

# Define the minimum and maximum frequencies before using them
min_freq = f[min_idx]
max_freq = f[max_idx]

for i in range(len(f)):
    if f[i] >= min_freq:
        min_idx = i
        break
for i in range(len(f)-1, -1, -1):
    if f[i] <= max_freq:
        max_idx = i
        break

print('Minimum frequency:', min_freq)
print('Maximum frequency:', max_freq)

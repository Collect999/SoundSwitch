# Details


- FindSound.py. The script is designed to read an audio file and calculate its spectrogram, which is a visual representation of the spectrum of frequencies in the audio signal as they vary with time. The script then identifies the minimum and maximum frequencies present in the audio file based on the calculated spectrogram.
- FindAudio2.py. The script is designed to find the temporal offset between two audio signals: a reference signal and a target signal. The reference signal is recorded via a microphone, while the target signal is loaded from an audio file. The program employs cross-correlation to identify the point in time where the two signals are most similar.
- MelSpectogramCorrelate.py. This is neat. It turns the waveform into a melspectogram then uses this to correlate against incoming sound
- StandardCorrelation.py. The script used in the main app. Its faster and less intensive than the melspectogram approach
- RealFind.py. The script is designed to continuously capture audio from a microphone and process it in real-time to detect specific sounds. It uses the Mel spectrogram to analyze the frequency content of the audio and identifies sounds based on a threshold applied to the mean of the logarithmic power spectrogram.
- SoundSwitch.py. uses the Mel spectrogram to analyze the frequency content of the audio and identifies these sounds based on their frequency ranges.


# The program is designed to find the temporal offset between two audio signals: a reference signal that is recorded via a microphone and a target signal that is loaded from an audio file. The program uses cross-correlation to find the point in time where the two signals are most similar.

import argparse
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import sounddevice as sd
import librosa
import soundfile as sf  # For saving debug audio files


def find_offset(within_signal, find_signal, sample_rate, window):
    c = signal.correlate(within_signal, find_signal[:int(sample_rate * window)], mode='valid', method='fft')
    peak = np.argmax(c)
    offset = round(peak / sample_rate, 2)

    fig, ax = plt.subplots()
    ax.plot(c)
    fig.savefig("cross-correlation.png")

    return offset


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--find-offset-of', metavar='audio file', type=str, help='Find the offset of file')
    parser.add_argument('--window', metavar='seconds', type=int, default=10, help='Only use first n seconds of a target audio')
    args = parser.parse_args()

    try:
        print("Available audio devices:")
        print(sd.query_devices())

        sample_rate = sd.default.samplerate if sd.default.samplerate is not None else 44100

        print(f"Using sample rate: {sample_rate}")

        print("Recording reference audio file...")
        within_signal = sd.rec(int(args.window * sample_rate), channels=1, blocking=True, device=2)
        sd.wait()

        # Save the recorded audio for debugging
        sf.write('debug_within_signal.wav', within_signal, sample_rate)

        print("Loading target audio file...")
        find_signal, _ = librosa.load(args.find_offset_of, sr=sample_rate)

        # Finding offset
        offset = find_offset(within_signal[:, 0], find_signal, sample_rate, args.window)
        print(f"Offset: {offset}s")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()

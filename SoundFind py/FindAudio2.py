import argparse
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import sounddevice as sd


def find_offset(within_signal, find_signal, sample_rate, window):
    c = signal.correlate(within_signal, find_signal[:int(sample_rate*window)], mode='valid', method='fft')
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

    # Capture audio from microphone as reference audio file
    print("Recording reference audio file...")
    within_signal, sample_rate = sd.rec(int(args.window * sd.default.samplerate), channels=1, blocking=True, device=2)
    sd.wait()

    # Load audio file to find offset
    print("Loading target audio file...")
    find_signal, _ = librosa.load(args.find_offset_of, sr=sample_rate)

    offset = find_offset(within_signal[:,0], find_signal, sample_rate, args.window)
    print(f"Offset: {offset}s" )


if __name__ == '__main__':
    main()

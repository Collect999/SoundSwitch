import time
import array
import math
import board
import digitalio
import audiobusio
from ulab import numpy as np

DEBUG = True

# BLE
import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
# BLE Setup


if DEBUG == False:
    hid = HIDService()
    device_info = DeviceInfoService(software_revision=adafruit_ble.__version__,
                                    manufacturer="AceCentre")
    advertisement = ProvideServicesAdvertisement(hid)
    advertisement.appearance = 961
    scan_response = Advertisement()
    scan_response.complete_name = "Sound Switch v1"

    ble = adafruit_ble.BLERadio()
    if not ble.connected:
        print("advertising")
        ble.start_advertising(advertisement, scan_response)
    else:
        print("already connected")
        print(ble.connections)

    k = Keyboard(hid.devices)
    kl = KeyboardLayoutUS(k)

# turn on the microphone
micpwr = digitalio.DigitalInOut(board.MIC_PWR)
micpwr.direction = digitalio.Direction.OUTPUT
micpwr.value = True
time.sleep(0.1)

mic = audiobusio.PDMIn(board.PDM_CLK,
                       board.PDM_DATA,
                       sample_rate=16000,
                       bit_depth=16
                       )

# NB: was 160
samples = array.array('H', [0] * 256)
# Define the number of frames to average
num_frames_to_average = 5
pitch_history = []
# Define the parameters for the low-pass filter
alpha = 0.1  # Smoothing factor
# Initialize the filtered pitch value
filtered_pitch = 0

# Define threshold parameters
magnitude_threshold = 150.0
lower_magnitude_threshold = 125
min_trigger_period = 0.2  # Minimum time to trigger (in seconds)
triggered = False
trigger_start_time = 0.0
# Define the parameters for the high-pass filter
cutoff_frequency = 250  # Hz

# Apply a simple high-pass filter to samples
def apply_high_pass_filter(samples):
    filtered_samples = [samples[0]]  # Initialize the first value
    alpha = 0.95  # Filter coefficient

    for i in range(1, len(samples)):
        filtered_sample = alpha * (filtered_samples[i - 1] + samples[i] - samples[i - 1])
        filtered_samples.append(filtered_sample)
    
    return filtered_samples

# Remove DC bias before computing RMS.
def mean(values):
    return sum(values) / len(values)

# Calculate the Normalized RMS value of samples
def normalized_rms(values):
    minbuf = int(mean(values))
    samples_sum = sum(
        float(sample - minbuf) * (sample - minbuf)
        for sample in values
    )
    return math.sqrt(samples_sum / len(values))


# Function to calculate the pitch using autocorrelation
def fft_pitch(samples, sample_rate):
    samples_ndarray = np.array(samples, dtype=np.float)
    freqs = np.fft.fft(samples_ndarray)
    freqs_real, freqs_imag = np.fft.fft(samples_ndarray)
    freqs_mag = np.sqrt(freqs_real ** 2 + freqs_imag ** 2)  # Calculate magnitude manually
    max_freq_index = np.argmax(freqs_mag[1:]) + 1  # Skip DC component
    max_freq = max_freq_index * (sample_rate / len(samples))
    return max_freq



# Function to calculate the pitch using autocorrelation
# Not as accurate as FFT
def autocorrelation_pitch(samples, sample_rate):
    autocorr = array.array('f', [0.0] * len(samples))
    for lag in range(1, len(samples)):
        for i in range(len(samples) - lag):
            autocorr[lag] += samples[i] * samples[i + lag]
    
    peak = autocorr.index(max(autocorr))
    period = peak / sample_rate
    frequency = 1 / period
    return frequency


while True:
    if DEBUG == False:
        while not ble.connected:
            pass
        print("Start typing:")

    #while ble.connected:
    print('hello')
    mic.record(samples, len(samples))
    # Apply high-pass filter to samples
    filtered_samples = apply_high_pass_filter(samples)

    # Calculate the magnitude (normalized RMS)
    magnitude = normalized_rms(filtered_samples)
    # Calculate the pitch (fundamental frequency)
    pitch = fft_pitch(filtered_samples, 16000)
    # Append the current pitch to the history
    pitch_history.append(pitch)
    # Keep the history size within the specified limit
    if len(pitch_history) > num_frames_to_average:
        pitch_history.pop(0)
    # Calculate the average pitch over the history
    average_pitch = sum(pitch_history) / len(pitch_history)
    # Apply the low-pass filter
    filtered_pitch = (1 - alpha) * filtered_pitch + alpha * pitch
    print("Magnitude:", magnitude)
    #print("Pitch:", pitch, "Hz")
    #print("Magnitude", magnitude, "Pitch", pitch, "Average Pitch", average_pitch, "Filtered pitch", filtered_pitch)
    # Check if the magnitude threshold is reached
    
     # Check if the magnitude threshold is reached
    if magnitude > magnitude_threshold and not triggered:
        trigger_start_time = time.monotonic()
        triggered = True
        print("Magnitude threshold reached. Triggered.")
        #k.send(Keycode.F1)
    # Check if the minimum trigger period has been met

    if triggered:
        current_time = time.monotonic()
        trigger_duration = current_time - trigger_start_time
        if trigger_duration >= min_trigger_period:
            triggered = False

    # Check if the magnitude drops below the lower threshold to reset the hysteresis
    if magnitude < lower_magnitude_threshold:
        triggered = False
    

    time.sleep(0.1)             
            
    #ble.start_advertising(advertisement)




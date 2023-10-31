import board
import audioio
import array
import time
import math

# Configure the PDM microphone
mic_pin = board.MICROPHONE_CLOCK
data_pin = board.MICROPHONE_DATA
mic = audioio.PDMIn(clock=mic_pin, data=data_pin, sample_rate=16000, bit_depth=16)

# Sound detection parameters
threshold = 3000  # Adjust this value based on your microphone sensitivity
min_sound_duration = 0.5  # Minimum duration of "ah" sound in seconds
last_triggered_time = 0

# Define the expected pattern for "ah" sound
pattern = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 0.8, 0.6, 0.4, 0.2, 0.0]

def calculate_correlation(signal, pattern):
    correlation = 0.0
    for i in range(len(signal)):
        correlation += signal[i] * pattern[i]
    return correlation

def detect_ah_sound():
    global last_triggered_time
    
    samples = array.array("H", [0] * len(pattern))
    mic.record(samples, len(samples))
    
    # Calculate the correlation between the captured signal and the pattern
    correlation = calculate_correlation(samples, pattern)
    
    # Check if the correlation is above the threshold
    if correlation > threshold:
        current_time = time.monotonic()
        # Check if the minimum sound duration has passed since the last trigger
        if current_time - last_triggered_time >= min_sound_duration:
            last_triggered_time = current_time
            return True
    
    return False

while True:
    if detect_ah_sound():
        print("Detected 'ah' sound")
    
    time.sleep(0.01)  # Add a small delay to avoid busy waiting

import time
import array
import math
import board
import digitalio
import audiobusio
from ulab import numpy as np


micpwr = digitalio.DigitalInOut(board.MIC_PWR)
micpwr.direction = digitalio.Direction.OUTPUT
micpwr.value = True
time.sleep(0.1)

mic = audiobusio.PDMIn(board.PDM_CLK,
                       board.PDM_DATA,
                       sample_rate=16000,
                       bit_depth=16
                       )

# Sound detection parameters
threshold = 3000  # Adjust this value based on your microphone sensitivity
min_sound_duration = 0.5  # Minimum duration of "ah" sound in seconds
last_triggered_time = 0

def detect_ah_sound():
    global last_triggered_time
    
    samples = array.array("H", [0] * 160)
    mic.record(samples, len(samples))
    
    # Check if the sound level is above the threshold
    if max(samples) > threshold:
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

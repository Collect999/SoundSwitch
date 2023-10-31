import board
import digitalio
import audioio
import time
import usb_hid
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

# Configure the PDM microphone
mic_pin = board.MICROPHONE_CLOCK
data_pin = board.MICROPHONE_DATA
mic = audioio.PDMIn(clock=mic_pin, data=data_pin, sample_rate=16000, bit_depth=16)

# Configure the button to start the sound detection
button_pin = board.BUTTON_A
button = digitalio.DigitalInOut(button_pin)
button.switch_to_input(pull=digitalio.Pull.DOWN)

# Initialize Bluetooth HID keyboard
kbd = Keyboard(usb_hid.devices)

# Initialize the keyboard layout
layout = KeyboardLayoutUS(kbd)

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
    if button.value:  # Wait for the button to be pressed
        while button.value:
            pass
        
        if detect_ah_sound():
            # Send "F1" key press via Bluetooth HID
            kbd.press(Keycode.F1)
            kbd.release_all()
            print("Detected 'ah' sound and sent F1 key press")
    
    time.sleep(0.01)  # Add a small delay to avoid busy waiting

import pyaudio
import numpy as np
import librosa
import configparser
import os
import sys
import PySimpleGUI as sg
from psgtray import SystemTray
import threading
from scipy import signal
from scipy.signal import butter, filtfilt
import time
import pyautogui
import argparse
import logging

# Enable logging if debug flag is set
# Initialize the argparse
logging.basicConfig(filename='app.log', level=logging.DEBUG)
ahh_templates = []

# Determine application and config paths
if getattr(sys, 'frozen', False):
	home_directory = os.path.expanduser("~")
	application_path = os.path.join(home_directory, 'AppData', 'Roaming', 'SoundSwitch')
elif __file__:
	application_path = os.path.dirname(__file__)
config_path = os.path.join(application_path, 'config.ini')
sample_folder = os.path.join(application_path, 'sound-samples')

# Read config file
config = configparser.ConfigParser()
config.read('config.ini')
correlation_threshold = float(config['DEFAULT']['CorrelationThreshold'])
debug = bool(config.getboolean('DEFAULT', 'Debug'))
key_to_press = config['DEFAULT']['KeyToPress']
audioinput = int(config['DEFAULT']['AudioInput'])
cooldown_time = float(config['DEFAULT']['CooldownTime'])


def load_samples():
	global ahh_templates  # Declare ahh_templates as global
	sample_files = [f for f in os.listdir(sample_folder) if f.endswith('.wav')]
	for f in sample_files:
		audio, sr = librosa.load(os.path.join(sample_folder, f), sr=44100)
		ahh_templates.append(audio)
	return sr  # return sample rate

# Helper function to find the audio devices. 
def findAudioDevices():
	p = pyaudio.PyAudio()
	info = p.get_host_api_info_by_index(0)
	numdevices = info.get('deviceCount')
	device_info = ""
	for i in range(0, numdevices):
		if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
			device_info += f"Input Device ID {i} - {p.get_device_info_by_host_api_device_index(0, i).get('name')}\n"
	sg.popup('Audio Devices', device_info)

# Function to perform cross-correlation
def detect_ahh(audio_signal, templates, threshold):
	max_correlations = []
	for template in templates:
		c = np.correlate(audio_signal, template, mode='valid')
		max_correlations.append(np.max(c))
	max_correlation = np.max(max_correlations)
	return max_correlation > threshold

# The function running the detection loop
def detection_loop(windo, sr, cooldown_time):
	global stop_thread
	global ahh_templates
	stop_thread = False	 # Reset when function starts
	p = pyaudio.PyAudio()
	
	if debug:
		logging.debug(f"Initializing stream with input_device_index: {audioinput}, rate: {sr}")

	
	stream = p.open(format=pyaudio.paFloat32,
					channels=1,
					rate=sr,
					input=True,
					input_device_index=audioinput,
					frames_per_buffer=2048)
	last_triggered_time = 0	 # Initialize to zero for first loop
	
	
	if debug:
		logging.debug("Stream initialized.")
	

	while True:
		if stop_thread:
			if debug:
				logging.debug("About to terminate stream.")
			stream.stop_stream()  # Stop the audio stream
			stream.close()	# Close the audio stream
			p.terminate()  # Terminate the PyAudio object
			break  # Break out of the loop
		try:
			block = stream.read(2048, exception_on_overflow=False)
		except Exception as e:
			if debug:
				logging.debug(f"Exception caught while reading stream: {e}")	
		audio_signal = np.frombuffer(block, dtype=np.float32)
		current_time = time.time()
		max_correlation_value = detect_ahh(audio_signal, ahh_templates, correlation_threshold)
		if debug:
			print(f"Max Correlation Value: {max_correlation_value}, Timestamp: {current_time}")
		if max_correlation_value > correlation_threshold:
			if current_time - last_triggered_time > cooldown_time:
				try:
					pyautogui.press(key_to_press)
				except Exception as e:
					if debug:
						logging.debug(f"Error occurred while pressing key: {e}. Ahh sound detected!")
				windo.change_icon(r'IconOn.png')  # Set this variable to your inverted icon
				# After a short delay, revert back to the original icon
				time.sleep(0.5)
				windo.change_icon(r'Icon.png')				  
				last_triggered_time = current_time
				# Here you can send a message to your GUI or trigger other actions

def initialize_program():
	global stop_thread, t
	
	# Debug log example
	if debug:
		logging.debug("initialize_program() called")
		
	# PySimpleGUI setup
	menu_def = ['File', ['Show Audio Devices', 'Open Config', 'Open Sound Files', 'Reload Samples','Exit']]
	tooltip = 'Tooltip'
	layout = [[sg.T('Empty Window', key='-T-')]]
	window = sg.Window('Window Title', layout, finalize=True, enable_close_attempted_event=True, alpha_channel=0)
	window.hide()

	
	# Initialize the tray
	tray = SystemTray(menu=menu_def, single_click_events=False, tooltip=tooltip, window=window, icon=r'Icon.png')
	tray.show_message('Sound Switch', 'Sound Switchs Started!')

	sr = load_samples()	 # get the sample rate	  
	# Start detection loop in a separate thread
	stop_thread = True
	if 't' in globals():  # Check if the thread exists
		t.join()  # Wait for the existing thread to finish
	t = threading.Thread(target=detection_loop, args=(tray, sr, cooldown_time))
	t.start()
	stop_thread = False
	
	# Event loop
	while True:
		event, values = window.read()
		menu_item = values[event]
		if menu_item == 'Reload Samples':
			load_samples()	# Reload the audio samples
			stop_thread = True
			t.join()  # Wait for the existing thread to finish
			stop_thread = False
			t = threading.Thread(target=detection_loop, args=(tray,sr, cooldown_time))
			t.start()  # Start a new detection thread
		elif menu_item == 'Exit':
			stop_thread = True	# Signal to stop the detection_loop thread
			if 't' in globals():  # Check if the thread exists
					t.join()  # Wait for the existing thread to finish
					break  # Then break out of the event loop
		elif menu_item == 'Show Audio Devices':
			findAudioDevices()	# This function should probably be modified to display a popup instead of printing to console
		elif menu_item == 'Open Config':
			os.system(f"notepad {config_path}")
		elif menu_item == 'Open Sound Files':
			os.startfile(sample_folder)

	tray.close()
	window.close()

initialize_program()	
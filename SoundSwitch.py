import pyaudio
import numpy as np
import librosa
import configparser
import os
import sys
import PySimpleGUI as sg
from psgtray import SystemTray
import threading
import time
import pyautogui
import logging
# New SVM technique 
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline


# Enable logging if debug flag is set
# Initialize the argparse
logging.basicConfig(filename='app.log', level=logging.DEBUG)
ahh_templates = []
# Global variables
clf = None	# The SVM classifier
scaler = StandardScaler()  # Feature scaler


# Determine application and config paths
if getattr(sys, 'frozen', False):
	home_directory = os.path.expanduser("~")
	application_path = os.path.join(home_directory, 'AppData', 'Roaming', 'SoundSwitch')
elif __file__:
	application_path = os.path.dirname(__file__)
config_path = os.path.join(application_path, 'config.ini')

# Read config file
config = configparser.ConfigParser()
config.read('config.ini')
correlation_threshold = float(config['DEFAULT']['CorrelationThreshold'])
debug = bool(config.getboolean('DEFAULT', 'Debug'))
key_to_press = config['DEFAULT']['KeyToPress']
audioinput = int(config['DEFAULT']['AudioInput'])
cooldown_time = float(config['DEFAULT']['CooldownTime'])

def load_clips():
    global positive_clips, background_noises, application_path  # Declare as global if you plan to use them globally
    positive_path = os.path.join(application_path, 'positive-samples')
    negative_path = os.path.join(application_path, 'negative-samples')
    
    positive_clips = []
    background_noises = []
    
    for f in os.listdir(positive_path):
        if f.endswith('.wav'):
            audio, sr = librosa.load(os.path.join(positive_path, f), sr=44100)
            positive_clips.append(audio)
            
    for f in os.listdir(negative_path):
        if f.endswith('.wav'):
            audio, sr = librosa.load(os.path.join(negative_path, f), sr=44100)
            background_noises.append(audio)


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



def extract_combined_features(audio, sr):
	mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
	chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
	spectral_contrast = librosa.feature.spectral_contrast(y=audio, sr=sr)

	# Take the mean of each feature to use as the feature vector
	mfccs_mean = np.mean(mfccs, axis=1)
	chroma_mean = np.mean(chroma, axis=1)
	spectral_contrast_mean = np.mean(spectral_contrast, axis=1)

	# Combine the features into a single array
	combined_features = np.concatenate((mfccs_mean, chroma_mean, spectral_contrast_mean))

	return combined_features


def train_svm_classifier(positive_clips, background_noises, sr=44100):
	global clf, scaler

	X_train = []
	y_train = []

	for clip in positive_clips:
		features = extract_combined_features(clip, sr)
		X_train.append(features)
		y_train.append(1)  # Label for positive clips

	for noise in background_noises:
		features = extract_combined_features(noise, sr)
		X_train.append(features)
		y_train.append(0)  # Label for negative clips

	# Scale features
	X_train = scaler.fit_transform(X_train)

	# Train the classifier
	clf = make_pipeline(StandardScaler(), SVC(gamma='auto'))
	clf.fit(X_train, y_train)

# Function to detect sound using the trained SVM classifier
def detect_ahh(audio_signal, sr):
	global clf, scaler

	features = extract_combined_features(audio_signal, sr)
	scaled_features = scaler.transform([features])	# Note the [features] to make it 2D array
	prediction = clf.predict(scaled_features)
	return prediction[0] == 1  # 1 is the label for positive clips


# The function running the detection loop
def detection_loop(windo, sr, cooldown_time):
	global stop_thread
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
		detected = detect_ahh(audio_signal, sr)
		if detected:
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

def initialize_program():
	global stop_thread, t
	#
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

	sr = load_clips()	 # get the sample rate	  
	
	# Train the classifier
	train_svm_classifier(positive_clips, background_noises, sr=44100)

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
			load_clips()	# Reload the audio samples
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
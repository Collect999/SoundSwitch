import PySimpleGUI as sg
import pyaudio
import numpy as np
import sounddevice as sd
import threading
from datetime import datetime
import os
import wave
import sys

recording = False
paused = False
audio_data = {}
elapsed_time = 0

if getattr(sys, 'frozen', False):
	home_directory = os.path.expanduser("~")
	application_path = os.path.join(home_directory, 'AppData', 'Roaming', 'SoundSwitch')
elif __file__:
	application_path = os.path.dirname(__file__)
sample_folder = os.path.join(application_path, 'sound-samples')


def save_wav(data, filename, sample_rate=44100):
	wav_file = wave.open(filename, 'wb')
	n_channels = 1
	sampwidth = 2  # Number of bytes for each sample
	n_frames = len(data)
	comptype = "NONE"
	compname = "not compressed"

	wav_file.setparams((n_channels, sampwidth, sample_rate, n_frames, comptype, compname))

	# Convert the NumPy array to bytes
	wav_data = np.array(data * 32767, dtype=np.int16).tobytes()
	wav_file.writeframes(wav_data)
	wav_file.close()

def get_audio_devices():
	p = pyaudio.PyAudio()
	device_count = p.get_device_count()
	devices = []
	for i in range(device_count):
		device_info = p.get_device_info_by_index(i)
		devices.append(device_info['name'])
	p.terminate()
	return devices

def record_audio(device_index, num_channels):
	global recording, paused, audio_data, elapsed_time
	recording = True
	paused = False
	audio_data = {}
	with sd.InputStream(device=device_index, channels=num_channels, callback=callback):
		while recording:
			if not paused:
				elapsed_time += 1
			sd.sleep(1000)

def callback(indata, frames, time, status):
	global audio_data, elapsed_time, paused
	if not paused:
		if elapsed_time not in audio_data:
			audio_data[elapsed_time] = []
		audio_data[elapsed_time].append(indata.copy())

def main():
	global recording, paused, elapsed_time, window
	samples = []

	layout = [
		[sg.Text("Choose recording device:"),
		 sg.Combo(get_audio_devices(), key="-DEVICE-", readonly=True)],
		[sg.Text("Elapsed Time: 0s", key='-TIME-')],
		[sg.Listbox(values=samples, size=(50, 6), key='-LIST-', enable_events=True),
		 sg.Column([[sg.Button("Play")], [sg.Button("Delete")]])],
		[sg.Button("Record", key='-RECORD-', button_color=('white', 'green')),
		 sg.Button("Stop", key='-STOP-', button_color=('white', 'red'), visible=False),
		 sg.Button("Save All"), sg.Button("Open Directory"), sg.Button("Exit")]
	]

	window = sg.Window("Sample Recorder", layout)

	while True:
		event, values = window.read(timeout=10)
		window['-TIME-'].update(f"Elapsed Time: {elapsed_time}s")

		if event == "Exit" or event == sg.WIN_CLOSED:
			break
		elif event == "-RECORD-":
			if not recording:
				window['-RECORD-'].update("Pause", button_color=('white', 'red'))
				window['-STOP-'].update(visible=True)
				device_name = values["-DEVICE-"]
				p = pyaudio.PyAudio()
				for i in range(p.get_device_count()):
					device_info = p.get_device_info_by_index(i)
					if device_info["name"] == device_name:
						device_index = i
						num_channels = device_info['maxInputChannels']
						break
				p.terminate()
				elapsed_time = 0
				threading.Thread(target=record_audio, args=(device_index, num_channels)).start()
			else:
				window['-RECORD-'].update("Record", button_color=('white', 'green'))
				paused = True

		elif event == "-STOP-":
			recording = False
			paused = False
			window['-RECORD-'].update("Record", button_color=('white', 'green'))
			window['-STOP-'].update(visible=False)
			timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
			all_data = [item for sublist in audio_data.values() for item in sublist]
			np_data = np.concatenate(all_data, axis=0) if all_data else np.array([])
			audio_data[timestamp] = np_data
			samples.append(timestamp)
			window['-LIST-'].update(samples)

		elif event == "Play":
			selected_sample = values['-LIST-']
			if selected_sample:
				sample_data = audio_data.get(selected_sample[0], None)
				if sample_data is not None:
					sd.play(sample_data, 44100)
					sd.wait()

		elif event == "Delete":
			selected_sample = values['-LIST-']
			if selected_sample:
				del audio_data[selected_sample[0]]
				samples.remove(selected_sample[0])
				window['-LIST-'].update(samples)

		elif event == "Save All":
			for timestamp, data in audio_data.items():
				save_wav(data, os.path.join(sample_folder, f"audio_sample_{timestamp}.wav"))
			sg.popup("All samples saved!")

		elif event == "Open Directory":
			os.system(f'explorer {os.path.realpath(sample_folder)}')

	window.close()

if __name__ == "__main__":
	main()

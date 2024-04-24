import pyaudio
import wave
import os
from sftp_connection import SFTPConnection
from database_connection import DatabaseConnection

FORMAT = pyaudio.paInt16
SAMPLE_RATE = 44100
CHANNELS = 1
CHUNK = 4096
RECORDING_DURATION = 10


def search_devices_by_name(name, max_devices=2):
    devices = []
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if name in device_info.get('name'):
            devices.append(i)
            if len(devices) >= max_devices:
                break
    return devices


def start_recording(device, sftp):
    store = {}
    store['counter'] = int((SAMPLE_RATE/CHUNK) * RECORDING_DURATION)
    store['path'] = os.path.abspath(f'test{device}.wav')
    store['file'] = wave.open(store['path'], 'wb')
    store['file'].setnchannels(CHANNELS)
    store['file'].setsampwidth(p.get_sample_size(FORMAT))
    store['file'].setframerate(SAMPLE_RATE)
    
    def callback(in_data, frame_count, time_info, status_flags):
        store['file'].writeframes(in_data)
        
        if store['counter'] <= 0:
            store['file'].close()
            return None, pyaudio.paComplete
        else:
            store['counter'] -= 1
            return None, pyaudio.paContinue
        
    stream = p.open(
        format=FORMAT,
        rate=SAMPLE_RATE,
        channels=CHANNELS,
        input_device_index=device,
        input=True,
        frames_per_buffer=CHUNK,
        stream_callback=callback
        )
    
    return stream, store['path'], device


def start_recordings(devices, sftp):
    streams = []
    for device in devices:
        streams.append(start_recording(device, sftp))
    return streams


def is_any_stream_active(streams):
    for stream, path in streams:
        if stream.is_active():
            return True
    return False
             

if __name__ == '__main__':
    p = pyaudio.PyAudio()
    devices = search_devices_by_name('USB Audio Device')
    sftp = SFTPConnection()
    db = DatabaseConnection()
    streams = start_recordings(devices, sftp)
    
    while is_any_stream_active(streams):
        pass
    
    for stream, path, device in streams:
        remote_path = sftp.upload_recording(path)
        if sftp.file_exists(remote_path):
            db.insert_sound_data(device, path)
        
    sftp.close()
    p.terminate()




import pyaudio
import wave
import os
import shortuuid

class RecordingDevice:
    
    __pyaudio = pyaudio.PyAudio()
    
    def __init__(self, device_index):
        self.device_index = device_index
        self.stream = None
    
    
    def __recording_callback(self, in_data, frame_count, time_info, status_flags):
        self.__file.writeframes(in_data)
        
        if self.__counter <= 0:
            self.__file.close()
            return None, pyaudio.paComplete
        else:
            self.__counter -= 1
            return None, pyaudio.paContinue
    
    
    def start_recording(self):
        FORMAT = pyaudio.paInt16
        SAMPLE_RATE = 44100
        CHANNELS = 1
        CHUNK = 4096
        RECORDING_DURATION = 10
        
        self.file_path = os.path.abspath(f'{shortuuid.uuid()}.wav')
        self.__counter = int((SAMPLE_RATE/CHUNK) * RECORDING_DURATION)
        
        try:
            self.__file = wave.open(self.file_path, 'wb')
            self.__file.setnchannels(CHANNELS)
            self.__file.setsampwidth(RecordingDevice.__pyaudio.get_sample_size(FORMAT))
            self.__file.setframerate(SAMPLE_RATE)
        except:
            print('Failed to open recording file')
            return
        
        try:
            self.stream = RecordingDevice.__pyaudio.open(
                format=FORMAT,
                rate=SAMPLE_RATE,
                channels=CHANNELS,
                input_device_index=self.device_index,
                input=True,
                frames_per_buffer=CHUNK,
                stream_callback=self.__recording_callback
            )
        except:
            print('Failed to start recording')
        
        
    def is_recording_active(self):
        if self.stream:
            return self.stream.is_active()
        else:
            return False
        
        
    @staticmethod
    def is_any_recording_active(devices):
        for device in devices:
            if device.is_recording_active():
                return True
        return False
        
    
    @staticmethod
    def get_devices_by_name(name, start_recording=False, max_devices=2):
        devices = []
        for i in range(RecordingDevice.__pyaudio.get_device_count()):
            device_info = RecordingDevice.__pyaudio.get_device_info_by_index(i)
            if (name in device_info.get('name') and device_info.get('maxInputChannels') > 0):
                device = RecordingDevice(i)
                if start_recording:
                    device.start_recording()
                devices.append(device)
                if len(devices) >= max_devices:
                    break
        return devices
             
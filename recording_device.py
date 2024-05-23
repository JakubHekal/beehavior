import pyaudio
import wave
import os
import shortuuid


class RecordingDevice:
    FORMAT = pyaudio.paInt16
    SAMPLE_RATE = 44100
    CHANNELS = 1
    CHUNK = 4096
    __pyaudio = pyaudio.PyAudio()

    def __init__(self, device_index):
        self.device_index = device_index

    def record(self, path, duration):
        with wave.open(path, 'wb') as file:
            file.setnchannels(RecordingDevice.CHANNELS)
            file.setsampwidth(RecordingDevice.__pyaudio.get_sample_size(RecordingDevice.FORMAT))
            file.setframerate(RecordingDevice.SAMPLE_RATE)

            stream = RecordingDevice.__pyaudio.open(
                input_device_index=self.device_index,
                format=RecordingDevice.FORMAT,
                channels=RecordingDevice.CHANNELS,
                rate=RecordingDevice.SAMPLE_RATE,
                input=True
            )

            for _ in range(0, RecordingDevice.SAMPLE_RATE // RecordingDevice.CHUNK * duration):
                file.writeframes(stream.read(RecordingDevice.CHUNK))

            stream.close()

    @staticmethod
    def get_devices_by_name(name, max_devices=10):
        devices = []
        for i in range(RecordingDevice.__pyaudio.get_device_count()):
            device_info = RecordingDevice.__pyaudio.get_device_info_by_index(i)
            if name in device_info.get('name') and device_info.get('maxInputChannels') > 0:
                device = RecordingDevice(i)
                devices.append(device)
                if len(devices) >= max_devices:
                    break

        return devices

    @staticmethod
    def get_device_by_name(name, index=0):
        return RecordingDevice.get_devices_by_name(name)[index]

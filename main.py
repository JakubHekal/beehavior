import concurrent.futures
import glob
import time
import datetime
import schedule
import os
import pywifi
from pywifi import const
import requests

from config import get_config
from recording_device import RecordingDevice
from sensor_device import *


def record(hive_id, microphone):
    print(f'Recording started {hive_id}')
    path = os.path.join(
        os.path.dirname(__file__),
        f"{hive_id}-{int(time.time())}.wav"
    )
    timestamp = datetime.datetime.now()
    microphone.record(path, config['general']['recording']['duration'])

    requests_queue.append({
        'path': '/recordings',
        'data': {
            'hive_id': hive_id,
            'recorded_at': timestamp
        },
        'filepath': path
    })


def measure(hive_id, sensors):
    print(f'Measurement started {hive_id}')
    temperature_in, humidity_in, temperature_out = None, None, None
    for device in sensors:
        if device.ambient:
            temperature_out = device.measure()
        else:
            temperature_in, humidity_in = device.measure()

    requests_queue.append({
        'path': '/measurements',
        'data': {
            'hive_id': hive_id,
            'temp_in': temperature_in,
            'humi_in': humidity_in,
            'temp_out': temperature_out,
            'measured_at': datetime.datetime.now()
        }
    })


def load_cache():
    for i, filename in enumerate(glob.glob(os.path.join(os.path.dirname(__file__), '*.wav'))):
        parts = filename.replace('.wav', '').split('-')
        hive_id = '-'.join(parts[0:2])
        timestamp = datetime.datetime.fromtimestamp(int(parts[2]))

        requests_queue.append({
            'path': '/recordings',
            'data': {
                'hive_id': hive_id,
                'recorded_at': timestamp
            },
            'filepath': filename
        })


def handle_requests():
    if len(requests_queue) > 0:
        request_data = requests_queue.pop(0)
        if 'filepath' in request_data:
            print(f'Request {request_data["path"]} with file {request_data["filepath"]} ... started')
            with open(request_data['filepath'], 'rb') as file:
                response = requests.post(
                    config['general']['api_root'] + request_data['path'],
                    data=request_data['data'],
                    files={
                        'recording': file
                    }
                )

                if response.status_code != 200:
                    requests_queue.append(request_data)
                    print(f'Request {request_data["path"]} with file {request_data["filepath"]} ... failed {response.status_code}')
                else:
                    os.remove(request_data['filepath'])
                    print(f'Request {request_data["path"]} with file {request_data["filepath"]} ... sent')

        else:
            print(f'Request {request_data["path"]} ... started')
            response = requests.post(
                config['general']['api_root'] + request_data['path'],
                data=request_data['data']
            )
            if response.status_code != 200:
                requests_queue.append(request_data)
                print(f'Request {request_data["path"]} ... failed {response.status_code}')
            else:
                print(f'Request {request_data["path"]} ... sent')


if __name__ == '__main__':
    config = get_config(os.path.join(
        os.path.dirname(__file__),
        'config.yaml'
    ))

    wifi = pywifi.PyWiFi()

    interface = None
    for i in wifi.interfaces():
        if i.name() == config['wifi']['interface']:
            interface = i

    if interface.status() != const.IFACE_CONNECTED:
        profile = pywifi.Profile()
        profile.ssid = config['wifi']['ssid']
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm.append(const.AKM_TYPE_WPA2PSK)
        profile.cipher = const.CIPHER_TYPE_CCMP
        profile.key = config['wifi']['password']

        interface.remove_all_network_profiles()
        profile = interface.add_network_profile(profile)
        interface.connect(profile)

        time.sleep(30)
        assert interface.status() == const.IFACE_CONNECTED

    hive_sensors = {}
    for sensor_config in config['sensors']:
        sensor_device = SensorDevice.setup_from_config(sensor_config)
        for hive in sensor_config['hive']:
            hive = f"{config['general']['station']}-{hive}"
            if hive not in hive_sensors:
                hive_sensors[hive] = []
            hive_sensors[hive].append(sensor_device)

    hive_microphone = {}
    for microphone_config in config['microphones']:
        recording_device = RecordingDevice.get_device_by_name(microphone_config['name'], microphone_config['index'])
        hive_microphone[f"{config['general']['station']}-{microphone_config['hive']}"] = recording_device

    requests_queue = []

    load_cache()

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for h, m in hive_microphone.items():
            schedule.every(config['general']['recording']['interval']).seconds.do(executor.submit, record, h, m)
        for h, s in hive_sensors.items():
            schedule.every(config['general']['measurements']['interval']).seconds.do(executor.submit, measure, h, s)
        request_thread = executor.submit(handle_requests)
        while 1:
            if request_thread.done():
                request_thread = executor.submit(handle_requests)
            schedule.run_pending()
            time.sleep(1)

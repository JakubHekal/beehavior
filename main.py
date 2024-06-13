import concurrent.futures
import time
import datetime
import schedule
import os
import pywifi
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

    with open(path, 'rb') as file:
        requests.post(
            config['general']['api_root'] + '/recordings',
            data={
                'hive_id': hive_id,
                'recorded_at': timestamp
            },
            files={'recording': file}
        )
    os.remove(path)


def measure(hive_id, sensors):
    print(f'Measurement started {hive_id}')
    temperature_in, humidity_in, temperature_out = None, None, None
    for device in sensors:
        if device.ambient:
            temperature_out = device.measure()
        else:
            temperature_in, humidity_in = device.measure()

    requests.post(
        config['general']['api_root'] + '/measurements',
        {
            'hive_id': hive_id,
            'temp_in': temperature_in,
            'humi_in': humidity_in,
            'temp_out': temperature_out,
            'measured_at': datetime.datetime.now()
        }
    )


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

    profile = pywifi.Profile()
    profile.ssid = config['wifi']['ssid']
    profile.auth = 0
    profile.akm.append(4)
    profile.cipher = 3
    profile.key = config['wifi']['password']

    interface.remove_all_network_profiles()
    profile = interface.add_network_profile(profile)
    interface.connect(profile)

    time.sleep(30)

    assert interface.status() == 4

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

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for h, m in hive_microphone.items():
            schedule.every(config['general']['recording']['interval']).seconds.do(executor.submit, record, h, m)
        for h, s in hive_sensors.items():
            schedule.every(config['general']['measurements']['interval']).seconds.do(executor.submit, measure, h, s)
        while 1:
            schedule.run_pending()
            time.sleep(1)

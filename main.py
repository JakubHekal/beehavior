import concurrent.futures
import time
import schedule
import os
from config import get_config
from database_connection import DatabaseConnection
from recording_device import RecordingDevice
from sensor_device import *
from sftp_connection import SFTPConnection


def record(microphone):
    device = RecordingDevice.get_device_by_name(microphone['name'], microphone['index'])
    path = os.path.join(
        os.path.dirname(__file__),
        f'{config['general']['station']}-{microphone['hive']}-{int(time.time())}.wav'
    )
    device.record(path, config['general']['recording']['duration'])

    remote_path = sftp.upload_recording(path)
    if sftp.file_exists(remote_path):
        db.insert_sound_data(device.device_index, remote_path)


def measure(hive_id, sensors):
    temperature_in, humidity_in, temperature_out = None, None, None
    for device in sensors:
        if device.ambient:
            temperature_out = device.measure()
        else:
            temperature_in, humidity_in = device.measure()
    db.insert_hive_data(hive_id, temperature_in, humidity_in, temperature_out)


if __name__ == '__main__':
    config = get_config(os.path.join(
        os.path.dirname(__file__),
        'config.yaml'
    ))

    sftp = SFTPConnection(
        host=config['sftp']['host'],
        port=config['sftp']['port'],
        user=config['sftp']['user'],
        password=config['sftp']['password']
    )
    db = DatabaseConnection(
        host=config['database']['host'],
        user=config['database']['user'],
        password=config['database']['password'],
        database=config['database']['database']
    )

    hive_sensors = {}
    for sensor in config['sensors']:
        sensor_device = SensorDevice.setup_from_config(sensor)
        for hive in sensor['hive']:
            if hive not in hive_sensors:
                hive_sensors[hive] = []
            hive_sensors[hive].append(sensor_device)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for m in config['microphones']:
            print(m)
            schedule.every(config['general']['recording']['interval']).seconds.do(executor.submit, record, m)
        for h, s in hive_sensors.items():
            schedule.every(config['general']['measurements']['interval']).seconds.do(executor.submit, measure, h, s)
        while 1:
            schedule.run_pending()
            time.sleep(1)


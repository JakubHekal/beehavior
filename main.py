import concurrent.futures
import time
import schedule
import os
from config import get_config
from database_connection import DatabaseConnection
from recording_device import RecordingDevice
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

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for m in config['microphones']:
            print(m)
            schedule.every(config['general']['recording']['interval']).seconds.do(executor.submit, record, m)
        while 1:
            schedule.run_pending()
            time.sleep(1)

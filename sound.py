from config import get_config
from recording_device import RecordingDevice
from sftp_connection import SFTPConnection
from database_connection import DatabaseConnection

if __name__ == '__main__':

    config = get_config('config.yaml')

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
    
    devices = RecordingDevice.get_devices_by_name('USB Audio Device', True)
    
    while RecordingDevice.is_any_recording_active(devices):
        pass
    
    for device in devices:
        remote_path = sftp.upload_recording(device.file_path)
        if sftp.file_exists(remote_path):
            db.insert_sound_data(device.device_index, remote_path)
        
    sftp.close()




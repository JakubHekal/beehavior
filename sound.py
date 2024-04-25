from recording_device import RecordingDevice
from sftp_connection import SFTPConnection
from database_connection import DatabaseConnection

if __name__ == '__main__':
    
    sftp = SFTPConnection()
    db = DatabaseConnection()
    
    devices = RecordingDevice.get_devices_by_name('USB Audio Device', True)
    
    while RecordingDevice.is_any_recording_active(devices):
        pass
    
    for device in devices:
        remote_path = sftp.upload_recording(device.file_path)
        if sftp.file_exists(remote_path):
            db.insert_sound_data(device.device_index, remote_path)
        
    sftp.close()




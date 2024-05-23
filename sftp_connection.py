import paramiko
import os


class SFTPConnection:

    def __init__(self, host, port, user, password):
        try:
            self.conn = paramiko.SSHClient()
            self.conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.conn.connect(
                hostname=host,
                port=port,
                username=user,
                password=password,
                look_for_keys=False
            )
        except:
            print('Failed connecting to SFTP')

    def upload_recording(self, path):
        sftp = self.conn.open_sftp()
        head, tail = os.path.split(path)
        remote_path = f'/home/projekt/{tail}'
        try:
            sftp.put(path, remote_path)
            return remote_path
        except:
            print('Upload failed')
        sftp.close()

    def file_exists(self, path):
        sftp = self.conn.open_sftp()
        try:
            sftp.stat(path)
            return True
        except IOError:
            return False
        sftp.close()

    def close(self):
        self.conn.close()

import paramiko

class SFTPConnection:

    def __init__(self):
        try:
            self.conn = paramiko.SSHClient()
            self.conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.conn.connect(
                hostname='fyzika.feec.vutbr.cz',
                port=22,
                username='projekt',
                password='ba7men6a',
                look_for_keys=False
            )
            self.sftp = self.conn.open_sftp()
        except:
            print('Failed connecting to SFTP')

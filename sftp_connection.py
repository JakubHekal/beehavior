import pysftp

class SFTPConnection:

    def __init__(self):
        try:
            self.conn = pysftp.Connection(
                host='fyzika.feec.vutbr.cz',
                port='22',
                username='projekt',
                password='ba7men6a',
                default_path='/home/projekt'
            )
        except:
            print('Failed connecting to SFTP')

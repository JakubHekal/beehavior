import MySQLdb
import os   # ondrova změna
from dotenv import load_dotenv  # ondrova změna

load_dotenv()     # ondrova změna


class DatabaseConnection:
    
    def __init__(self):
        try:
            self.db = MySQLdb.connect(
                host=os.getenv('database_host'),             # velké ondrovy změny
                user=os.getenv('database_user'),
                password=os.getenv('database_password'),
                database=os.getenv('database'),
            )
        except:
            print('Failed connecting to database')

    def insert_hive_data(self, hive, temp_in, humi_in, temp_out):
        try:
            c = self.db.cursor()
            c.execute('INSERT INTO measurements (hive, temp_in, humi_in, temp_out) VALUES (%s, %s, %s, %s)', (hive, temp_in, humi_in, temp_out))
            c.close()
        except:
            print('Insert into "measurements" failed')

    def insert_sound_data(self, hive, path):
        try:
            c = self.db.cursor()
            c.execute('INSERT INTO recordings (hive, path) VALUES (%s, %s)', (hive, path))
            c.close()
        except:
            print('Insert into "recordings" failed')

    def insert_error(self, hive, message):
        try:
            c = self.db.cursor()
            c.execute('INSERT INTO errors (hive, message) VALUES (%s, %s)', (hive, message))
            c.close()
        except:
            print('Insert into "errors" failed')

import MySQLdb


class DatabaseConnection:
    
    def __init__(self, host, user, password, database):
        try:
            self.db = MySQLdb.connect(
                host=host,
                user=user,
                password=password,
                database=database,
            )
        except Exception as e:
            print(f'Failed connecting to database: {e}')

    def insert_hive_data(self, hive, temp_in, humi_in, temp_out, timestamp):
        try:
            c = self.db.cursor()
            c.execute('INSERT INTO measurements (hive, temp_in, humi_in, temp_out, timestamp) VALUES (%s, %s, %s, %s, %s)', (hive, temp_in, humi_in, temp_out, timestamp))
            c.close()
        except:
            print('Insert into "measurements" failed')

    def insert_sound_data(self, hive, path, timestamp):
        try:
            c = self.db.cursor()
            c.execute('INSERT INTO recordings (hive, path, timestamp) VALUES (%s, %s, %s)', (hive, path, timestamp))
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

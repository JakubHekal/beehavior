import MySQLdb

class DatabaseConnection:
    
    def __init__(self):
        try:
            self.db = MySQLdb.connect(
                host = 'fyzika.feec.vutbr.cz',
                user = 'projekt_user',
                password = 'han27dom',
                database = 'projekt',
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
    

    def insert_error(self, hive, message):
        try:
            c = self.db.cursor()
            c.execute('INSERT INTO errors (hive, message) VALUES (%s, %s)', (hive, message))
            c.close()
        except:
            print('Insert into "errors" failed')

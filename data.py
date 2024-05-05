from sensirion_i2c_driver import I2cConnection, errors
from sensirion_i2c_sht.sht3x import Sht3xI2cDevice
from sensirion_i2c_driver.linux_i2c_transceiver import LinuxI2cTransceiver
from pi1wire import Pi1Wire, Resolution, _exception
from database_connection import DatabaseConnection


def measure_temp_humi(device_file, slave_address=0x44):
    try:
        sht3x = Sht3xI2cDevice(I2cConnection(LinuxI2cTransceiver(device_file)), slave_address)
        sht3x.single_shot_measurement()
        temp, humi = sht3x.single_shot_measurement()
        return temp.degrees_celsius, humi.percent_rh
    except errors.I2cTransceiveError:
        print(f'Sensor missing [I2C-{hex(slave_address)}]')
    except:
        print(f'Unknown error [I2C-{hex(slave_address)}]')


def measure_temp(mac):
    try:
        sensor = Pi1Wire().find(mac)
        return sensor.get_temperature()
    except _exception.NotFoundSensorException:
        print(f'Sensor missing [1Wire-{mac}]')
    except:
        print(f'Unknown error [1Wire-{mac}]')
        

if __name__ == "__main__":
    database = DatabaseConnection()
    out = measure_temp('28c81fb20164ff')
    hives = [measure_temp_humi('/dev/i2c-1'), measure_temp_humi('/dev/i2c-1', 0x45)]
    
    for (i, hive) in enumerate(hives):
    
        if hive != None and out != None:
            database.insert_hive_data(i+1, hive[0], hive[1], out)
        else:
            print(f'Missing data [HIVE{i+1}]')

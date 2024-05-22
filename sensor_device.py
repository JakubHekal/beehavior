from pi1wire import Pi1Wire
from sensirion_i2c_driver import I2cConnection, LinuxI2cTransceiver
from sensirion_i2c_sht.sht3x import Sht3xI2cDevice


class SensorDevice:
    def __init__(self, ambient):
        self.ambient = ambient

    @staticmethod
    def setup_from_config(config):
        match config['comm']:
            case 'i2c': I2CSensorDevice(config['device_file'], config['address'], config['ambient'])
            case 'w1': OneWireSensorDevice(config['mac'], config['ambient'])


class I2CSensorDevice(SensorDevice):
    def __init__(self, device_file, address, ambient):
        super().__init__(ambient)
        self.sensor = Sht3xI2cDevice(I2cConnection(LinuxI2cTransceiver(device_file)), address)

    def measure(self):
        self.sensor.single_shot_measurement()
        temperature, humidity = self.sensor.single_shot_measurement()
        return temperature.degrees_celsius, humidity.percent_rh


class OneWireSensorDevice(SensorDevice):
    def __init__(self, mac_address, ambient):
        super().__init__(ambient)
        self.sensor = Pi1Wire().find(mac_address)

    def measure(self):
        return self.sensor.get_temperature()

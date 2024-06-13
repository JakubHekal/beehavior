# Configuration file

> **Information:**
> The configuration file is written using YAML. You can find its syntax nicely explained here https://en.wikipedia.org/wiki/YAML#Syntax

Main configuration file `config.yaml` is located in root of the project. It needs to be available on all stations. 
It has 6 main sections `wifi`, `database`, `sftp`, `general`, `microphones` and `sensors`.

> **Warning:**
> Never commit config files to GitHub repository

## Wifi
Section for setting up wireless connection to the internet
```yaml
wifi:
  ssid: 'wifi'
  password: 'pass123'
  interface: 'wlan0'
```
- `ssid`: The ssid of the network.
- `password`: The password to connect to the network.
- `interface`: The interface used for connecting.

## General
Section that contains properties specifying the behaviour of the station
```yaml
general:
  api_root: 'https://api.vcelky.com'
  station: 'sad'
  hives: [1,2]
  recording:
    interval: 1800
    duration: 300
  measurements:
    interval: 600
```
- `api_root`: The root url of remote API.
- `station`: The unique ID given to each station.
- `hives`: The list of hive IDs connected to specified station.
- `recording`: Properties that control sound recording 
  - `interval`: The interval between recordings in seconds.
  - `duration`: The duration of each recording in seconds.
- `measurements`: Properties that control measurement of temperature and humidity
  - `interval`: The interval between measurements in seconds.

## Microphones
A list of audio input devices connected to the station.
```yaml
microphones:
  -
    name: 'USB Audio Device'
    index: 0
    hive: 1
  -
    name: 'USB Audio Device'
    index: 1
    hive: 2
```
Each audio device has these properties:
- `name`: The name of the audio input device used by stations OS.
- `index`: Index of the audio device, used if multiple devices have a same name. Defaults to 0
- `hive`: The hive ID the microphone is associated with (one of those specified in `general.hives`)

## Sensors
A list of sensors connected to the station.
```yaml
sensors:
  -
    comm: 'w1'
    mac: '28c81fb20164ff'
    ambient: true
    hive: [1,2]
  -
    comm: 'i2c'
    device_file: '/dev/i2c-1'
    address: '0x44'
    hive: 1
```
Following properties are common for all types of sensors:
- `comm`: The communication protocol used by the sensor. Currently only two protocols are supported 'w1' for 1Wire, 'i2c' for I2C.
- `hive`: The hive ID or list of hive IDs the sensor is associated with.
- `ambient`: If true this sensor is used for measuring ambient conditions.

Additional properties are dependent on communication protocol used by each sensor
### I2C sensor
- `device_file`: The device file for the sensor.
- `address`: The I2C address of the sensor.
### 1Wire sensor
- `mac`: The MAC address of the sensor.
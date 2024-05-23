from ruamel.yaml import YAML
from schema import Schema, Or, Use, Optional


def get_config(path):

    schema = Schema({
        'wifi': {
            'ssid': Use(str),
            'password': Use(str),
            'interface': Use(str), 
        },
        'database': {
            'host': Use(str),
            'user': Use(str),
            'password': Use(str),
            'database': Use(str)
        },
        'sftp': {
            'host': Use(str),
            'port': Use(int),
            'user': Use(str),
            'password': Use(str),
        },
        'general': {
            'station': Use(str),
            'hives': [Use(str)],
            'recording': {
                'interval': Use(int),
                'duration': Use(int)
            },
            'measurements': {
                'interval': Use(int)
            }
        },
        'microphones': [{
            'name': Use(str),
            Optional('index', default=0): Use(int),
            'hive': Use(str)
        }],
        'sensors': [{
            'comm': lambda s: s in ('i2c', 'w1'),
            'hive': Or([Use(str)], Use(str)),
            Optional('ambient', default=False): Use(bool),
            str: object
        }],
    }, ignore_extra_keys=True)

    with open(path) as file:
        yaml = YAML()
        code = yaml.load(file)
        valid = schema.validate(code)
        return valid

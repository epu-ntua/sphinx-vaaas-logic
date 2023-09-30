import os
import json

config = None


def read_config():
    global config
    script_path = os.path.abspath(__file__)
    script_dir = os.path.split(script_path)[0]

    with open(str(os.path.join(script_dir, 'default.json'))) as default_data:
        config = json.load(default_data)

    with open(str(os.path.join(script_dir, 'config.json'))) as config_data:
        config.update(json.load(config_data))


def get_config():
    global config
    if not config:
        read_config()
    return config

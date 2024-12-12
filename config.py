import yaml
import os

def load_eve_config(config_path='/opt/evectl/etc/evectl.yaml'):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

eve_cfg = load_eve_config()

def validate_config(config):
    required_keys = ['directories', 'network']
    for key in required_keys:
        if key not in config:
            raise KeyError(f"Missing required configuration key: {key}")

    return True
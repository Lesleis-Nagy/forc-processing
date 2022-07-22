from importlib import resources

import yaml
from yaml.loader import SafeLoader

def get_config():
    config_file = resources.open_text("forc_processing.config", "config.yaml")
    data = yaml.load(config_file, SafeLoader)
    return data

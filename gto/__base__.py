from .exceptions import ConfigNotFoundException
import json
import os


moduledir = os.path.dirname(os.path.abspath(__file__))
basedir = os.path.dirname(moduledir)


def get_config():
    if os.path.isfile(os.path.join(basedir, "config.json")):
        with open(os.path.join(basedir, "config.json")) as f:
            return json.load(f)
    raise ConfigNotFoundException


configdict = get_config()

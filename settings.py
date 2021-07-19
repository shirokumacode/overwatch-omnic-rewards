from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import os,json

import logging
logger = logging.getLogger(__name__)

class Settings():

    #Default settings
    settings = {
        'account': '', 
        'owl': True, 
        'owc': True, 
        'min_check': 10
    }

    def __init__(self, location:str):
        self.file_path = location
        self.load_settings()

    def get(self, key, default=None):
        if key in self.settings:
            return self.settings[key]
        else:
            return None

    def load_settings(self):
        if not os.path.isfile(self.file_path):
            logger.info("Settings file doesn't exist.")
            return

        with open(self.file_path, 'r') as f:
            try:
                self.settings.update(json.load(f))
            except Exception as e:
                logger.error("Error loading settings file - " + str(e))
        logger.info("Settings loaded")

    def set(self, key, value, flush_file=True):
        logger.info(f"Setting: {key} - {value}")
        if key:
            self.settings[key] = value
        if flush_file:
            self.write_file()

    def write_file(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.settings, f, sort_keys=True, indent=4)
    


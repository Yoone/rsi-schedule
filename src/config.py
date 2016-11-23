from configparser import ConfigParser
import os


__all__ = ['CORE', 'OCR', 'ICAL']


config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.cfg'))

CORE = config['core']
OCR = config['ocr']
ICAL = config['ical']

from configparser import ConfigParser


__all__ = ['CORE', 'OCR', 'ICAL']


config = ConfigParser()
config.read('config.cfg')

CORE = config['core']
OCR = config['ocr']
ICAL = config['ical']

#!/usr/bin/env python3

from config import *
_activate_env = CORE.get('activate_env')
if _activate_env is not None:
    exec(compile(open(_activate_env, 'rb').read(), _activate_env, 'exec'), dict(__file__=_activate_env))

import sys
import os
from io import BytesIO
from configparser import ConfigParser
import hashlib
import logging

from crawler import get_images
from image import get_blocks
from ocr import get_text
from ical import create_ics


__all__ = ['mkschedule']


logger = logging.getLogger(__name__)


def md5file(fname):
    hash_md5 = hashlib.md5()
    with open(fname, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def update_image_data(meta):
    ini_file = os.path.splitext(meta['file'])[0] + '.ini'
    checksum = md5file(meta['file'])
    ini = ConfigParser()

    if os.path.isfile(ini_file):
        ini.read(ini_file)
        try:
            if ini['info']['checksum'] == checksum:
                return
        except KeyError:
            logger.error('Corrupted ini file')

    ini['info'] = {'checksum': checksum, 'name': meta['name']}
    ini['events'] = {}

    for i, block in enumerate(get_blocks(meta['file'])):
        bytes_out = BytesIO()
        block.save(bytes_out, format='PNG')
        bytes_out.seek(0)
        bfile = bytes_out.getvalue()
        bytes_out.close()
        ini['events']['e{}'.format(i)] = get_text(bfile)

    with open(ini_file, 'w') as f:
        ini.write(f)


def mkschedule(ics_dir='', img_dir=''):
    images = get_images(img_dir=img_dir)
    for meta in images:
        update_image_data(meta)

    events = {}
    for fname in os.listdir(img_dir):
        prefix, ext = os.path.splitext(fname)
        if ext != '.ini':
            continue

        ini = ConfigParser()
        ini.read(os.path.join(img_dir, prefix + '.ini'))
        try:
            name = ini['info']['name']
            events[name] = []
            for e in ini['events']:
                events[name].append(ini['events'][e])
        except KeyError as e:
            logger.error('Corrupted ini file')

    create_ics(events, ics_dir)


if __name__ == '__main__':
    argc = len(sys.argv)
    if argc >= 3:
        kw = {'level': logging.INFO, 'format': CORE['logging_format']}
        if argc >= 4:
            kw['filename'] = sys.argv[3]
        logging.basicConfig(**kw)

        logger.info('Start mkschedule')
        mkschedule(ics_dir=sys.argv[1], img_dir=sys.argv[2])
        logger.info('End mkschedule')
    else:
        print('Usage: {} ICS_DIR IMG_DIR [LOG_FILE]'.format(sys.argv[0]))

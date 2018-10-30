#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from configparser import ConfigParser
from datetime import datetime, timedelta
import logging
import sys

from ics import Calendar, Event
import requests


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))
config = ConfigParser()


def load_config(config_file):
    config.read(config_file)


def get_roadmap():
    logger.info('Get roadmap from %s', config['core']['roadmap_url'])
    result = requests.get(config['core']['roadmap_url'])
    result.raise_for_status()
    return result.json()['data']


def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)


def get_date_from_quarter(date_str):
    """
    Parse a string containing a date in quarter notation and extract a date. The date extracted is the end of the
    quarter. If mid is present, the date will be half of the middle month of the quarter.

    :param date_str: string matching one of the following: 'Q1 2019' or 'Mid Q4 2018' or 'Start of Q3 2018'.
    :return: date as datetime object
    """
    date_array = date_str.split(' ')
    year = int(date_array[-1])

    if len(date_array) > 2:
        if date_array[0] == 'Mid':
            q = date_array[1]
        else:
            q = date_array[2]
    else:
        q = date_array[0]

    if q == 'Q1':
        month = 3
    elif q == 'Q2':
        month = 6
    elif q == 'Q3':
        month = 9
    elif q == 'Q4':
        month = 12
    else:
        month = 1

    date_object = None
    if date_array[0] == 'Mid':
        date_object = datetime(year, month - 1, 15, 0, 0)
    elif date_array[0] == 'Start' and date_array[1] == 'of':
        date_object = datetime(year, month - 2, 15, 0, 0)
    else:
        date_object = last_day_of_month(datetime(year, month, 1, 0, 0))
    return date_object


def generate_description(cards):
    description = "Patch note:\n"
    for card in cards:
        description += "- %s: %s\n" % (card['name'], card['description'])
    return description


def parse_roadmap(roadmap):
    logger.info('Parse roadmap')
    events = []
    for release in roadmap['releases']:
        event = Event()
        if release['released']:
            begin_date = datetime.strptime(release['description'].split(' ', 1)[1], '%B %d, %Y')
        else:
            begin_date = get_date_from_quarter(release['description'])
        event.begin = begin_date
        event.make_all_day()
        event.name = 'Star Citizen %s release' % release['name']
        event.description = generate_description(release['cards'])
        events.append(event)
    return events


def create_ics(events):
    logger.info('Create ics file: %s', config['core']['ics_output'])
    calendar = Calendar()
    calendar.events = events
    with open(config['core']['ics_output'], 'w') as ics_file:
        ics_file.writelines(calendar)


def mkschedule():
    try:
        roadmap = get_roadmap()
    except requests.HTTPError as e:
        logger.error('Error while downloading the roadmap: %s', e)
        return
    except ValueError as e:
        logger.error('Error while extracting the roadmap: %s', e)
        return
    except KeyError as e:
        logger.error('Error while reading the roadmap: %s', e)
        return

    events = parse_roadmap(roadmap)
    create_ics(events)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="configuration file", type=str, dest="config_file", required=True)
    args = parser.parse_args()
    load_config(args.config_file)
    logger.info('Starting rsi-schedule')
    mkschedule()
    logger.info('End rsi-schedule')

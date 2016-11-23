from datetime import datetime, timedelta
import hashlib
import os
import re
import logging

from config import *


__all__ = ['create_ics']


logger = logging.getLogger(__name__)


def parse_event(s):
    lines = s.splitlines()
    if len(lines) != 2:
        logger.error('Wrong number of lines: {}'.format(lines))
        return

    name, duration = lines
    duration = duration.replace('.', '-').strip()
    reg = r'([A-Za-z]{3}\s*[0-9]{2}-?[0-9]{2}-?[0-9]{2})\s*-?\s*([A-Za-z]{3}\s*[0-9]{2}-?[0-9]{2}-?[0-9]{2})'
    matches = re.findall(reg, duration)
    if len(matches) == 0:
        logger.error('Dates are not formatted properly: {}'.format(duration))
        return
    dates = matches[0]

    return {
        'name': name.strip(),
        'date': datetime.strptime(dates[1], '%a %d-%m-%y').replace(hour=int(ICAL['event_start'])),
    }


def create_ics(events, ics_dir):
    cal = 'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//{}//NONSGML {}//EN\r\n'.format(CORE['company'], ICAL['name'])

    for sched_name in events:
        for event_str in events[sched_name]:
            e = parse_event(event_str)
            if e is None:
                continue

            cal += 'BEGIN:VEVENT\r\n'

            start_time = datetime.strftime(e['date'], '%Y%m%dT%H0000Z')
            end_time = datetime.strftime(e['date'] + timedelta(hours=int(ICAL['event_duration'])), '%Y%m%dT%H0000Z')
            cal += 'DTSTAMP:{}\r\n'.format(start_time)
            cal += 'DTSTART:{}\r\n'.format(start_time)
            cal += 'DTEND:{}\r\n'.format(end_time)

            summary = '{} - {}'.format(sched_name, e['name'])
            h = hashlib.md5()
            h.update(summary.encode())
            cal += 'UID:{}@{}\r\n'.format(h.hexdigest(), ICAL['uid_domain'])
            cal += 'SUMMARY:{}\r\n'.format(summary)

            cal += \
                'DESCRIPTION:({}) Work on "{}" should be finished '.format(sched_name, e['name']) + \
                '(remember that this is an estimate!)\\nMore info at: {}\\n\\n'.format(CORE['schedule_url']) + \
                'Brought to you by community website: {}\r\n'.format(CORE['website'])

            cal += 'END:VEVENT\r\n'

    cal += 'END:VCALENDAR\r\n'

    with open(os.path.join(ics_dir, 'rsi-schedule.ics'), 'w+') as f:
        f.write(cal)

rsi-schedule
============

Introduction
------------

Cloud Imperium Games released their [roadmap](https://robertsspaceindustries.com/roadmap/board/1-Star-Citizen) for Star
Citizen. You can now access it from calendars such as Google Calendar, Apple Calendar, Yahoo! Calendar, Microsoft 
Outlook, and many others.

This project consists in crawling the API from the public roadmap web page and parse it to generate an iCalendar file
(RFC 5545).

Requirements
------------

* [requests](https://github.com/requests/requests)
* [ics.py](https://github.com/C4ptainCrunch/ics.py)

Usage
-----

```
pipenv install
pipenv run rsi_schedule/schedule.py --config config.cfg
```

Contributors
------------

* [Yoone](https://github.com/yoone): Creator of the project
* [Chafouin](https://github.com/chafouin): Revamped project to use the roadmap API

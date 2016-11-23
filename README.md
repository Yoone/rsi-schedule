rsi-schedule
============

Introduction
------------

Cloud Imperium Games released their weekly-updated internal development schedule for Star Citizen. I thought it would be useful to access it from calendars such as Google Calendar, Apple Calendar, Yahoo! Calendar, Microsoft Outlook, and many others.

This project consists in crawling images from the public schedule web page, splitting them into blocks (representing tasks with their names and start/end dates) and feeding these blocks to an OCR in order to use the output text to generate an iCalendar file (RFC 5545).

Generated calendar can be accessed at: http://www.portolisar.com/

Requirements
------------

* `pip install -r requirements.txt`

Known issues
------------

* A short title (such as "UI") does not get translated by the OCR
* Bright background colors do not allow task blocks to be cut out properly
* The utilized OCR service is not _perfect_ but still yields better results than a properly trained `tesseract-ocr`

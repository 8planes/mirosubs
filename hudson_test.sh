#!/bin/bash
python manage.py test api auth comments messages profiles search statistic teams videos widget --settings=test_settings --with-coverage --with-xunit --with-xcoverage
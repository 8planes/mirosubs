#!/bin/bash
python manage.py test api auth comments messages profiles search statistic teams videos widget --settings=$1 --with-xunit

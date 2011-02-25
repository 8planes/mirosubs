#!/bin/bash
. ../env/bin/activate
python manage.py update_from_feed --settings=unisubs-settings
python manage.py send_notification --settings=unisubs-settings
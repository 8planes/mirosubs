#!/bin/bash
. /var/www/universalsubtitles.dev/env/bin/activate
python /var/www/universalsubtitles.dev/mirosubs/manage.py update_from_feed --settings=unisubs-settings
python /var/www/universalsubtitles.dev/mirosubs/manage.py send_notification --settings=unisubs-settings
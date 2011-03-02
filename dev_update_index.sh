#!/bin/bash
echo "Update search indexes..."
python /var/www/universalsubtitles.dev/mirosubs/manage.py update_index --settings=unisubs-settings
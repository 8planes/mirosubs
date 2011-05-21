#!/bin/bash

if [ -z "$1" ]; then
   echo "ERROR: No application home directory provided"
   exit 1
fi

apphome="$1"

. $apphome/env/bin/activate
python $apphome/mirosubs/manage.py update_from_feed --settings=unisubs_settings
# python $apphome/mirosubs/manage.py update_statistic --settings=unisubs_settings
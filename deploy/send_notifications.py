#!/usr/bin/env python                                                           

import subprocess

def send_notifications(suffix = ''):
    process = subprocess.Popen(
        ['../env/bin/python',
         'manage.py',
         'send_notification',
         '--settings=unisubs-settings'],
        cwd='/var/www/universalsubtitles{0}/mirosubs'.format(suffix))
    process.communicate()

send_notifications('.dev')
send_notifications('.staging')
send_notifications()

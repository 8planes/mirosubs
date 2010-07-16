#!/usr/bin/env/python

def send_notifications(suffix = ''):
    os.chdir('/var/www/universalsubtitles{0}'.format(suffix))
    subprocess.Popen('../env/bin/python manage.py send_notifications --settings=unisubs-settings')

send_notifications('.dev')
send_notifications('.staging')
send_notifications()

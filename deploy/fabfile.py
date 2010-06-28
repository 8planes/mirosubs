# Universal Subtitles, universalsubtitles.org
# 
# Copyright (C) 2010 Participatory Culture Foundation
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see 
# http://www.gnu.org/licenses/agpl-3.0.html.

from __future__ import with_statement
from fabric.api import run, put, sudo, env, cd, local
import os

def _create_env(username, installation_dir):
    env.hosts = ['universalsubtitles.org:2191']
    env.user = username
    env.base_dir = '/var/www/{0}'.format(installation_dir)

def staging(username):
    _create_env(username, 'universalsubtitles.staging')

def dev(username):
    _create_env(username, 'universalsubtitles.dev')

def unisubs(username):
    _create_env(username, 'universalsubtitles')

def set_permissions(home='/home/mirosubs'):
    """
    Make sure the web server has permission to write files into the
    upload directories.
    """
    # Note that 'fab staging set_permissions' won't work, because you need
    # to log in as a user with permission to use sudo. the mirosubs user does
    # not have that permission
    with cd(home):
        sudo('chgrp www-data -R mirosubs/media/')

def syncdb():
    with cd('{0}/mirosubs'.format(env.base_dir)):
        run('python manage.py syncdb --settings=unisubs-settings')

def migrate(app_name=''):
    with cd('{0}/mirosubs'.format(env.base_dir)):
        run('python manage.py migrate {0} --settings=unisubs-settings'.format(app_name))

def migrate_fake(app_name):
    """Unfortunately, one must do this when moving an app to South for the first time.
    
    See http://south.aeracode.org/docs/convertinganapp.html and
    http://south.aeracode.org/ticket/430 for more details. Perhaps this will be changed 
    in a subsequent version, but now we're stuck with this solution.
    """
    with cd('{0}/mirosubs'.format(env.base_dir)):
        run('python manage.py migrate {0} 0001 --fake --settings=unisubs-settings'.format(app_name))

def update_closure():
    pass

def update_environment():
    pass

def update():
    """
    Put the latest version of the code on the server and reload the app.
    """
    with cd('{0}/mirosubs'.format(env.base_dir)):
        run('git pull')
        env.warn_only = True
        run("find . -name '*.pyc' -print0 | xargs -0 rm")
        env.warn_only = False
        run('{0}/env/bin/python closure/compile.py'.format(env.base_dir))
        run('touch deploy/unisubs.wsgi')

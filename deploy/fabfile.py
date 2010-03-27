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

def _command(cmd):
    """Return a closure that holds the path and required args."""
    def f(arg):
        run("%s %s" % (cmd, arg))
    return f

def staging():
    """
    Run the subsequent commands on the staging server, e.g., li77-157.members.linode.com or 74.207.235.157
    """
    env.hosts = ['8planes.com']
    env.user = 'mirosubsstaging'
    env.production = False

def dev():
    env.hosts = ['8planes.com']
    env.user = 'mirosubsdev'
    env.production = False

def prod():
    env.hosts = ['pcf10.pculture.org:2191']
    env.user = 'adam'
    env.production = True

def setup_virtualenv(home='/home/mirosubs'):
    run('virtualenv --no-site-packages %s/env' % home)
    with cd(home):
        run('env/bin/easy_install -U setuptools')
        run('env/bin/easy_install pip')
        # use shell with pip to get PIP_DOWNLOAD_CACHE environment variable:
        run('env/bin/pip install -r mirosubs/deploy/dev-requirements.txt')
        run('ln -s /usr/lib/python2.5/site-packages/PIL env/lib/python2.5/site-packages/')

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

def reset_db():
    env.warn_only = True
    with cd('/home/{0}/mirosubs/'.format(env.user)):
        run(('/home/{0}/env/bin/python manage.py reset_db --noinput '
             '--settings={0}-settings').format(env.user))
        run(('/home/{0}/env/bin/python manage.py syncdb --noinput '
              '--settings={0}-settings').format(env.user))

def update():
    base_dir = '/var/www/universalsubtitles' if env.production else '/home/{0}'.format(env.user)
    """
    Put the latest version of the code on the server and reload the app.
    """
    with cd('{0}/mirosubs'.format(base_dir)):
        run('git pull origin master')
        env.warn_only = True
        run("find . -name '*.pyc' -print0 | xargs -0 rm")
        env.warn_only = False
        run('{0}/env/bin/python closure/compile.py'.format(base_dir))
        run('touch deploy/{0}.wsgi'.format(env.user))

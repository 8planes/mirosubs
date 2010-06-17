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
    Run the subsequent commands on the staging server, e.g., li77-157.members.linode.com 
    or 74.207.235.157
    """
    env.hosts = ['8planes.com']
    env.user = 'mirosubsstaging'
    env.base_dir = '/home/{0}'.format(env.user)

def dev():
    env.hosts = ['8planes.com']
    env.user = 'mirosubsdev'
    env.base_dir = '/home/{0}'.format(env.user)

def unisubs():
    env.hosts = ['universalsubtitles.org:2191']
    env.user = 'adam'
    env.base_dir = '/var/www/universalsubtitles'

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

def migrate(app_name):
    with cd('{0}/mirosubs'.format(env.base_dir)):
        run('python manage.py migrate {0}'.format(app_name))

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
        run('touch deploy/{0}.wsgi'.format(env.user))

def user_update(username):
    env.user = username
    env.base_dir = '/home/{0}'.format(env.user)
    this_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(this_dir, '..')
    exclude_file = os.path.join(this_dir, 'rsync-exclude.txt')
    local(("rsync -ave ssh {0} {1}@8planes.com:mirosubs "
           "--exclude-from '{2}'").format(
            base_dir, env.user, exclude_file))
    env.host_string = '8planes.com'
    with cd('{0}/mirosubs'.format(env.base_dir)):
        run('{0}/env/bin/python closure/compile.py'.format(env.base_dir))
        run('{0}/env/bin/python manage.py migrate'.format(env.base_dir))
        env.warn_only = True
        run("find . -name '*.pyc' -print0 | xargs -0 rm")
        env.warn_only = False
        run('touch deploy/{0}.wsgi'.format(env.user))

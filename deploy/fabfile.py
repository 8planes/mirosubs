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
    Run the subsequent commands on the staging server, e.g., li22-44.members.linode.com or 75.127.96.44
    """
    env.hosts = ['75.127.96.44:2222']
    env.user = 'mirosubs'

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
    # Note that 'fab highsite2 set_permissions' won't work, because you need
    # to log in as a user with permission to use sudo. the evolve user does
    # not have that permission
    with cd(home):
        sudo('chgrp www-data -R mirosubs/media/')

def reset_db():
    env.warn_only = True
    with cd('/home/mirosubs/mirosubs/'):
        run('/home/mirosubs/env/bin/python manage.py reset_db --noinput --settings=staging-settings')
        run('/home/mirosubs/env/bin/python manage.py syncdb --noinput --settings=staging-settings')

def update():
    """
    Put the latest version of the code on the server and reload the app.
    """
    with cd('/home/mirosubs/mirosubs'):
        run('git pull origin master')
        run('touch deploy/evolve.wsgi')

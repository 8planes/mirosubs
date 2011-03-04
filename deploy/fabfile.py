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
from fabric.context_managers import settings
import os

DEV_HOST = 'dev.universalsubtitles.org:2191'

def _create_env(username, hosts, s3_bucket, installation_dir, static_dir, name):
    env.user = username
    env.web_hosts = hosts
    env.hosts = []
    env.s3_bucket = s3_bucket
    env.web_dir = '/var/www/{0}'.format(installation_dir)
    env.static_dir = '/var/static/{0}'.format(static_dir)
    env.installation_name = name

def staging(username):
    _create_env(username, 
                ['pcf-us-staging1.pculture.org:2191', 
                 'pcf-us-staging2.pculture.org:2191'],
                's3.staging.universalsubtitles.org',
                'universalsubtitles.staging',
                'staging', 'staging')

def dev(username):
    _create_env(username,
                ['dev.universalsubtitles.org:2191'],
                None,
                'universalsubtitles.dev',
                'dev', 'dev')

def unisubs(username):
    _create_env(username,
                ['pcf10.pculture.org:2191', 
                 'pcf-us-cluster2.pculture.org:2191'],
                's3.www.universalsubtitles.org',
                'universalsubtitles',
                'production', None)


def syncdb():
    env.host_string = DEV_HOST
    with cd(os.path.join(env.static_dir, 'mirosubs')):
        run('{0}/env/bin/python manage.py syncdb --settings=unisubs-settings'.format(env.static_dir))

def migrate(app_name=''):
    env.host_string = DEV_HOST
    with cd(os.path.join(env.static_dir, 'mirosubs')):
        run('yes no | {0}/env/bin/python manage.py migrate {1} --settings=unisubs-settings'.format(
                env.static_dir, app_name))

def migrate_fake(app_name):
    """Unfortunately, one must do this when moving an app to South for the first time.
    
    See http://south.aeracode.org/docs/convertinganapp.html and
    http://south.aeracode.org/ticket/430 for more details. Perhaps this will be changed 
    in a subsequent version, but now we're stuck with this solution.
    """
    env.host_string = DEV_HOST
    with cd(os.path.join(env.static_dir, 'mirosubs')):
        run('yes no | {0}/env/bin/python manage.py migrate {1} 0001 --fake --settings=unisubs-settings'.format(env.static_dir, app_name))

def refresh_db():
    env.host_string = DEV_HOST
    sudo('/scripts/univsubs_reset_db.sh {0}'.format(env.installation_name))
    sudo('/scripts/univsubs_refresh_db.sh {0}'.format(env.installation_name))

def update_closure():
    # this happens so rarely, it's not really worth putting it here.
    pass

def _switch_branch(dir, branch_name):
    with cd(os.path.join(dir, 'mirosubs')):
        _git_pull()
        run('git fetch')
        # the following command will harmlessly fail if branch already exists.
        # don't be intimidated by the one-line message.
        env.warn_only = True
        run('git branch --track {0} origin/{0}'.format(branch_name))
        run('git checkout {0}'.format(branch_name))
        env.warn_only = False

def switch_branch(branch_name):
    for host in env.web_hosts:
        env.host_string = host
        _switch_branch(env.web_dir, branch_name)
    env.host_string = DEV_HOST
    _switch_branch(env.static_dir, branch_name)

def _update_environment(base_dir):
    with cd(os.path.join(base_dir, 'mirosubs', 'deploy')):
        _git_pull()
        run('export PIP_REQUIRE_VIRTUALENV=true')
        # see http://lincolnloop.com/blog/2010/jul/1/automated-no-prompt-deployment-pip/
        run('yes i | {0}/env/bin/pip install -E {0}/env/ -r requirements.txt'.format(base_dir), pty=True)

def update_environment():
    for host in env.web_hosts:
        env.host_string = host
        _update_environment(env.web_dir)
    env.host_string = DEV_HOST
    _update_environment(env.static_dir)

def _clear_permissions(dir):
    sudo('chgrp pcf-web -R {0}'.format(dir))
    sudo('chmod g+w -R {0}'.format(dir))

def clear_environment_permissions():
    for host in env.web_hosts:
        env.host_string = host
        _clear_permissions(os.path.join(env.web_dir, 'env'))
    env.host_string = DEV_HOST
    _clear_permissions(os.path.join(env.static_dir, 'env'))

def _git_pull():
    run('git pull')
    run('chgrp pcf-web -R .git 2> /dev/null; /bin/true')
    run('chmod g+w -R .git 2> /dev/null; /bin/true')

def add_disabled():
    for host in env.web_hosts:
        env.host_string = host
        run('touch {0}/mirosubs/disabled'.format(env.web_dir))

def remove_disabled():
    for host in env.web_hosts:
        env.host_string = host
        run('rm {0}/mirosubs/disabled'.format(env.web_dir))

def update_web():
    for host in env.web_hosts:
        env.host_string = host
        with cd('{0}/mirosubs'.format(env.web_dir)):
            python_exe = '{0}/env/bin/python'.format(env.web_dir)
            _git_pull()
            env.warn_only = True
            run("find . -name '*.pyc' -print0 | xargs -0 rm")
            env.warn_only = False
            run('{0} deploy/create_commit_file.py'.format(python_exe))
            run('touch deploy/unisubs.wsgi')

def _update_static(dir):
    with cd(os.path.join(dir, 'mirosubs')):
        media_dir = '{0}/mirosubs/media/'.format(dir)
        python_exe = '{0}/env/bin/python'.format(dir)
        _git_pull()
        run('{0} manage.py compile_config {1} --settings=unisubs-settings'.format(
                python_exe, media_dir))
        run('{0} manage.py compile_statwidgetconfig {1} --settings=unisubs-settings'.format(
                python_exe, media_dir))
        run('{0} closure/compile.py'.format(python_exe))
        run('{0} manage.py compile_embed {1} --settings=unisubs-settings'.format(
                python_exe, media_dir))

def update_static():
    env.host_string = DEV_HOST
    if env.s3_bucket is not None:
        _update_static(env.static_dir)
        media_dir = '{0}/mirosubs/media/'.format(env.static_dir)
        run('/usr/local/s3sync/s3sync.rb -r -p -v {0} {1}:'.format(
                media_dir, env.s3_bucket))
    else:
        _update_static(env.web_dir)
    

def update():
    update_web()
    update_static()

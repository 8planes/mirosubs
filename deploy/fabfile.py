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
import string
import random
import os

#:This environment is responsible for:
#:
#:- syncdb on all environment
#:- memechached and solr for `dev`
#:- media compilation on all environments
DEV_HOST = 'dev.universalsubtitles.org:2191'
#: Environment where celeryd and solr run for staging
#: - solr, celeryd and memcached for staging and production
ADMIN_HOST = 'pcf-us-admin.pculture.org:2191'

def _create_env(username, hosts, s3_bucket, 
                installation_dir, static_dir, name,
                memcached_bounce_cmd, 
                admin_dir, celeryd_host, celeryd_proj_root, 
                separate_uslogging_db=False,
                celeryd_bounce_cmd="",
                web_dir=None):
    env.user = username
    env.web_hosts = hosts
    env.hosts = []
    env.s3_bucket = s3_bucket
    env.web_dir = web_dir or '/var/www/{0}'.format(installation_dir)
    env.static_dir = static_dir 
    env.installation_name = name
    env.memcached_bounce_cmd = memcached_bounce_cmd
    env.admin_dir = admin_dir
    env.separate_uslogging_db = separate_uslogging_db
    env.celeryd_bounce_cmd=celeryd_bounce_cmd
    env.celeryd_host = celeryd_host
    env.celeryd_proj_root = celeryd_proj_root

def staging(username):
    _create_env(username              = username, 
                hosts                 = ['pcf-us-staging1.pculture.org:2191', 
                                        'pcf-us-staging2.pculture.org:2191'],
                s3_bucket             = 's3.staging.universalsubtitles.org',
                installation_dir      = 'universalsubtitles.staging',
                static_dir            = '/var/static/staging', 
                name                  = 'staging',
                memcached_bounce_cmd  = '/etc/init.d/memcached-staging restart',
                admin_dir             = '/usr/local/universalsubtitles.staging',
                celeryd_host          = ADMIN_HOST,
                celeryd_proj_root     = 'universalsubtitles.staging',
                separate_uslogging_db = True, 
                celeryd_bounce_cmd    = "/etc/init.d/celeryd.staging restart")

def dev(username):
    _create_env(username              = username,
                hosts                 = ['dev.universalsubtitles.org:2191'],
                s3_bucket             = None,
                installation_dir      = 'universalsubtitles.dev',
                static_dir            = '/var/www/universalsubtitles.dev', 
                name                  = 'dev', 
                memcached_bounce_cmd  = '/etc/init.d/memcached restart', 
                admin_dir             = None,
                celeryd_host          = DEV_HOST,
                celeryd_proj_root     = 'universalsubtitles.dev',
                separate_uslogging_db = False,
                celeryd_bounce_cmd    = "/etc/init.d/celeryd.dev restart")

def unisubs(username):
    _create_env(username              = username,
                hosts                 = ['pcf-us-cluster1.pculture.org:2191', 
                                        'pcf-us-cluster2.pculture.org:2191'],
                s3_bucket             = 's3.www.universalsubtitles.org',
                installation_dir      = 'universalsubtitles',
                static_dir            = 'static/production',
                name                  =  None,
                memcached_bounce_cmd  = '/etc/init.d/memcached restart', 
                admin_dir             = '/usr/local/universalsubtitles',
                celeryd_host          = ADMIN_HOST,
                celeryd_proj_root     = 'universalsubtitles',
                separate_uslogging_db = True, 
                celeryd_bounce_cmd    = "/etc/init.d/celeryd restart")


def syncdb():
    env.host_string = DEV_HOST
    with cd(os.path.join(env.static_dir, 'mirosubs')):
        _git_pull()
        run('{0}/env/bin/python manage.py syncdb '
            '--settings=unisubs_settings'.format(env.static_dir))
        if env.separate_uslogging_db:
            run('{0}/env/bin/python manage.py syncdb '
                '--database=uslogging --settings=unisubs_settings'.format(
                    env.static_dir))

def migrate(app_name=''):
    env.host_string = DEV_HOST
    with cd(os.path.join(env.static_dir, 'mirosubs')):
        _git_pull()
        if env.separate_uslogging_db:
            run('{0}/env/bin/python manage.py migrate sentry '
                '--database=uslogging --settings=unisubs_settings'.format(
                    env.static_dir))
            run('{0}/env/bin/python manage.py migrate uslogging '
                '--database=uslogging --settings=unisubs_settings'.format(
                    env.static_dir))
        run('yes no | {0}/env/bin/python manage.py migrate {1} --settings=unisubs_settings'.format(
                env.static_dir, app_name))

def run_command(command):
    env.host_string = DEV_HOST
    with cd(os.path.join(env.static_dir, 'mirosubs')):
        _git_pull()
        run('{0}/env/bin/python manage.py {1} '
            '--settings=unisubs_settings'.format(env.static_dir, command))

def migrate_fake(app_name):
    """Unfortunately, one must do this when moving an app to South for the first time.
    
    See http://south.aeracode.org/docs/convertinganapp.html and
    http://south.aeracode.org/ticket/430 for more details. Perhaps this will be changed 
    in a subsequent version, but now we're stuck with this solution.
    """
    env.host_string = DEV_HOST
    with cd(os.path.join(env.static_dir, 'mirosubs')):
        run('yes no | {0}/env/bin/python manage.py migrate {1} 0001 --fake --settings=unisubs_settings'.format(env.static_dir, app_name))

def refresh_db():
    env.host_string = env.web_hosts[0]
    sudo('/scripts/univsubs_reset_db.sh {0}'.format(env.installation_name))
    sudo('/scripts/univsubs_refresh_db.sh {0}'.format(env.installation_name))
    promote_django_admins()
    bounce_memcached()

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
        _git_pull()

def _execute_on_all_hosts(cmd):
    for host in env.web_hosts:
        env.host_string = host
        cmd(env.web_dir)
    env.host_string = DEV_HOST
    cmd(env.static_dir)
    if env.admin_dir is not None:
        env.host_string = ADMIN_HOST
        cmd(env.admin_dir)

def switch_branch(branch_name):
    _execute_on_all_hosts(lambda dir: _switch_branch(dir, branch_name))    

def _remove_pip_package(base_dir, package_name):
    with cd(os.path.join(base_dir, 'mirosubs', 'deploy')):
        run('yes y | {0}/env/bin/pip uninstall {1}'.format(base_dir, package_name), pty=True)

def remove_pip_package(package_egg_name):
    _execute_on_all_hosts(lambda dir: _remove_pip_package(dir, package_egg_name))

def _update_environment(base_dir):
    with cd(os.path.join(base_dir, 'mirosubs', 'deploy')):
        _git_pull()
        run('export PIP_REQUIRE_VIRTUALENV=true')
        # see http://lincolnloop.com/blog/2010/jul/1/automated-no-prompt-deployment-pip/
        run('yes i | {0}/env/bin/pip install -E {0}/env/ -r requirements.txt'.format(base_dir), pty=True)

def update_environment():
    _execute_on_all_hosts(lambda dir: _update_environment(dir))

def _clear_permissions(dir):
    sudo('chgrp pcf-web -R {0}'.format(dir))
    sudo('chmod g+w -R {0}'.format(dir))

def clear_environment_permissions():
    _execute_on_all_hosts(
        lambda dir: _clear_permissions(os.path.join(dir, 'env')))

def clear_permissions():
    for host in env.web_hosts:
        env.host_string = host
        _clear_permissions('{0}/mirosubs'.format(env.web_dir))

def _git_pull():
    run('git checkout --force')
    run('git pull --rebase')
    run('chgrp pcf-web -R .git 2> /dev/null; /bin/true')
    run('chmod g+w -R .git 2> /dev/null; /bin/true')
    _clear_permissions('.')

def _reload_app_server():
    """
    Reloading the app server will both make sure we have a
    valid commit guid (by running the create_commit_file)
    and also that we make the server reload code (currently
    with mod_wsgi this is touching the wsgi file)
    """
    with cd('{0}/mirosubs'.format(env.web_dir)):
        run('python deploy/create_commit_file.py')
        run('touch deploy/unisubs.wsgi')
    
def add_disabled():
    for host in env.web_hosts:
        env.host_string = host
        run('touch {0}/mirosubs/disabled'.format(env.web_dir))

def remove_disabled():
    for host in env.web_hosts:
        env.host_string = host
        run('rm {0}/mirosubs/disabled'.format(env.web_dir))

def update_web():
    """
    This is how code gets reloaded:

    - Checkout code on the auxiliary server ADMIN whost
    - Checkout the latest code on all appservers
    - Remove all pyc files from app servers
    - Bounce celeryd, memcached , test services
    - Reload app code (touch wsgi file)

    Until we implement the checking out code to an isolated dir
    any failure on these steps need to be fixed or will result in
    breakage
    """
    if env.admin_dir is not None:
        env.host_string = ADMIN_HOST
        with cd(os.path.join(env.admin_dir, 'mirosubs')):
            _git_pull()
    for host in env.web_hosts:
        env.host_string = host
        with cd('{0}/mirosubs'.format(env.web_dir)):
            python_exe = '{0}/env/bin/python'.format(env.web_dir)
            _git_pull()
            env.warn_only = True
            run("find . -name '*.pyc' -print0 | xargs -0 rm")
            env.warn_only = False
    _bounce_celeryd()
    bounce_memcached()
    test_services()
    for host in env.web_hosts:
        _reload_app_server()

def bounce_memcached():
    """
    Purges old data from memcached should be done by the end of each deploy
    """
    if env.admin_dir:
        env.host_string = ADMIN_HOST
    else:
        env.host_string = DEV_HOST
    sudo(env.memcached_bounce_cmd)

def update_solr_schema():
    if env.admin_dir:
        # staging and production
        env.host_string = ADMIN_HOST
        dir = env.admin_dir
        python_exe = '{0}/env/bin/python'.format(env.admin_dir)
        with cd(os.path.join(dir, 'mirosubs')):
            _git_pull()
            run('{0} manage.py build_solr_schema --settings=unisubs_settings > /etc/solr/conf/{1}/conf/schema.xml'.format(
                    python_exe, 
                    'production' if env.installation_name is None else 'staging'))
            sudo('service tomcat6 restart')
            run('yes y | {0} manage.py rebuild_index --settings=unisubs_settings'.format(python_exe))
    else:
        # dev
        env.host_string = DEV_HOST
        dir = env.web_dir
        python_exe = '{0}/env/bin/python'.format(env.web_dir)
        with cd(os.path.join(dir, 'mirosubs')):
            _git_pull()
            run('{0} manage.py build_solr_schema --settings=unisubs_settings > /etc/solr/conf/main/conf/schema.xml'.format(python_exe))
            run('{0} manage.py build_solr_schema --settings=unisubs_settings > /etc/solr/conf/testing/conf/schema.xml'.format(python_exe))
            sudo('service tomcat6 restart')
            run('screen -d -m "yes y | {0} manage.py rebuild_index --settings=unisubs_settings"'.format(python_exe))

def _bounce_celeryd():
    if env.admin_dir:
        env.host_string = ADMIN_HOST
    else:
        env.host_string = DEV_HOST
    if bool(env.celeryd_bounce_cmd):
        sudo(env.celeryd_bounce_cmd)

def _update_static(dir):
    with cd(os.path.join(dir, 'mirosubs')):
        media_dir = '{0}/mirosubs/media/'.format(dir)
        python_exe = '{0}/env/bin/python'.format(dir)
        _git_pull()
        # this has to be here, since the environment that compiles media is not an app server
        # so there is no guarantee we we'll have run the create_commit command
        run('{0} deploy/create_commit_file.py'.format(python_exe))
        run('{0} manage.py compile_config {1} --settings=unisubs_settings'.format(
                python_exe, media_dir))
        run('{0} manage.py compile_statwidgetconfig {1} --settings=unisubs_settings'.format(
                python_exe, media_dir))
        run('{0} manage.py compile_embed {1} --settings=unisubs_settings'.format(
                python_exe, media_dir))
        # we need to remove whatever was left on static-cache
        static_cache_path = "./media/static-cache/*"
        _clear_permissions(media_dir)
        
        
        run('{0} manage.py  compile_media --settings=unisubs_settings'.format(python_exe))
        
def update_static():
    env.host_string = DEV_HOST
    if env.s3_bucket is not None:
        with cd(os.path.join(env.static_dir, 'mirosubs')):
            _update_static(env.static_dir)
            media_dir = '{0}/mirosubs/media/'.format(env.static_dir)
            python_exe = '{0}/env/bin/python'.format(env.static_dir)
            run('{0} manage.py  send_to_s3 --settings=unisubs_settings'.format(python_exe))
    else:
        _update_static(env.web_dir)

def update():
    update_static()
    update_web()

def _promote_django_admins(dir, email=None, new_password=None, userlist_path=None):
    with cd(os.path.join(dir, 'mirosubs')):
        python_exe = '{0}/env/bin/python'.format(dir)
        args = ""
        if email is not None:
            args += "--email=%s" % (email)
        if new_password is not None:
            args += "--pass=%s" % (new_password)
        if userlist_path is not None:
            args += "--userlist-path=%s" % (userlist_path)    
        cmd_str ='{0} manage.py promote_admins {1} --settings=unisubs_settings'.format(python_exe, args)
        run(cmd_str)

def promote_django_admins(email=None, new_password=None, userlist_path=None):
    """
    Make sure identified users are can access the admin site.
    If new_password is provided will reset the user's password
    You can pass either one user email, or a path to a json file with
    'email', 'new_password' objects.

    Examples:
    fab staging:serveruser promote_django_admins:email=arthur@example.com
    """
    env.host_string = env.web_hosts[0]
    return _promote_django_admins(env.web_dir, email, new_password, userlist_path)

def update_translations():
    """
    What it does:
    
    - Pushes new strings in english and new languages to transifex.
    - Pulls all changes from transifex, for all languages
    - Adds only the *.mo and *.po files to the index area
    - Commits to the rep with a predefined message
    - Pushes to origon.

    Caveats:
    
    - If any of these steps fail, it will stop execution
    - At some point, this is pretty much about syncing two reps, so conflicts can appear
    - This assumes that we do not edit translation .po files on the file system.
    - This assumes that we want to push with a "git push".
    - You must have the  .transifexrc file into your home (this has auth credentials is stored outside of source control)
    """
    run ('cd {0} && sh update_translations.sh'.format(os.path.dirname(__file__)))

def test_celeryd():
    print '=== TEST CELERYD SCHEDULLER ==='
    env.host_string = env.celeryd_host
    output = run('ps aux | grep "%s/mirosubs/manage\.py.*celeryd.*-B" | grep -v grep' % env.celeryd_proj_root)
    assert len(output.split('\n'))

def test_services():
    test_memcached()
    test_celeryd()
    print '=== TEST SERVICES ==='
    for host in env.web_hosts:
        env.host_string = host    
        with cd(os.path.join(env.web_dir, 'mirosubs')):
            run('{0}/env/bin/python manage.py test_services --settings=unisubs_settings'.format(
                env.web_dir))

def test_memcached():
    print '=== TEST MEMCACHED ==='
    alphanum = string.letters+string.digits
    host_set = set(env.web_hosts)
    for host in host_set:
        random_string = ''.join(
            [alphanum[random.randint(0, len(alphanum)-1)] 
             for i in xrange(12)])
        env.host_string = host
        with cd(os.path.join(env.web_dir, 'mirosubs')):
            run('{0}/env/bin/python manage.py set_memcached {1} --settings=unisubs_settings'.format(
                env.web_dir,
                random_string))
        other_hosts = host_set - set([host])
        for other_host in other_hosts:
            env.host_string = host
            output = ''
            with cd(os.path.join(env.web_dir, 'mirosubs')):
                output = run('{0}/env/bin/python manage.py get_memcached --settings=unisubs_settings'.format(
                    env.web_dir))
            if output.find(random_string) == -1:
                raise Exception('Machines {0} and {1} are using different memcached instances'.format(
                        host, other_host))

def generate_docs():
    env.host_string = DEV_HOST
    with cd(os.path.join(env.static_dir, 'mirosubs')):
        python_exe = '{0}/env/bin/python'.format(env.static_dir)
        run('{0} manage.py  sphinx-build docs/ media/docs --settings=unisubs_settings'.format(python_exe))
    
try:
    from local_env import *
    def local (username):
        _create_env(**local_env_data)

except ImportError:
    pass 


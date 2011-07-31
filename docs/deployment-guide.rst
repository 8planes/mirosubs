================
Deployment Guide
================


Update unisubs-settings.py if necessary *::

    fab <server> add_disabled
    fab <server> switch_branch:<branch_name>
    fab <server> update_environment
    fab <server> syncdb
    fab <server> migrate_fake:<app_name>
    fab <server> migrate
    fab <server> update
    fab <server> bounce_memcached
    fab <server> remove_disabled

open ssh session and run::

    $manage.py/ build_solr_schema --settings=unisubs_settings > /etc/solr/conf/production/conf/schema.xml # 20 seconds
    $python manage.py update_index --settings=unisubs_settings --verbosity=2 # ~1 hours


for staging::

    fab staging:<username> refresh_db
    fab staging:<username> switch_branch:<branch_name>
    fab staging:<username> clear_environment_permissions
    fab staging:<username> update_environment
    fab staging:<username> syncdb
    fab <server> migrate_fake:<app_name>
    fab <server> migrate
    fab <server> update



================
Deployment Guide
================


The basic sequence:

    fab <server> add_disabled
    fab <server> switch_branch:<branch_name>
    fab <server> update_environment
    fab <server> syncdb
    fab <server> migrate_fake:<app_name> # if we converted an app to south, pretty rare
    fab <server> migrate
    fab <server> update
    fab <server> remove_disabled
    # if and only if we have updates to sole indexes
    fab <server> update_solr_schema

Things to keep in mind:
    - Rebuilding the solr index is pretty slow, so it will run on a screen session, if you need to check it, just logge back to the server and open it on screen


.. automodule:: deploy.fabfile
    :members:

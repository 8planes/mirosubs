#!/bin/bash

python manage.py build_solr_schema > /usr/lib/apache-solr/example/solr/conf/schema.xml
launchctl stop org.apache.Solr
launchctl start org.apache.Solr
python manage.py rebuild_index
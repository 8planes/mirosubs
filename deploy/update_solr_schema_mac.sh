#!/bin/bash

python manage.py build_solr_schema > /usr/lib/apache-solr/example/multicore/core0/conf/schema.xml
python manage.py build_solr_schema > /usr/lib/apache-solr/example/multicore/core1/conf/schema.xml
launchctl stop org.apache.Solr
launchctl start org.apache.Solr
python manage.py rebuild_index --settings=dev_settings

#!/bin/bash

python manage.py build_solr_schema > /etc/solr/conf/main/conf/schema.xml
python manage.py build_solr_schema > /etc/solr/conf/testing/conf/schema.xml
service tomcat6 restart
python manage.py rebuild_index --settings=unisubs_settings

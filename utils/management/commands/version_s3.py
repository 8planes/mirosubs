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

from django.core.management.base import BaseCommand
from sentry.models import Message, GroupedMessage, FilterValue
import datetime
from storages.backends import s3boto
try:
    from boto.s3 import Key
except:
    from boto.s3 import key
    Key = key.Key


KEY_NAME = "boto-test.txt"

class Command(BaseCommand):
    
    def get_bucket(self):
        storage = s3boto.S3BotoStorage()
        return storage.bucket

    def enable_versioning(self):
        self.bucket.configure_versioning(True)

    def pause_versioning(self):
        self.bucket.configure_versioning(False)

    def upload_test_file(self):
        key =  Key(name=KEY_NAME, bucket=self.bucket)
        key.set_contents_from_string( str(datetime.datetime.now()))
        

    def get_versioning_status(self):
        print self.bucket.get_versioning_status()
        self.upload_test_file()
        versions =  [x for x  in self.bucket.list_versions(KEY_NAME)]
        print "%s versions" % len(versions)
        print "version ids" , versions

    def handle(self, *args, **kwargs):
        self.bucket = self.get_bucket()
        if args and args[0] == "true":
            self.enable_versioning()
        elif args and args[0] == "false":
            self.pause_versioning()
        print "versioning status: %s"  % self.get_versioning_status()

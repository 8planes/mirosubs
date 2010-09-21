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

#  Based on: http://www.djangosnippets.org/snippets/73/
#
#  Modified by Sean Reifschneider to be smarter about surrounding page
#  link context.  For usage documentation see:
#
#     http://www.tummy.com/Community/Articles/django-pagination/
from mimetypes import guess_type
import os

from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import Storage
from django.core.files import File
from django.utils.functional import curry
from django.conf import settings
from django.core.files.storage import default_storage

ACCESS_KEY_NAME = 'AWS_ACCESS_KEY_ID'
SECRET_KEY_NAME = 'AWS_SECRET_ACCESS_KEY'

from utils.amazon.S3 import AWSAuthConnection, QueryStringAuthGenerator, CallingFormat

class S3Storage(Storage):
    """Amazon Simple Storage Service"""

    def __init__(self, bucket=settings.AWS_STORAGE_BUCKET_NAME, 
            access_key=None, secret_key=None, acl='public-read', 
            calling_format=CallingFormat.SUBDOMAIN):
        self.bucket = bucket
        self.acl = acl

        if not access_key and not secret_key:
             access_key, secret_key = self._get_access_keys()

        self.connection = AWSAuthConnection(access_key, secret_key, 
                            calling_format=calling_format)
        self.generator = QueryStringAuthGenerator(access_key, secret_key, 
                            calling_format=calling_format, is_secure=False)
        
        #print self.connection.check_bucket_exists(self.bucket).read()
        #if not self.connection.check_bucket_exists(self.bucket):
        self.connection.create_bucket(self.bucket)
         
    def _get_access_keys(self):
        access_key = getattr(settings, ACCESS_KEY_NAME, None)
        secret_key = getattr(settings, SECRET_KEY_NAME, None)

        if access_key and secret_key:
            # Both were provided, so use them
            return access_key, secret_key

        return None, None

    def _get_connection(self):
        return AWSAuthConnection(*self._get_access_keys())

    def _put_file(self, filename, raw_contents):
        content_type = guess_type(filename)[0] or "application/x-octet-stream"
        headers = {'x-amz-acl':  self.acl, 'Content-Type': content_type}
        response = self.connection.put(self.bucket, filename, raw_contents, headers)
        
    def url(self, filename):
        return self.generator.make_bare_url(self.bucket, filename)

    def filesize(self, filename):
        response = self.connection._make_request('HEAD', self.bucket, filename)
        return int(response.getheader('Content-Length'))

    def open(self, filename, mode='rb'):
        response = self.connection.get(self.bucket, filename)
        writer = curry(self._put_file, filename)
        return File(response.object.data)

    def exists(self, filename):
        response = self.connection._make_request('HEAD', self.bucket, filename)
        return response.status == 200

    def save(self, filename, raw_contents):
        filename = self.get_available_filename(filename)
        self._put_file(filename, raw_contents)
        return filename

    def delete(self, filename):
        self.connection.delete(self.bucket, filename)

    def get_available_filename(self, filename):
        """ Overwrite existing file with the same name. """
        return filename
    
if not getattr(settings, ACCESS_KEY_NAME, None) and not getattr(settings, SECRET_KEY_NAME, None):
    default_image_storage = default_storage
else:
    default_image_storage = S3Storage()
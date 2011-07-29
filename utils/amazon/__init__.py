# ########################################################
# S3FileField.py
# Extended FileField and ImageField for use with Django and Boto.
#
# Required settings:
#    USE_AMAZON_S3 - Boolean, self explanatory
#    DEFAULT_BUCKET - String, represents the default bucket name to use if one isn't provided
#    AWS_ACCESS_KEY_ID - String
#    AWS_SECRET_ACCESS_KEY - String
#
# ########################################################

from django.db import models
from django.conf import settings
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.exception import BotoClientError, BotoServerError
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from fields import S3EnabledImageField, S3EnabledFileField
from django.core.mail import mail_admins
from sentry.client.models import client
import os

__all__ = ['S3EnabledImageField', 'S3EnabledFileField', 'S3Storage']

DEFAULT_HOST = 's3.amazonaws.com'

class S3StorageError(Exception):
    pass

class S3Storage(FileSystemStorage):
    def __init__(self, bucket=None, location=None, base_url=None):
        if bucket is None:
            connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            if not connection.lookup(settings.DEFAULT_BUCKET):
                self.connection.create_bucket(settings.DEFAULT_BUCKET)
            bucket = connection.get_bucket(settings.DEFAULT_BUCKET)
        if location is None:
            location = settings.MEDIA_ROOT
        if base_url is None:
            base_url = settings.MEDIA_URL
        self.location = os.path.abspath(location)
        self.bucket = bucket
        self.base_url = base_url

    def _open(self, name, mode='rb'):
        class S3File(File):
            def __init__(self, key):
                self.key = key
            
            def size(self):
                return self.key.size
            
            def read(self, *args, **kwargs):
                return self.key.read(*args, **kwargs)
            
            def write(self, content):
                self.key.set_contents_from_string(content)
            
            def close(self):
                self.key.close()  
        return S3File(Key(self.bucket, name))

    def _save(self, name, content):
        name = name.replace('\\', '/')
        key = Key(self.bucket, name)
        try:
            if hasattr(content, 'temporary_file_path'):
                key.set_contents_from_filename(content.temporary_file_path())
            elif isinstance(content, File):
                key.set_contents_from_file(content)
            else:
                key.set_contents_from_string(content)
            key.make_public()
            return name
        except (BotoClientError, BotoServerError), e:
            client.create_from_exception()
            raise S3StorageError(*e.args)

    def _get_traceback(self):
        "Helper function to return the traceback as a string"
        import traceback, sys
        return '\n'.join(traceback.format_exception(*sys.exc_info()))

    def delete(self, name):
        if name and self.exists(name):
            self.bucket.delete_key(name)

    def exists(self, name):
        return Key(self.bucket, name).exists()

    def listdir(self, path):
        return [key.name for key in self.bucket.list()]

    def path(self, name):
        raise NotImplementedError

    def size(self, name):
        return self.bucket.get_key(name).size
    
    def url(self, name):
        name = name.replace('\\', '/')
        return 'http://%s.%s/%s' % (self.bucket.name, DEFAULT_HOST, name)
        #return Key(self.bucket, name).generate_url(100000)
    
    def get_available_name(self, name):
        return name
    
    @classmethod
    def create_default_storage(cls):
        if settings.USE_AMAZON_S3:
            connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)

            if not connection.lookup(settings.DEFAULT_BUCKET):
                connection.create_bucket(settings.DEFAULT_BUCKET)
            bucket = connection.get_bucket(settings.DEFAULT_BUCKET)
            return S3Storage(bucket)

default_s3_store = S3Storage.create_default_storage()
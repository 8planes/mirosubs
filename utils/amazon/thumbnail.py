from sorl.thumbnail.main import DjangoThumbnail, get_thumbnail_setting
from sorl.thumbnail.base import ThumbnailException
from os.path import isfile, isdir, getmtime, dirname, splitext, getsize
import os
from django.conf import settings
from utils.files_storages import S3Storage
from django.conf import settings
from django.utils.encoding import iri_to_uri, force_unicode

from sorl.thumbnail.base import Thumbnail
from sorl.thumbnail.processors import dynamic_import
from sorl.thumbnail import defaults

class AmazonThumbnail(DjangoThumbnail):

    def __init__(self, relative_source, requested_size, opts=None,
                 quality=None, basedir=None, subdir=None, prefix=None,
                 relative_dest=None, processors=None, extension=None):
        relative_source = force_unicode(relative_source)
        # Set the absolute filename for the source file
        source = self._absolute_path(relative_source)

        quality = get_thumbnail_setting('QUALITY', quality)
        convert_path = get_thumbnail_setting('CONVERT')
        wvps_path = get_thumbnail_setting('WVPS')
        if processors is None:
            processors = dynamic_import(get_thumbnail_setting('PROCESSORS'))

        # Call super().__init__ now to set the opts attribute. generate() won't
        # get called because we are not setting the dest attribute yet.
        super(DjangoThumbnail, self).__init__(source, requested_size,
            opts=opts, quality=quality, convert_path=convert_path,
            wvps_path=wvps_path, processors=processors)

        # Get the relative filename for the thumbnail image, then set the
        # destination filename
        if relative_dest is None:
            relative_dest = \
               self._get_relative_thumbnail(relative_source, basedir=basedir,
                                            subdir=subdir, prefix=prefix,
                                            extension=extension)
        filelike = not isinstance(relative_dest, basestring)
        if filelike:
            self.dest = relative_dest
        else:
            self.dest = self._absolute_path(relative_dest)
        self.relative_dest = relative_dest
        # Call generate now that the dest attribute has been set
        self.generate()

        # Set the relative & absolute url to the thumbnail
        if not filelike:
            self.relative_url = \
                iri_to_uri('/'.join(relative_dest.split(os.sep)))
            self.absolute_url = '%s%s' % (settings.MEDIA_URL,
                                          self.relative_url)
    
    def generate(self):
        """
        Generates the thumbnail if it doesn't exist or if the file date of the
        source file is newer than that of the thumbnail.
        """
        # Ensure dest(ination) attribute is set
        if not self.dest:
            raise ThumbnailException("No destination filename set.")
        
        new_generated = False

        if not isinstance(self.dest, basestring):
            # We'll assume dest is a file-like instance if it exists but isn't
            # a string.
            self._do_generate()
            new_generated = True
            
        elif not isfile(self.dest) or (self.source_exists and
            getmtime(self.source) > getmtime(self.dest)):
            
            if is_on_s3(self.relative_dest):
                 # "thumb is on s3"
                pull_from_s3(self.relative_dest)
                self._source_exists = True
            else:
                 # "thumb not on s3"
                if self.source_exists:
                    # Ensure the directory exists
                    directory = dirname(self.dest)
                    if not isdir(directory):
                        os.makedirs(directory)
    
                    self._do_generate()
                    new_generated = True                  
                else:
                    # file's missing.
                    print self.relative_source
                    if is_on_s3(self.relative_source):
                        pull_from_s3(self.relative_source)
                        self._source_exists = True
                    else:
                         # "source is not on S3!"
                        self._source_exists = False
    

    
        if new_generated:
            push_to_s3(self.dest)

    def _get_relative_source(self):
        # Hack.
        try:
            start_str = self.relative_dest[:7]
            return self.source[self.source.find(start_str):]
        except:
            return self.source
    relative_source = property(_get_relative_source)


def push_to_s3(file_path):
    s3_storage = S3Storage()
    img_file = open("%s%s" % (settings.MEDIA_ROOT,file_path),'r')    
    s3_storage.save(file_path.split('/')[-1], img_file.read())
    img_file.close()

def is_on_s3(file_path):
    s3_storage = S3Storage() 
    return s3_storage.exists(file_path)
    
def pull_from_s3(file_path):
    s3_storage = S3Storage()     
    img_file = open("%s%s" % (settings.MEDIA_ROOT,file_path),'w')
    s3_img_file = s3_storage.open(file_path)
    print s3_img_file
    img_file.write(s3_img_file.read())
    s3_img_file.close()
    img_file.close()
    
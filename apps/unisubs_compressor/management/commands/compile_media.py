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

from django.conf import settings

from django.core.management.base import BaseCommand
import os, hashlib
import subprocess

def call_command(command):
    process = subprocess.Popen( command.split(' '),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return process.communicate()

class Command(BaseCommand):

    def compile_media_bundle(self, bundle_name, bundle_type, files):
        file_list = [os.path.join(settings.MEDIA_ROOT, x) for x in files]
        for f in file_list:
            open(f).read()
        buffer = [open(f).read() for f in file_list]
        concatenated_path =  os.path.join(settings.MEDIA_ROOT, settings.COMPRESS_OUTPUT_DIRNAME, "%s.%s" % (bundle_name, bundle_type))
        out = open(concatenated_path, 'w')
        out.write("".join(buffer))
        out.close()
        yui_command = "%s --type=%s %s" % (settings.COMPRESS_YUI_BINARY, bundle_type, concatenated_path)

        compiled_css, err_data  = call_command(yui_command)
        checksum = hashlib.md5(compiled_css).hexdigest()
        # store files media_root + cache_set + checksum
        filename = "%s.css" % ( checksum)
        out_path = os.path.join(settings.MEDIA_ROOT, settings.COMPRESS_OUTPUT_DIRNAME, filename)
        out = open(out_path, 'w')
        out.write(compiled_css)
        out.close()
        os.remove(concatenated_path)
        return  filename


    def handle(self, *args, **kwargs):
        os.chdir(settings.PROJECT_ROOT)
        bundles = settings.MEDIA_BUNDLES
        output_dir = os.path.join(settings.MEDIA_ROOT, settings.COMPRESS_OUTPUT_DIRNAME)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        for filename in os.listdir(output_dir):
            os.remove(os.path.join(output_dir, filename))
        
        buffer = []
        for bundle_name, data in bundles.items():
            checksum = self.compile_media_bundle(
                bundle_name,
                data['type'],
                data["files"])
            buffer.append("'%s' : '%s'," % (bundle_name, checksum))
        open(os.path.join(output_dir, "compresses.py"), 'w').write("MEDIA_BUNDLE_URLS = {%s}" % "\n".join(buffer))
                    
        
        

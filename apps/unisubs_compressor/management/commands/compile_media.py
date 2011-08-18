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

import sys, os, shutil, subprocess, logging, time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

import optparse

from deploy.git_helpers import get_current_commit_hash

from apps import widget

LAST_COMMIT_GUID = get_current_commit_hash()

def _make_version_debug_string():
    """
    See Command._append_verion_for_debug

    We have this as an external function because we need this on compilation and testing deployment
    """
    return '/*mirosubs.static_version="%s"*/' % LAST_COMMIT_GUID
    



logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
MEDIA_ROOT = settings.MEDIA_ROOT
def to_media_root(*paths):
    return os.path.join(settings.MEDIA_ROOT, *paths)
JS_LIB = os.path.join(settings.PROJECT_ROOT, "media")
CLOSURE_LIB = os.path.join(JS_LIB, "js", "closure-library")
FLOWPLAYER_JS = os.path.join(settings.PROJECT_ROOT, "media/flowplayer/flowplayer-3.2.2.min.js")
COMPILER_PATH = os.path.join(settings.PROJECT_ROOT,  "closure", "compiler.jar")

DIRS_TO_COMPILE = []
SKIP_COPING_ON = DIRS_TO_COMPILE + [
    "videos",
    "*closure-lib*" ,
    settings.COMPRESS_OUTPUT_DIRNAME,
    "teams",
     ]

NO_UNIQUE_URL = (
    #"js/embed.js", -> embed is actually a dinamic url
    "js/mirosubs-widgetizer.js",
    "js/mirosubs-widgetizer-debug.js",
    "js/mirosubs-widgetizer-sumo.js",
    "js/mirosubs-extension.js",
    "js/mirosubs-statwidget.js",
    "js/mirosubs-api.js",
    "js/mirosubs-offsite-compiled.js",
    "js/widgetizer/widgetizerprimer.js",
)

def call_command(command):
    process = subprocess.Popen( command.split(' '),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return process.communicate()

def get_cache_dir():
    return os.path.join(settings.MEDIA_ROOT, settings.COMPRESS_OUTPUT_DIRNAME, LAST_COMMIT_GUID)

def get_cache_base_url():
    return "%s%s/%s" % (settings.MEDIA_URL_BASE, settings.COMPRESS_OUTPUT_DIRNAME, LAST_COMMIT_GUID)



def sorted_ls(path):
    """
    Returns contents of dir from older to newer
    """
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))

class Command(BaseCommand):




    help = 'Compiles all bundles in settings.py (css and js).'
    args = 'media_bundles'

    option_list = BaseCommand.option_list + (

        optparse.make_option('--checks-version',
            action='store_true', dest='test_str_version', default=True,
            help="Check that we outputed the version string for comopiled files."),


        optparse.make_option('--keeps-previous',
            action='store_true', dest='keeps_previous', default=False,
            help="Will remove older static media builds."),
        )

    def create_cache_dir(self):
        commit_hash = settings.LAST_COMMIT_GUID.split("/")[1]
        temp = os.path.join("/tmp", "static-%s-%s" % (commit_hash, time.time()))
        os.makedirs(temp)

        return temp

    
    def _append_version_for_debug(self, descriptor, file_type):
        """
        We append the /*mirosubs.static_version="{{commit guid}"*/ to the end of the
        file so we can debug, be sure we have the correct version of media.

        Arguments:
        `descriptor` : the fd to append to
        `file_type` : if it's a js or html or css file - we currently only support js and css
            """
        descriptor.write(_make_version_debug_string())
        
    def compile_css_bundle(self, bundle_name, bundle_type, files):
        file_list = [os.path.join(settings.MEDIA_ROOT, x) for x in files]
        for f in file_list:
            open(f).read()
        buffer = [open(f).read() for f in file_list]
        dir_path = os.path.join(self.base_dir, "css-compressed")
        if os.path.exists(dir_path) is False:
            os.mkdir(dir_path)
        concatenated_path =  os.path.join(dir_path, "%s.%s" % (bundle_name, bundle_type))
        out = open(concatenated_path, 'w')
        out.write("".join(buffer))        
        out.close()
        if bundle_type == "css":
            filename = "%s.css" % ( bundle_name)
            cmd_str = "%s --type=%s %s" % (settings.COMPRESS_YUI_BINARY, bundle_type, concatenated_path)
        if self.verbosity > 1:
            logging.info( "calling %s" % cmd_str)
        output, err_data  = call_command(cmd_str)

            
        out = open(concatenated_path, 'w')
        out.write(output)
        self._append_version_for_debug(out, "css")
        out.close()
        #os.remove(concatenated_path)
        return  filename

    def compile_js_bundle(self, bundle_name, bundle_type, files):
        output_file_name = "%s.js" % bundle_name
        bundle_settings = settings.MEDIA_BUNDLES[bundle_name]
        debug = bundle_settings.get("debug", False)
        extra_defines = bundle_settings.get("extra_defines", None)
        include_flash_deps = bundle_settings.get("include_flash_deps", True)
        closure_dep_file = bundle_settings.get("closure_deps",'js/closure-dependencies.js' )
        optimization_type = bundle_settings.get("optimizations", "ADVANCED_OPTIMIZATIONS")

        logging.info("Starting {0}".format(output_file_name))

        deps = [" --js %s " % os.path.join(JS_LIB, file) for file in files]
        calcdeps_js = os.path.join(JS_LIB, 'js', 'mirosubs-calcdeps.js')
        compiled_js = os.path.join(self.base_dir, "js" , output_file_name)
        if not os.path.exists(os.path.dirname(compiled_js)):
            os.makedirs(os.path.dirname(compiled_js))
        compiler_jar = COMPILER_PATH

        logging.info("Calculating closure dependencies")

        js_debug_dep_file = ''
        if debug:
            js_debug_dep_file = '-i {0}/{1}'.format(JS_LIB, 'js/closure-debug-dependencies.js')

        cmd_str = "%s/closure/bin/calcdeps.py -i %s/%s %s -p %s/ -o script"  % (
            CLOSURE_LIB,
            JS_LIB,
            closure_dep_file, 
            js_debug_dep_file,
            CLOSURE_LIB)
        if self.verbosity > 1:
            logging.info( "calling %s" % cmd_str)    
        output,_ = call_command(cmd_str)

        # This is to reduce the number of warnings in the code.
        # The mirosubs-calcdeps.js file is a concatenation of a bunch of Google Closure
        # JavaScript files, each of which has a @fileoverview tag to describe it.
        # When put all in one file, the compiler complains, so remove them all.
        output_lines = filter(lambda s: s.find("@fileoverview") == -1,
                              output.split("\n"))

        calcdeps_file = open(calcdeps_js, "w")
        calcdeps_file.write("\n".join(output_lines))
        calcdeps_file.close()

        logging.info("Compiling {0}".format(output_file_name))

        debug_arg = ''
        if not debug:
            debug_arg = '--define goog.DEBUG=false'
        extra_defines_arg = ''
        if extra_defines is not None:
            for k, v in extra_defines.items():
                extra_defines_arg += ' --define {0}={1} '.format(k, v)
        cmd_str =  ("java -jar %s --js %s %s --js_output_file %s %s %s "
                    "--define goog.NATIVE_ARRAY_PROTOTYPES=false "
                    "--output_wrapper (function(){%%output%%})(); "
                    "--compilation_level %s") % \
                    (compiler_jar, calcdeps_js, deps, compiled_js, 
                     debug_arg, extra_defines_arg, optimization_type)

        if self.verbosity > 1:
            logging.info( "calling %s" % cmd_str)    
        output,err = call_command(cmd_str)

        with open(compiled_js, 'r') as compiled_js_file:
            compiled_js_text = compiled_js_file.read()

        with open(compiled_js, 'w') as compiled_js_file:
            if include_flash_deps:
                with open(os.path.join(JS_LIB, 'js', 'swfobject.js'), 'r') as swfobject_file:
                    compiled_js_file.write(swfobject_file.read())
                with open(FLOWPLAYER_JS, 'r') as flowplayerjs_file:
                    compiled_js_file.write(flowplayerjs_file.read())
            compiled_js_file.write(compiled_js_text)
            self._append_version_for_debug(compiled_js_file, "js")
        if len(output) > 0:
            logging.info("compiler.jar output: %s" % output)

        if len(err) > 0:
            logging.info("stderr: %s" % err)
        else:
            logging.info("Successfully compiled {0}".format(output_file_name))        
        return
    
    def compile_media_bundle(self, bundle_name, bundle_type, files):
        getattr(self, "compile_%s_bundle" % bundle_type)(bundle_name, bundle_type, files)

    def copy_dirs(self):
        mr = settings.MEDIA_ROOT
        for dirname in os.listdir(mr):
            original_path = os.path.join(mr, dirname)
            if os.path.isdir(original_path) and dirname not in SKIP_COPING_ON :
                dest =  os.path.join(self.base_dir, dirname)
                if os.path.exists(dest):
                    shutil.rmtree(dest)
                shutil.copytree(original_path,
                         dest,
                         ignore=shutil.ignore_patterns(*SKIP_COPING_ON))
         # we need to copy all js, ideally this can be refactored in other libs

        

    def _output_embed_to_dir(self, output_dir, version=''):
        file_name = 'embed{0}.js'.format(version)
        context = widget.add_offsite_js_files(
            {'current_site': Site.objects.get_current(),
             'MEDIA_URL': get_cache_base_url() +"/"})
        rendered = render_to_string(
            'widget/{0}'.format(file_name), context)
        with open(os.path.join(output_dir, file_name), 'w') as f:
            f.write(rendered)
            
    def compile_conf_js(self):
        file_name = os.path.join(settings.MEDIA_ROOT, 'js/config.js')


        context = {'current_site': Site.objects.get_current(),
                   'MEDIA_URL': get_cache_base_url()+ "/"}
        rendered = render_to_string(
            'widget/config.js', context)
        with open(file_name, 'w') as f:
            f.write(rendered)

        self._output_embed_to_dir(settings.MEDIA_ROOT)
        self._output_embed_to_dir(settings.MEDIA_ROOT, settings.EMBED_JS_VERSION)
        for version in settings.PREVIOUS_EMBED_JS_VERSIONS:
            self._output_embed_to_dir(output_dir, version)


        file_name = os.path.join(settings.MEDIA_ROOT, 'js/statwidget/statwidgetconfig.js')
        rendered = render_to_string(
            'widget/statwidgetconfig.js', context)
        with open(file_name, 'w') as f:
            f.write(rendered)    
            
    def handle(self, *args, **options):
        self.verbosity = int(options.get('verbosity'))
        self.test_str_version = bool(options.get('test_str_version'))
        self.keeps_previous = bool(options.get('keeps_previous'))        
        restrict_bundles = bool(args)

        os.chdir(settings.PROJECT_ROOT)
        self.base_dir = self.create_cache_dir()
        bundles = settings.MEDIA_BUNDLES
        self.copy_dirs()
        self.compile_conf_js()
        for bundle_name, data in bundles.items():
            if restrict_bundles and bundle_name not in args:
                continue
            self.compile_media_bundle( bundle_name, data['type'], data["files"])


            
        if not self.keeps_previous:
            # we remove all but the last export, since the build can fail at the next step
            # in which case it will still need the previous build there
            base = os.path.dirname(get_cache_dir())
            targets = [os.path.join(base, x) for x in sorted_ls("media/static-cache/")
                       if x.startswith(".") is False][:-1]
            [shutil.rmtree(t) for t in targets ]
        # we now move the old temp dir to it's final destination
        final_path = get_cache_dir()
        if os.path.exists(final_path):
            shutil.rmtree(final_path)
        for filename in os.listdir(self.base_dir):
            shutil.move(os.path.join(self.base_dir, filename), os.path.join(final_path, filename))

        for filename in NO_UNIQUE_URL:
            to_path =  os.path.join(settings.MEDIA_ROOT, filename)
            from_path = os.path.join(final_path, filename)
            if os.path.exists(to_path):
                os.remove(to_path)
            shutil.copy(from_path, to_path)

        if self.test_str_version:
            self.test_string_version()

    def test_string_version(self):
        """
        Make sure all the compiled files have the version name appended
        """
        version_str = _make_version_debug_string()
        for filename in NO_UNIQUE_URL:
            # we only need compiled sutff (widgetizerprimer breaks the stable urls = compiled assumption
            if os.path.basename(filename) not in settings.MEDIA_BUNDLES.keys():
                continue
            to_path =  os.path.join(settings.MEDIA_ROOT, filename)
            
            data = open(to_path).read()
            assert(data.endswith(version_str))
            
        


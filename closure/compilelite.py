#!/usr/bin/env python

import sys
import os
import subprocess
import logging

BASE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(BASE, ".."))
import settings

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

JS_LIB = os.path.join(BASE, "../media/js")
CLOSURE_LIB = os.path.join(JS_LIB, "closure-library")
FLOWPLAYER_JS = os.path.join(BASE, "../media/flowplayer/flowplayer-3.2.2.min.js")

calcdeps_js = os.path.join(JS_LIB, 'mirosubs-calcdeps.js')

def call_command(command):
    process = subprocess.Popen(command.split(' '),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return process.communicate()

logging.info("Calculating closure dependencies")

output,_ = call_command(("%s/closure/bin/calcdeps.py -i %s/closure-dependencies.js " +
                         "-p %s/ -o script") % 
                        (CLOSURE_LIB, JS_LIB, CLOSURE_LIB))

logging.info("Compiling JavaScript")

def compile(output_file_name, js_file_list):
    output_file_path = os.path.join(JS_LIB, output_file_name)
    with open(output_file_path, 'w') as compiled_js_file:
        compiled_js_file.write('(function(){');
        with open(os.path.join(JS_LIB, 'swfobject.js'), 'r') as swfobject_file:
            compiled_js_file.write(swfobject_file.read())
        with open(FLOWPLAYER_JS, 'r') as flowplayerjs_file:
            compiled_js_file.write(flowplayerjs_file.read())
        compiled_js_file.write(output)
        js_file_paths = [os.path.join(JS_LIB, file) for file in js_file_list]
        for dep_file_name in js_file_paths:
            logging.info('Adding {0}'.format(dep_file_name))
            with open(dep_file_name, 'r') as dep_file:
                compiled_js_file.write(dep_file.read())
        compiled_js_file.write('})();');

# compile('mirosubs-offsite-compiled.js', settings.JS_OFFSITE)
# compile('mirosubs-onsite-compiled.js', settings.JS_ONSITE)

# widgetizer_js_files = list(settings.JS_OFFSITE)
# assumes that some other process has generated widgetizer/widgetizerconfig.js
# widgetizer_js_files.append('widgetizer/widgetizerconfig.js')
# widgetizer_js_files.append('widgetizer/widgetizer.js')
# widgetizer_js_files.append('widgetizer/dowidgetize.js')
compile('mirosubs-widgetizer.js', [])

# extension_js_files = list(settings.JS_OFFSITE)
# assumes that some other process has generated widgetizer/widgetizerconfig.js
# extension_js_files.append('widgetizer/widgetizerconfig.js')
# extension_js_files.append('widgetizer/widgetizer.js')
# extension_js_files.append('widgetizer/extension.js')
# compile('mirosubs-extension.js', extension_js_files)

logging.info("Success")

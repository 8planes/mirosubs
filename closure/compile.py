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

def call_command(command):
    process = subprocess.Popen(command.split(' '),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return process.communicate()

def compile(output_file_name, js_file_list, 
            closure_dep_file='closure-dependencies.js',
            include_flash_deps=True):
    logging.info("Starting {0}".format(output_file_name))

    deps = [" --js %s " % os.path.join(JS_LIB, file) for file in js_file_list]
    calcdeps_js = os.path.join(JS_LIB, 'mirosubs-calcdeps.js')
    compiled_js = os.path.join(JS_LIB, output_file_name)
    compiler_jar = os.path.join(BASE, 'compiler.jar')

    logging.info("Calculating closure dependencies")

    output,_ = call_command(("%s/closure/bin/calcdeps.py -i %s/%s " +
                             "-p %s/ -o script") % 
                            (CLOSURE_LIB, JS_LIB, closure_dep_file, CLOSURE_LIB))

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

    output,err = call_command(("java -jar %s --js %s %s "
                               "--js_output_file %s "
                               "--output_wrapper (function(){%%output%%})(); "
                               "--compilation_level ADVANCED_OPTIMIZATIONS") % 
                              (compiler_jar, calcdeps_js, deps, compiled_js))
    
    with open(compiled_js, 'r') as compiled_js_file:
        compiled_js_text = compiled_js_file.read()
        
    with open(compiled_js, 'w') as compiled_js_file:
        if include_flash_deps:
            with open(os.path.join(JS_LIB, 'swfobject.js'), 'r') as swfobject_file:
                compiled_js_file.write(swfobject_file.read())
            with open(FLOWPLAYER_JS, 'r') as flowplayerjs_file:
                compiled_js_file.write(flowplayerjs_file.read())
        compiled_js_file.write(compiled_js_text)

    if len(output) > 0:
        logging.info("compiler.jar output: %s" % output)

    if len(err) > 0:
        logging.info("stderr: %s" % err)

    logging.info("Successfully compiled {0}".format(output_file_name))

compile('mirosubs-offsite-compiled.js', settings.JS_OFFSITE)
compile('mirosubs-onsite-compiled.js', settings.JS_ONSITE)

# assumes that some other process has generated config.js
widgetizer_js_files = ['config.js']
widgetizer_js_files.extend(settings.JS_WIDGETIZER)
compile('mirosubs-widgetizer.js', widgetizer_js_files)

# assumes that some other process has generated config.js
extension_js_files = ['config.js']
extension_js_files.extend(settings.JS_EXTENSION)
compile('mirosubs-extension.js', extension_js_files)

statwidget_js_files = [
    'mirosubs.js',
    'rpc.js',
    'loadingdom.js',
    'statwidget/statwidgetconfig.js',
    'statwidget/statwidget.js']
# assumes that some other process has generated statwidget/statwidgetconfig.js
compile('mirosubs-statwidget.js', statwidget_js_files, 
        closure_dep_file='closure-stat-dependencies.js',
        include_flash_deps=False)

api_js_files = list(settings.JS_CORE)
assumes that some other process has generated config.js
api_js_files.append('config.js')
api_js_files.append('widget/api/servermodel.js')
api_js_files.append('widget/api/api.js')
compile('mirosubs-api.js', api_js_files)

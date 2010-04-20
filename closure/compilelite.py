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

deps = [os.path.join(JS_LIB, file) for file in settings.JS_RAW]
calcdeps_js = os.path.join(JS_LIB, 'mirosubs-calcdeps.js')
compiled_js = os.path.join(JS_LIB, 'mirosubs-compiled.js')

def call_command(command):
    process = subprocess.Popen(command.split(' '),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    return process.communicate()

logging.info("Calculating closure dependencies")

output,_ = call_command(("%s/closure/bin/calcdeps.py -i %s/closure-dependencies.js " +
                         "-p %s/ -o script") % 
                        (CLOSURE_LIB, JS_LIB, CLOSURE_LIB))

calcdeps_file = open(calcdeps_js, "w")
calcdeps_file.write(output)
calcdeps_file.close()

logging.info("Compiling JavaScript")

with open(compiled_js, 'w') as compiled_js_file:
    with open(os.path.join(JS_LIB, 'swfobject.js'), 'r') as swfobject_file:
        compiled_js_file.write(swfobject_file.read())
    compiled_js_file.write(output)
    for dep_file_name in deps:
        logging.info('Adding {0}'.format(dep_file_name))
        with open(dep_file_name, 'r') as dep_file:
            compiled_js_file.write(dep_file.read())

logging.info("Success")

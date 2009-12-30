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

deps = [" --js %s " % os.path.join(JS_LIB, file) for file in settings.JS_RAW]
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

output,_ = call_command(("java -jar compiler.jar --js %s %s " +
                         "--js_output_file %s " +
                         "--compilation_level ADVANCED_OPTIMIZATIONS") % 
                        (calcdeps_js, deps, compiled_js))

if len(output) > 0:
    logging.info("compiler.jar output: %s" % output)

logging.info("Success")

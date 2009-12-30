#!/bin/bash

BASE=`dirname $0`
JS_LIB=$BASE/../media/js
CLOSURE_LIB=$JS_LIB/closure-library

$CLOSURE_LIB/closure/bin/calcdeps.py -i $JS_LIB/closure-dependencies.js \
  -p $CLOSURE_LIB/ -o script > $JS_LIB/mirosubs-calcdeps.js

java -jar compiler.jar --js $JS_LIB/mirosubs-calcdeps.js --js $JS_LIB/mirosubs.js \
    --js_output_file $JS_LIB/mirosubs-compiled.js \
    --compilation_level ADVANCED_OPTIMIZATIONS
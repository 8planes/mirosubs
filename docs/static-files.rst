**********************************
Static Files
**********************************


*********
Overview
*********
The static files pipeline for unisubs has two goals:

- Combine & compress files that are used together (e.g. one html page linking to many css filed) 
- Make sure every time media is processed we have each file with a unique name. This allows us to the set the expire header to the far future, meaning that it will be aggressively cached.
- Each new release won't be cached by clients, since the URLS for each release are unique

**************************
Gotchas for developers
**************************
1. Make sure you run create_commit_file after each commit or merger (git hooks are the best place to keep that)
***************************
Compilation / Minification
***************************
settings.py has a MEDIA_BUNDLES dictionary. Each key sets an id (a unique name for the bundle), with the following properties:

- `type`: Can be `css` or `js` for now
- `files`: a sequence of files to be processed. Files will be processed in the order in which they're are defined on the bundle. They're path should be relative to the MEDIA_URL (i.e. mirosubs/media)
- `closure_deps`: File (inside js) that holds the closure dependencies list.
- `debug`: If true will include the closure-debug-dependencies.js.
- `include_flash_deps`: boolean
- `optimizations`: defaults to closure's more agreesive mode (ADVANCED_OPTIMIZATIONS) else can be set to `SIMPLE_OPTIMIZATIONS`.

Files will be concatenated in the order in which they are defined. 

JS will be compiled by the closure compiler at closure/compiler.jar .

CSS will be compressed with the YUI compressor at css-compression/yuicompressor-2.4.6.jar .For css we are only minifinng, but we are not changing anything that might break the site.

**********************************
In Templates
**********************************
In templates, instead of liking to the the individual css or js files, you'd simply::

 {% load  media_compressor %}
 {% include_bundle "[bundle name - the key in MEDIA_BUNDLE]" %}


If `CSS_USE_COMPILED` is True the link to that bundle compressed file will be inserted. Else we'll add the original urls. If a CSS_USE_COMPILED is not set, it will default to the oposite of `settings.DEBUG`.

***************************
Compiling
***************************
Compiling should be done with ::

  $manage.py compile_media --settings*[settings file]

***************************
Dir layout
***************************
Inside MEDIA_ROOT media will be compiled to `static-cache/[hash of latest git commit]/.
i.e. MEDIA_ROOT/static-cache/21a1bbcc/js/mirosubs-onsite-compiled.js

In this way we use one unique identifier for each revision, in fact, we relly on the one the scm gives us, which has the added benefit of making it easier to troubleshoot revisions and if the links are correct.

Static cache is never in source control and should not be the storage path for anything. It's sole purpose is to be a disposable place where media can be compiled and moved to a unique URL.


***************************
MEDIA_URL
***************************
Since the location of media is no longer static, the MEDIA_URL takes into consideration the new directory layout. Every time a new git version is running and deploy/create_commit_file.py is ran, the MEDIA_URL will change (and) therefore you need to restart the sever/reload app coder for that to take effect. 

^^^^^^^^^^^^^^^^^^^^^^^^^^^
Relevant Settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^
These need to be defined in settings.py:

""""""""""""""""""""
COMPRESS_YUI_BINARY
"""""""""""""""""""" 
The path, relative to the mirosubs dir where the YUI compressor jar lives( "java -jar ./css-compression/yuicompressor-2.4.6.jar")

"""""""""""""""""
JS_USE_COMPILED
"""""""""""""""""
Should always be True on dev, staging and production. Developers can set it to false to make development/debugging  easier.

""""""""""""""""""""
COMPRESS_OUTPUT_NAME
""""""""""""""""""""
The directory that holds the root to the static cache, i.e. where all compiled and version specific media will be copyed to (see dir layout above). Defaults to 'static-cache'.

********************
Serving Media
********************
On the local development machine or the dev environment media is stored locally in the file disk. Staging and production with Amazon's s3, so in those environments media needs to be copied to s3.

This is achieved by calling::

$manage.py send_to_s3 --settings=[settings module] 

Which is part of the update_static fabric command.
That command requires the USE_AMAZON set (needs correct values for secret, id and bucket), and it will:

- Move the entire content of MEDIA_ROOT/static-cache/[hash guid] . All of these will have far future expire headers.
- Copy and create the files that are used externally (in offsite widgets), namely: ["js/mirosubs-widgetizer.js", "js/widgetizer/widgetizerprimer.js"] to MEDIA_ROOT/js/.... These do not have far future expire headers.

All files above 1kb will be served with gzip compression (smaller files tend to actually inflate ).




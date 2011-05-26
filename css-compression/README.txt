Unisubs is compiling all css into specific files in order to make few requests as possible, use far future expire on headers and be able to compress (stripe comments and whitespaces) them.

1. How it works:
a) settings.py has media bundles, identified by their name (e.g 'video_history'), and the files to be included.
b) Add / remove  the path to the css files (always from the root of MEDIA_ROOT) to the desired bundles
c) if locally run:
$ python manage.py compile_media --settings=dev_settings && python manage.py update_compiled_urls --settings=dev_settings     
(to update the css)
d) You can disable css compression with the setting CSS_USE_COMPILED ( which defaults to the oposite of debug)

Then at compilation time, we go trough each bundle, read from disk the css file, concatenate them. Run the contatenated file though the yahoo yui compressor (at css-compression/yuicompressor....jar) . We take the md5 checksum of that result and save that file on static-cache with the checksum as the filename.
After all bundles are done, we save the mapping between available bundles and their md5 names static-cache/compresses.py.
When a new version is deployed (through the update fab command) we download the mappings above and read them, saving them as a dict on the settings file. (similar to how the commit.py works). Then, at run time, the template tag will subtistitute a 'include_css_bundle' block with the url that it fetched on the mappings file. If that files, it simply inserts the <link> tags pointing to the files in the bundle.

2, How to add css files:
a) Add files to media/css
b) Add to the bundles needed ( check on the templates used, which bundles are already in use ).
c) If you need a new page new a new bundle, create one in settings.py and use it on the {% include_css_bundle "new_name" %} on your template.
d) Watchout for URLS, an image url should be, for example: "../images/foo.jpg".

3. How to add an external lib (such as a Jquery plugin).
a) Move the plugin's css file to the media/css directory.
b) Include it on the needed bundles on settings.py (see above)
c) Move the 'images' directory to "images/plugin-name/", for example "images/jalert" for jalert.
d) Replace the "url()" tags in the css from "images/" to "../images/plugin_name" 



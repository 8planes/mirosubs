===========================
Running Universal Subtitles
===========================

To run the development version:

1. Git clone the repository::

       git clone git://github.com/8planes/mirosubs.git mirosubs

   Now the entire project will be in the mirosubs directory.

2. Install virtualenv http://pypi.python.org/pypi/virtualenv

3. (optional) download and download the virtualenv wrapper bash
   functions http://www.doughellmann.com/projects/virtualenvwrapper/

4. Create a virtual environment and activate it. Here is how to do it 
   *without* the virtualenv wrapper. Run these commands from the parent 
   of the mirosubs directory created in #1::

   $ virtualenv mirosubs-env
   $ source mirosubs-env/bin/activate

   If you're using the virtualenv wrapper (run from any directory)::

   $ mkvirtualenv mirosubs
   $ workon mirosubs

5. run::

   $ easy_install -U setuptools
   $ easy_install pip
   $ cd deploy
   # this is the mirosubs directory you cloned from git, not the parent you created the virtualenv in.
   $ pip install -r requirements.txt
       note: you'll need mercurial installed to make this last command work.
       note2: If you do not have the MySQL bindings installed (MySQLdb) and wish to keep it that way, unisubs runs just fine on sqlite, just comment out the line "MySQL_python>=1.2.2" on deploy/requirements.txt before running this command.


6. Check out google closure into directory of your choice: svn checkout 
   http://closure-library.googlecode.com/svn/trunk/ <directory>. Then 
   symlink media/js/closure-library to the checkout location. From the 
   mirosubs directory in step 1::

   $ cd media/js
   $ ln -s <google closure checkout directory> closure-library

7. Add mirosubs.example.com to your hosts file, pointing at 127.0.0.1. 
   This is necessary for Twitter oauth to work correctly.

8. From the mirosubs directory created in step 1, first create the 
   database with::

       python manage.py syncdb

   Then update the database with::

       python manage.py migrate

   SQLLite warnings are okay. Then run the site with::

       ./dev-runserver.sh

   You can access the site at http://mirosubs.example.com:8000.

9. (optional) If you want to run video searches  / watch page locally, you need to set up solr:

   A. Download solr and unzip to ../buildout/parts/solr (relative to this directory).
   B. Run ./manage.py run_solr in one terminal that is dedicated to running the solr process.
   C. run ./manage.py rebuild_index to update the index.
   D. That should be it but, in case you're interested, there's a 
      list of haystack commands at 
      http://docs.haystacksearch.org/dev/management_commands.html
   * If you want to install SOLR as a daemon on your Mac, please see
     https://github.com/8planes/mirosubs/wiki/Running-SOLR-as-a-daemon-on-Mac

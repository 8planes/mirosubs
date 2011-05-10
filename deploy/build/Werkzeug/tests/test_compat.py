# -*- coding: utf-8 -*-

import sys
import warnings
from subprocess import Popen, PIPE
from werkzeug.test import create_environ


import_code = '''\
import sys
sys.path.insert(0, '..')
import werkzeug.%s
print ':'.join([k[9:] for k, v in sys.modules.iteritems()
                if v is not None and k.startswith('werkzeug.')])
'''


def perform_import(module, allowed):
    client = Popen([sys.executable, '-c', import_code % module],
                   stdout=PIPE)
    imported = set(client.communicate()[0].strip().split(':'))
    rv = imported - allowed - set([module])
    print 'leftovers from %r import: %s' % (module, rv)
    return rv


def test_old_imports():
    """Make sure everything imports from old places"""
    from werkzeug.utils import Headers, MultiDict, CombinedMultiDict, \
         Headers, EnvironHeaders
    from werkzeug.http import Accept, MIMEAccept, CharsetAccept, \
         LanguageAccept, ETags, HeaderSet, WWWAuthenticate, \
         Authorization


def test_exposed_werkzeug_mod():
    """Make sure all things are importable."""
    import werkzeug
    for key in werkzeug.__all__:
        getattr(werkzeug, key)


def test_demand_import():
    """Make sure that we're not importing too much."""
    allowed_imports = set(['_internal', 'utils', 'http', 'exceptions',
                           'datastructures'])

    assert perform_import('http', allowed_imports) == set()
    assert perform_import('utils', allowed_imports) == set()

    allowed_imports.update(('urls', 'formparser', 'wsgi'))
    assert perform_import('wrappers', allowed_imports) == set()

    allowed_imports.add('wrappers')
    assert perform_import('useragents', allowed_imports) == set()
    assert perform_import('test', allowed_imports) == set()
    assert perform_import('serving', allowed_imports) == set()


def test_fix_headers_in_response():
    """Make sure fix_headers still works for backwards compatibility"""
    # ignore some warnings werkzeug emits for backwards compat
    for msg in ['called into deprecated fix_headers',
                'fix_headers changed behavior']:
        warnings.filterwarnings('ignore', message=msg,
                                category=DeprecationWarning)

    from werkzeug import Response
    class MyResponse(Response):
        def fix_headers(self, environ):
            Response.fix_headers(self, environ)
            self.headers['x-foo'] = "meh"
    myresp = MyResponse('Foo')
    resp = Response.from_app(myresp, create_environ(method='GET'))
    assert resp.headers['x-foo'] == 'meh'
    assert resp.data == 'Foo'

    warnings.resetwarnings()

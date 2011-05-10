=============
HTTP Utilties
=============

.. module:: werkzeug

You can import all these objects directly from :mod:`werkzeug`.

Date Functions
==============

The following functions simplify working with times in an HTTP context.
Werkzeug uses offset-naive :class:`~datetime.datetime` objects internally
that store the time in UTC.  If you're working with timezones in your
application make sure to replace the tzinfo attribute with a UTC timezone
information before processing the values.
   
.. autofunction:: cookie_date

.. autofunction:: http_date

.. autofunction:: parse_date

Form Data Parsing
=================

Werkzeug provides the form parsing functions separately from the request
object so that you can access form data from a plain WSGI environment.

The following formats are supported by the form data parser currently:

-   `application/x-www-form-urlencoded`
-   `multipart/form-data`

Nested multipart is currently not supported (Werkzeug 0.6) albeit unused
by any of the modern webbrowsers.

Usage example:

>>> from cStringIO import StringIO
>>> data = '--foo\r\nContent-Disposition: form-data; name="test"\r\n' \
... '\r\nHello World!\r\n--foo--'
>>> environ = {'wsgi.input': StringIO(data), 'CONTENT_LENGTH': str(len(data)),
...            'CONTENT_TYPE': 'multipart/form-data; boundary=foo',
...            'REQUEST_METHOD': 'POST'}
>>> stream, form, files = parse_form_data(environ)
>>> stream.read()
''
>>> form['test']
u'Hello World!'
>>> not files
True

Normally the WSGI environment is provided by the WSGI gateway with the
incoming data as part of it.  If you want to generate such fake-WSGI
environments for unittesting you might want to use the
:func:`create_environ` function or the :class:`EnvironBuilder` instead.

.. autofunction:: parse_form_data

Header Parsing
==============

The following functions can be used to parse incoming HTTP headers.
Because Python does not provide data structures with the semantics required
by :rfc:`2616`, Werkzeug implements some custom data structures that are
`documented separately <http-datastructures>`.

.. autofunction:: parse_options_header

.. autofunction:: parse_set_header

.. autofunction:: parse_list_header

.. autofunction:: parse_dict_header

.. autofunction:: parse_accept_header(value, [class])

.. autofunction:: parse_cache_control_header

.. autofunction:: parse_authorization_header

.. autofunction:: parse_www_authenticate_header

Header Utilities
================

The following utilities operate on HTTP headers well but do not parse
them.  They are useful if you're dealing with conditional responses or if
you want to proxy arbtirary requests but want to remove WSGI-unsupported
hop-by-hop headers.  Also there is a function to create HTTP header
strings from the parsed data.

.. autofunction:: is_entity_header

.. autofunction:: is_hop_by_hop_header

.. autofunction:: remove_entity_headers

.. autofunction:: remove_hop_by_hop_headers

.. autofunction:: quote_header_value

.. autofunction:: unquote_header_value

.. autofunction:: dump_header


Conditional Response Helpers
============================

For conditional responses the following functions might be useful:

.. autofunction:: parse_etags

.. autofunction:: quote_etag

.. autofunction:: unquote_etag

.. autofunction:: generate_etag

.. autofunction:: is_resource_modified

Constants
=========

.. data:: HTTP_STATUS_CODES

    A dict of status code -> default status message pairs.  This is used
    by the wrappers and other places where a integer status code is expanded
    to a string throughout Werkzeug.

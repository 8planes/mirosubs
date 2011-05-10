/*
 * x509.c
 *
 * Copyright (C) AB Strakt 2001, All rights reserved
 * Copyright (C) Jean-Paul Calderone 2008, All rights reserved
 *
 * Certificate (X.509) handling code, mostly thin wrappers around OpenSSL.
 * See the file RATIONALE for a short explanation of why this module was written.
 *
 * Reviewed 2001-07-23
 */
#include <Python.h>
#define crypto_MODULE
#include "crypto.h"

/*
 * X.509 is a standard for digital certificates.  See e.g. the OpenSSL homepage
 * http://www.openssl.org/ for more information
 */

static char crypto_X509_get_version_doc[] = "\n\
Return version number of the certificate\n\
\n\
Arguments: self - The X509 object\n\
           args - The Python argument tuple, should be empty\n\
Returns:   Version number as a Python integer\n\
";

static PyObject *
crypto_X509_get_version(crypto_X509Obj *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":get_version"))
        return NULL;

    return PyInt_FromLong((long)X509_get_version(self->x509));
}

static char crypto_X509_set_version_doc[] = "\n\
Set version number of the certificate\n\
\n\
Arguments: self - The X509 object\n\
           args - The Python argument tuple, should be:\n\
             version - The version number\n\
Returns:   None\n\
";

static PyObject *
crypto_X509_set_version(crypto_X509Obj *self, PyObject *args)
{
    int version;

    if (!PyArg_ParseTuple(args, "i:set_version", &version))
        return NULL;

    X509_set_version(self->x509, version);

    Py_INCREF(Py_None);
    return Py_None;
}

static char crypto_X509_get_serial_number_doc[] = "\n\
Return serial number of the certificate\n\
\n\
Arguments: self - The X509 object\n\
           args - The Python argument tuple, should be empty\n\
Returns:   Serial number as a Python integer\n\
";

static PyObject *
crypto_X509_get_serial_number(crypto_X509Obj *self, PyObject *args)
{
    ASN1_INTEGER *asn1_i;
    BIGNUM *bignum;
    char *hex;
    PyObject *res;

    if (!PyArg_ParseTuple(args, ":get_serial_number"))
        return NULL;

    asn1_i = X509_get_serialNumber(self->x509);
    bignum = ASN1_INTEGER_to_BN(asn1_i, NULL);
    hex = BN_bn2hex(bignum);
    res = PyLong_FromString(hex, NULL, 16);
    BN_free(bignum);
    free(hex);
    return res;
}

static char crypto_X509_set_serial_number_doc[] = "\n\
Set serial number of the certificate\n\
\n\
Arguments: self - The X509 object\n\
           args - The Python argument tuple, should be:\n\
             serial - The serial number\n\
Returns:   None\n\
";

static PyObject *
crypto_X509_set_serial_number(crypto_X509Obj *self, PyObject *args)
{
    long small_serial;
    PyObject *serial = NULL;
    PyObject *hex = NULL;
    PyObject *format = NULL;
    PyObject *format_args = NULL;
    ASN1_INTEGER *asn1_i = NULL;
    BIGNUM *bignum = NULL;

    if (!PyArg_ParseTuple(args, "O:set_serial_number", &serial)) {
        return NULL;
    }

    if (!PyInt_Check(serial) && !PyLong_Check(serial)) {
        PyErr_SetString(
            PyExc_TypeError, "serial number must be integer");
        goto err;
    }

    if ((format_args = Py_BuildValue("(O)", serial)) == NULL) {
        goto err;
    }

    if ((format = PyString_FromString("%x")) == NULL) {
        goto err;
    }

    if ((hex = PyString_Format(format, format_args)) == NULL) {
        goto err;
    }

    /**
     * BN_hex2bn stores the result in &bignum.  Unless it doesn't feel like
     * it.  If bignum is still NULL after this call, then the return value
     * is actually the result.  I hope.  -exarkun
     */
    small_serial = BN_hex2bn(&bignum, PyString_AsString(hex));

    Py_DECREF(format_args);
    format_args = NULL;
    Py_DECREF(format);
    format = NULL;
    Py_DECREF(hex);
    hex = NULL;

    if (bignum == NULL) {
        if (ASN1_INTEGER_set(X509_get_serialNumber(self->x509), small_serial)) {
            exception_from_error_queue();
            goto err;
        }
    } else {
        asn1_i = BN_to_ASN1_INTEGER(bignum, NULL);
        BN_free(bignum);
        bignum = NULL;
        if (asn1_i == NULL) {
            exception_from_error_queue();
            goto err;
        }
        if (!X509_set_serialNumber(self->x509, asn1_i)) {
            exception_from_error_queue();
            goto err;
        }
        ASN1_INTEGER_free(asn1_i);
        asn1_i = NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;

  err:
    if (format_args) {
        Py_DECREF(format_args);
    }
    if (format) {
        Py_DECREF(format);
    }
    if (hex) {
        Py_DECREF(hex);
    }
    if (bignum) {
        BN_free(bignum);
    }
    if (asn1_i) {
        ASN1_INTEGER_free(asn1_i);
    }
    return NULL;
}

static char crypto_X509_get_issuer_doc[] = "\n\
Create an X509Name object for the issuer of the certificate\n\
\n\
Arguments: self - The X509 object\n\
           args - The Python argument tuple, should be empty\n\
Returns:   An X509Name object\n\
";

static PyObject *
crypto_X509_get_issuer(crypto_X509Obj *self, PyObject *args)
{
    crypto_X509NameObj *pyname;
    X509_NAME *name;

    if (!PyArg_ParseTuple(args, ":get_issuer"))
        return NULL;

    name = X509_get_issuer_name(self->x509);
    pyname = crypto_X509Name_New(name, 0);
    if (pyname != NULL)
    {
        pyname->parent_cert = (PyObject *)self;
        Py_INCREF(self);
    }
    return (PyObject *)pyname;
}

static char crypto_X509_set_issuer_doc[] = "\n\
Set the issuer of the certificate\n\
\n\
Arguments: self - The X509 object\n\
           args - The Python argument tuple, should be:\n\
             issuer - The issuer name\n\
Returns:   None\n\
";

static PyObject *
crypto_X509_set_issuer(crypto_X509Obj *self, PyObject *args)
{
    crypto_X509NameObj *issuer;

    if (!PyArg_ParseTuple(args, "O!:set_issuer", &crypto_X509Name_Type,
			  &issuer))
        return NULL;

    if (!X509_set_issuer_name(self->x509, issuer->x509_name))
    {
        exception_from_error_queue();
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static char crypto_X509_get_subject_doc[] = "\n\
Create an X509Name object for the subject of the certificate\n\
\n\
Arguments: self - The X509 object\n\
           args - The Python argument tuple, should be empty\n\
Returns:   An X509Name object\n\
";

static PyObject *
crypto_X509_get_subject(crypto_X509Obj *self, PyObject *args)
{
    crypto_X509NameObj *pyname;
    X509_NAME *name;

    if (!PyArg_ParseTuple(args, ":get_subject"))
        return NULL;

    name = X509_get_subject_name(self->x509);
    pyname = crypto_X509Name_New(name, 0);
    if (pyname != NULL)
    {
        pyname->parent_cert = (PyObject *)self;
        Py_INCREF(self);
    }
    return (PyObject *)pyname;
}

static char crypto_X509_set_subject_doc[] = "\n\
Set the subject of the certificate\n\
\n\
Arguments: self - The X509 object\n\
           args - The Python argument tuple, should be:\n\
             subject - The subject name\n\
Returns:   None\n\
";

static PyObject *
crypto_X509_set_subject(crypto_X509Obj *self, PyObject *args)
{
    crypto_X509NameObj *subject;

    if (!PyArg_ParseTuple(args, "O!:set_subject", &crypto_X509Name_Type,
			  &subject))
        return NULL;

    if (!X509_set_subject_name(self->x509, subject->x509_name))
    {
        exception_from_error_queue();
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static char crypto_X509_get_pubkey_doc[] = "\n\
Get the public key of the certificate\n\
\n\
Arguments: self - The X509 object\n\
           args - The Python argument tuple, should be empty\n\
Returns:   The public key\n\
";

static PyObject *
crypto_X509_get_pubkey(crypto_X509Obj *self, PyObject *args)
{
    crypto_PKeyObj *crypto_PKey_New(EVP_PKEY *, int);
    EVP_PKEY *pkey;
    crypto_PKeyObj *py_pkey;

    if (!PyArg_ParseTuple(args, ":get_pubkey"))
        return NULL;

    if ((pkey = X509_get_pubkey(self->x509)) == NULL)
    {
        exception_from_error_queue();
        return NULL;
    }

    py_pkey = crypto_PKey_New(pkey, 1);
    if (py_pkey != NULL) {
	py_pkey->only_public = 1;
    }
    return (PyObject *)py_pkey;
}

static char crypto_X509_set_pubkey_doc[] = "\n\
Set the public key of the certificate\n\
\n\
Arguments: self - The X509 object\n\
           args - The Python argument tuple, should be:\n\
             pkey - The public key\n\
Returns:   None\n\
";

static PyObject *
crypto_X509_set_pubkey(crypto_X509Obj *self, PyObject *args)
{
    crypto_PKeyObj *pkey;

    if (!PyArg_ParseTuple(args, "O!:set_pubkey", &crypto_PKey_Type, &pkey))
        return NULL;

    if (!X509_set_pubkey(self->x509, pkey->pkey))
    {
        exception_from_error_queue();
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_set_asn1_time(char *format, ASN1_TIME* timestamp, crypto_X509Obj *self, PyObject *args)
{
	char *when;

	if (!PyArg_ParseTuple(args, format, &when))
		return NULL;

	if (ASN1_GENERALIZEDTIME_set_string(timestamp, when) == 0) {
		ASN1_GENERALIZEDTIME dummy;
		dummy.type = V_ASN1_GENERALIZEDTIME;
		dummy.length = strlen(when);
		dummy.data = (unsigned char *)when;
		if (!ASN1_GENERALIZEDTIME_check(&dummy)) {
			PyErr_SetString(PyExc_ValueError, "Invalid string");
		} else {
			PyErr_SetString(PyExc_RuntimeError, "Unknown ASN1_GENERALIZEDTIME_set_string failure");
		}
		return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static char crypto_X509_set_notBefore_doc[] = "\n\
Set the time stamp for when the certificate starts being valid\n\
\n\
Arguments: self - The X509 object\n\
           args - The Python argument tuple, should be:\n\
             when - A string giving the timestamp, in the format:\n\
\n\
                 YYYYMMDDhhmmssZ\n\
                 YYYYMMDDhhmmss+hhmm\n\
                 YYYYMMDDhhmmss-hhmm\n\
\n\
Returns:   None\n\
";

static PyObject*
crypto_X509_set_notBefore(crypto_X509Obj *self, PyObject *args)
{
	return _set_asn1_time(
		"s:set_notBefore", X509_get_notBefore(self->x509), self, args);
}

static char crypto_X509_set_notAfter_doc[] = "\n\
Set the time stamp for when the certificate stops being valid\n\
\n\
Arguments: self - The X509 object\n\
           args - The Python argument tuple, should be:\n\
             when - A string giving the timestamp, in the format:\n\
\n\
                 YYYYMMDDhhmmssZ\n\
                 YYYYMMDDhhmmss+hhmm\n\
                 YYYYMMDDhhmmss-hhmm\n\
\n\
Returns:   None\n\
";

static PyObject*
crypto_X509_set_notAfter(crypto_X509Obj *self, PyObject *args)
{
	return _set_asn1_time(
		"s:set_notAfter", X509_get_notAfter(self->x509), self, args);
}

static PyObject*
_get_asn1_time(char *format, ASN1_TIME* timestamp, crypto_X509Obj *self, PyObject *args)
{
	ASN1_GENERALIZEDTIME *gt_timestamp = NULL;
	PyObject *py_timestamp = NULL;

	if (!PyArg_ParseTuple(args, format)) {
		return NULL;
	}

	/*
	 * http://www.columbia.edu/~ariel/ssleay/asn1-time.html
	 */
	/*
	 * There must be a way to do this without touching timestamp->data
	 * directly. -exarkun
	 */
	if (timestamp->length == 0) {
	    Py_INCREF(Py_None);
	    return Py_None;
	} else if (timestamp->type == V_ASN1_GENERALIZEDTIME) {
		return PyString_FromString((char *)timestamp->data);
	} else {
		ASN1_TIME_to_generalizedtime(timestamp, &gt_timestamp);
		if (gt_timestamp == NULL) {
			exception_from_error_queue();
			return NULL;
		} else {
			py_timestamp = PyString_FromString((char *)gt_timestamp->data);
			ASN1_GENERALIZEDTIME_free(gt_timestamp);
			return py_timestamp;
		}
	}
}

static char crypto_X509_get_notBefore_doc[] = "\n\
Retrieve the time stamp for when the certificate starts being valid\n\
\n\
Arguments: self - The X509 object\n\
           args - The Python argument tuple, should be empty.\n\
\n\
Returns:   A string giving the timestamp, in the format:\n\
\n\
                 YYYYMMDDhhmmssZ\n\
                 YYYYMMDDhhmmss+hhmm\n\
                 YYYYMMDDhhmmss-hhmm\n\
           or None if there is no value set.\n\
";

static PyObject*
crypto_X509_get_notBefore(crypto_X509Obj *self, PyObject *args)
{
	/*
	 * X509_get_notBefore returns a borrowed reference.
	 */
	return _get_asn1_time(
		":get_notBefore", X509_get_notBefore(self->x509), self, args);
}


static char crypto_X509_get_notAfter_doc[] = "\n\
Retrieve the time stamp for when the certificate stops being valid\n\
\n\
Arguments: self - The X509 object\n\
           args - The Python argument tuple, should be empty.\n\
\n\
Returns:   A string giving the timestamp, in the format:\n\
\n\
                 YYYYMMDDhhmmssZ\n\
                 YYYYMMDDhhmmss+hhmm\n\
                 YYYYMMDDhhmmss-hhmm\n\
           or None if there is no value set.\n\
";

static PyObject*
crypto_X509_get_notAfter(crypto_X509Obj *self, PyObject *args)
{
	/*
	 * X509_get_notAfter returns a borrowed reference.
	 */
	return _get_asn1_time(
		":get_notAfter", X509_get_notAfter(self->x509), self, args);
}


static char crypto_X509_gmtime_adj_notBefore_doc[] = "\n\
Change the timestamp for when the certificate starts being valid to the current\n\
time plus an offset.\n \
\n\
Arguments: self - The X509 object\n\
           args - The Python argument tuple, should be:\n\
             i - The adjustment\n\
Returns:   None\n\
";

static PyObject *
crypto_X509_gmtime_adj_notBefore(crypto_X509Obj *self, PyObject *args)
{
    long i;

    if (!PyArg_ParseTuple(args, "l:gmtime_adj_notBefore", &i))
        return NULL;

    X509_gmtime_adj(X509_get_notBefore(self->x509), i);

    Py_INCREF(Py_None);
    return Py_None;
}

static char crypto_X509_gmtime_adj_notAfter_doc[] = "\n\
Adjust the time stamp for when the certificate stops being valid\n\
\n\
Arguments: self - The X509 object\n\
           args - The Python argument tuple, should be:\n\
             i - The adjustment\n\
Returns:   None\n\
";

static PyObject *
crypto_X509_gmtime_adj_notAfter(crypto_X509Obj *self, PyObject *args)
{
    long i;

    if (!PyArg_ParseTuple(args, "l:gmtime_adj_notAfter", &i))
        return NULL;

    X509_gmtime_adj(X509_get_notAfter(self->x509), i);

    Py_INCREF(Py_None);
    return Py_None;
}

static char crypto_X509_sign_doc[] = "\n\
Sign the certificate using the supplied key and digest\n\
\n\
Arguments: self - The X509 object\n\
           args - The Python argument tuple, should be:\n\
             pkey   - The key to sign with\n\
             digest - The message digest to use\n\
Returns:   None\n\
";

static PyObject *
crypto_X509_sign(crypto_X509Obj *self, PyObject *args)
{
    crypto_PKeyObj *pkey;
    char *digest_name;
    const EVP_MD *digest;

    if (!PyArg_ParseTuple(args, "O!s:sign", &crypto_PKey_Type, &pkey,
			  &digest_name))
        return NULL;

    if (pkey->only_public) {
	PyErr_SetString(PyExc_ValueError, "Key has only public part");
	return NULL;
    }

    if (!pkey->initialized) {
	PyErr_SetString(PyExc_ValueError, "Key is uninitialized");
	return NULL;
    }

    if ((digest = EVP_get_digestbyname(digest_name)) == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "No such digest method");
        return NULL;
    }

    if (!X509_sign(self->x509, pkey->pkey, digest))
    {
        exception_from_error_queue();
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static char crypto_X509_has_expired_doc[] = "\n\
Check whether the certificate has expired.\n\
\n\
Arguments: self - The X509 object\n\
           args - The Python argument tuple, should be empty\n\
Returns:   True if the certificate has expired, false otherwise\n\
";

static PyObject *
crypto_X509_has_expired(crypto_X509Obj *self, PyObject *args)
{
    time_t tnow;

    if (!PyArg_ParseTuple(args, ":has_expired"))
        return NULL;

    tnow = time(NULL);
    if (ASN1_UTCTIME_cmp_time_t(X509_get_notAfter(self->x509), tnow) < 0)
        return PyInt_FromLong(1L);
    else
        return PyInt_FromLong(0L);
}

static char crypto_X509_subject_name_hash_doc[] = "\n\
Return the hash of the X509 subject.\n\
\n\
Arguments: self - The X509 object\n\
           args - The Python argument tuple, should be empty\n\
Returns:   The hash of the subject\n\
";

static PyObject *
crypto_X509_subject_name_hash(crypto_X509Obj *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":subject_name_hash"))
        return NULL;

    return PyLong_FromLong(X509_subject_name_hash(self->x509));
}

static char crypto_X509_digest_doc[] = "\n\
Return the digest of the X509 object.\n\
\n\
Arguments: self - The X509 object\n\
           args - The Python argument tuple, should be empty\n\
Returns:   The digest of the object\n\
";

static PyObject *
crypto_X509_digest(crypto_X509Obj *self, PyObject *args)
{
    unsigned char fp[EVP_MAX_MD_SIZE];
    char *tmp;
    char *digest_name;
    unsigned int len,i;
    PyObject *ret;
    const EVP_MD *digest;

    if (!PyArg_ParseTuple(args, "s:digest", &digest_name))
        return NULL;

    if ((digest = EVP_get_digestbyname(digest_name)) == NULL)
    {
        PyErr_SetString(PyExc_ValueError, "No such digest method");
        return NULL;
    }

    if (!X509_digest(self->x509,digest,fp,&len))
    {
        exception_from_error_queue();
    }
    tmp = malloc(3*len+1);
    memset(tmp, 0, 3*len+1);
    for (i = 0; i < len; i++) {
        sprintf(tmp+i*3,"%02X:",fp[i]);
    }
    tmp[3*len-1] = 0;
    ret = PyString_FromStringAndSize(tmp,3*len-1);
    free(tmp);
    return ret;
}


static char crypto_X509_add_extensions_doc[] = "\n\
Add extensions to the certificate.\n\
\n\
Arguments: self - X509 object\n\
           args - The Python argument tuple, should be:\n\
             extensions - a sequence of X509Extension objects\n\
Returns:   None\n\
";

static PyObject *
crypto_X509_add_extensions(crypto_X509Obj *self, PyObject *args)
{   
    PyObject *extensions, *seq;
    crypto_X509ExtensionObj *ext;
    int nr_of_extensions, i;

    if (!PyArg_ParseTuple(args, "O:add_extensions", &extensions))
        return NULL;

    seq = PySequence_Fast(extensions, "Expected a sequence");
    if (seq == NULL)
        return NULL;

    nr_of_extensions = PySequence_Fast_GET_SIZE(seq);

    for (i = 0; i < nr_of_extensions; i++)
    { 
        ext = (crypto_X509ExtensionObj *)PySequence_Fast_GET_ITEM(seq, i);
        if (!crypto_X509Extension_Check(ext))
        {   
            Py_DECREF(seq);
            PyErr_SetString(PyExc_ValueError,
                            "One of the elements is not an X509Extension");
            return NULL;
        }
        if (!X509_add_ext(self->x509, ext->x509_extension, -1))
        {
            Py_DECREF(seq);
            exception_from_error_queue();
            return NULL;
        }
    }

    Py_INCREF(Py_None);
    return Py_None;
}

/*
 * ADD_METHOD(name) expands to a correct PyMethodDef declaration
 *   {  'name', (PyCFunction)crypto_X509_name, METH_VARARGS }
 * for convenience
 */
#define ADD_METHOD(name)        \
    { #name, (PyCFunction)crypto_X509_##name, METH_VARARGS, crypto_X509_##name##_doc }
static PyMethodDef crypto_X509_methods[] =
{
    ADD_METHOD(get_version),
    ADD_METHOD(set_version),
    ADD_METHOD(get_serial_number),
    ADD_METHOD(set_serial_number),
    ADD_METHOD(get_issuer),
    ADD_METHOD(set_issuer),
    ADD_METHOD(get_subject),
    ADD_METHOD(set_subject),
    ADD_METHOD(get_pubkey),
    ADD_METHOD(set_pubkey),
    ADD_METHOD(get_notBefore),
    ADD_METHOD(set_notBefore),
    ADD_METHOD(get_notAfter),
    ADD_METHOD(set_notAfter),
    ADD_METHOD(gmtime_adj_notBefore),
    ADD_METHOD(gmtime_adj_notAfter),
    ADD_METHOD(sign),
    ADD_METHOD(has_expired),
    ADD_METHOD(subject_name_hash),
    ADD_METHOD(digest),
    ADD_METHOD(add_extensions),
    { NULL, NULL }
};
#undef ADD_METHOD


/*
 * Constructor for X509 objects, never called by Python code directly
 *
 * Arguments: cert    - A "real" X509 certificate object
 *            dealloc - Boolean value to specify whether the destructor should
 *                      free the "real" X509 object
 * Returns:   The newly created X509 object
 */
crypto_X509Obj *
crypto_X509_New(X509 *cert, int dealloc)
{
    crypto_X509Obj *self;

    self = PyObject_New(crypto_X509Obj, &crypto_X509_Type);

    if (self == NULL)
        return NULL;

    self->x509 = cert;
    self->dealloc = dealloc;

    return self;
}

/*
 * Deallocate the memory used by the X509 object
 *
 * Arguments: self - The X509 object
 * Returns:   None
 */
static void
crypto_X509_dealloc(crypto_X509Obj *self)
{
    /* Sometimes we don't have to dealloc the "real" X509 pointer ourselves */
    if (self->dealloc)
        X509_free(self->x509);

    PyObject_Del(self);
}

/*
 * Find attribute
 *
 * Arguments: self - The X509 object
 *            name - The attribute name
 * Returns:   A Python object for the attribute, or NULL if something went
 *            wrong
 */
static PyObject *
crypto_X509_getattr(crypto_X509Obj *self, char *name)
{
    return Py_FindMethod(crypto_X509_methods, (PyObject *)self, name);
}

PyTypeObject crypto_X509_Type = {
    PyObject_HEAD_INIT(NULL)
    0,
    "X509",
    sizeof(crypto_X509Obj),
    0,
    (destructor)crypto_X509_dealloc,
    NULL, /* print */
    (getattrfunc)crypto_X509_getattr,
};

/*
 * Initialize the X509 part of the crypto sub module
 *
 * Arguments: dict - The crypto module dictionary
 * Returns:   None
 */
int
init_crypto_x509(PyObject *dict)
{
    crypto_X509_Type.ob_type = &PyType_Type;
    Py_INCREF(&crypto_X509_Type);
    PyDict_SetItemString(dict, "X509Type", (PyObject *)&crypto_X509_Type);
    return 1;
}


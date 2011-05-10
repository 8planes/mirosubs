/*
 * pkey.c
 *
 * Copyright (C) AB Strakt 2001, All rights reserved
 * Copyright (C) Jean-Paul Calderone 2008, All rights reserved
 *
 * Public/rivate key handling code, mostly thin wrappers around OpenSSL.
 * See the file RATIONALE for a short explanation of why this module was written.
 *
 */
#include <Python.h>
#define crypto_MODULE
#include "crypto.h"

/*
 * This is done every time something fails, so turning it into a macro is
 * really nice.
 *
 * Arguments:   None
 * Returns:     Doesn't return
 */
#define FAIL() \
do {                                    \
    exception_from_error_queue();       \
    return NULL;                        \
} while (0)
    

static char crypto_PKey_generate_key_doc[] = "\n\
Generate a key of a given type, with a given number of a bits\n\
\n\
Arguments: self - The PKey object\n\
           args - The Python argument tuple, should be:\n\
             type - The key type (TYPE_RSA or TYPE_DSA)\n\
             bits - The number of bits\n\
Returns:   None\n\
";

static PyObject *
crypto_PKey_generate_key(crypto_PKeyObj *self, PyObject *args)
{
    int type, bits;
    RSA *rsa;
    DSA *dsa;

    if (!PyArg_ParseTuple(args, "ii:generate_key", &type, &bits))
        return NULL;

    switch (type)
    {
        case crypto_TYPE_RSA:
            if (bits <= 0) {
                PyErr_SetString(PyExc_ValueError, "Invalid number of bits");
                return NULL;
            }
            if ((rsa = RSA_generate_key(bits, 0x10001, NULL, NULL)) == NULL)
                FAIL();
            if (!EVP_PKEY_assign_RSA(self->pkey, rsa))
                FAIL();
	    break;

        case crypto_TYPE_DSA:
            if ((dsa = DSA_generate_parameters(bits, NULL, 0, NULL, NULL, NULL, NULL)) == NULL)
                FAIL();
            if (!DSA_generate_key(dsa))
                FAIL();
            if (!EVP_PKEY_assign_DSA(self->pkey, dsa))
                FAIL();
	    break;

        default:
	    PyErr_SetString(crypto_Error, "No such key type");
	    return NULL;

    }
    self->initialized = 1;
    Py_INCREF(Py_None);
    return Py_None;
}

static char crypto_PKey_bits_doc[] = "\n\
Returns the number of bits of the key\n\
\n\
Arguments: self - The PKey object\n\
           args - The Python argument tuple, should be empty\n\
Returns: The number of bits of the key.\n\
";

static PyObject *
crypto_PKey_bits(crypto_PKeyObj *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":bits"))
        return NULL;

    return PyInt_FromLong(EVP_PKEY_bits(self->pkey));
}

static char crypto_PKey_type_doc[] = "\n\
Returns the type of the key\n\
\n\
Arguments: self - The PKey object\n\
           args - The Python argument tuple, should be empty\n\
Returns: The type of the key.\n\
";

static PyObject *
crypto_PKey_type(crypto_PKeyObj *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":type"))
        return NULL;

    return PyInt_FromLong(self->pkey->type);
}


/*
 * ADD_METHOD(name) expands to a correct PyMethodDef declaration
 *   {  'name', (PyCFunction)crypto_PKey_name, METH_VARARGS }
 * for convenience
 */
#define ADD_METHOD(name)        \
    { #name, (PyCFunction)crypto_PKey_##name, METH_VARARGS, crypto_PKey_##name##_doc }
static PyMethodDef crypto_PKey_methods[] =
{
    ADD_METHOD(generate_key),
    ADD_METHOD(bits),
    ADD_METHOD(type),
    { NULL, NULL }
};
#undef ADD_METHOD


/*
 * Constructor for PKey objects, never called by Python code directly
 *
 * Arguments: pkey    - A "real" EVP_PKEY object
 *            dealloc - Boolean value to specify whether the destructor should
 *                      free the "real" EVP_PKEY object
 * Returns:   The newly created PKey object
 */
crypto_PKeyObj *
crypto_PKey_New(EVP_PKEY *pkey, int dealloc)
{
    crypto_PKeyObj *self;

    self = PyObject_New(crypto_PKeyObj, &crypto_PKey_Type);

    if (self == NULL)
        return NULL;

    self->pkey = pkey;
    self->dealloc = dealloc;
    self->only_public = 0;

    /*
     * Heuristic.  Most call-sites pass an initialized EVP_PKEY.  Not
     * necessarily the case that they will, though.  That's part of why this is
     * a hack. -exarkun
     */
    self->initialized = 1;

    return self;
}

/*
 * Deallocate the memory used by the PKey object
 *
 * Arguments: self - The PKey object
 * Returns:   None
 */
static void
crypto_PKey_dealloc(crypto_PKeyObj *self)
{
    /* Sometimes we don't have to dealloc the "real" EVP_PKEY pointer ourselves */
    if (self->dealloc)
        EVP_PKEY_free(self->pkey);

    PyObject_Del(self);
}

/*
 * Find attribute
 *
 * Arguments: self - The PKey object
 *            name - The attribute name
 * Returns:   A Python object for the attribute, or NULL if something went
 *            wrong
 */
static PyObject *
crypto_PKey_getattr(crypto_PKeyObj *self, char *name)
{
    return Py_FindMethod(crypto_PKey_methods, (PyObject *)self, name);
}

PyTypeObject crypto_PKey_Type = {
    PyObject_HEAD_INIT(NULL)
    0,
    "PKey",
    sizeof(crypto_PKeyObj),
    0,
    (destructor)crypto_PKey_dealloc,
    NULL, /* print */
    (getattrfunc)crypto_PKey_getattr,
    NULL, /* setattr */
    NULL, /* compare */
    NULL, /* repr */
    NULL, /* as_number */
    NULL, /* as_sequence */
    NULL, /* as_mapping */
    NULL, /* hash */
};


/*
 * Initialize the PKey part of the crypto sub module
 *
 * Arguments: dict - The crypto module dictionary
 * Returns:   None
 */
int
init_crypto_pkey(PyObject *dict)
{
    crypto_PKey_Type.ob_type = &PyType_Type;
    Py_INCREF(&crypto_PKey_Type);
    PyDict_SetItemString(dict, "PKeyType", (PyObject *)&crypto_PKey_Type);
    return 1;
}


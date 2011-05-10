/*
 * rand.c
 *
 * Copyright (C) AB Strakt 2001, All rights reserved
 *
 * PRNG management routines, thin wrappers.
 * See the file RATIONALE for a short explanation of why this module was written.
 *
 * Reviewed 2001-07-23
 */
#include <Python.h>

/* 
 * In order to get the RAND_screen definition from the rand.h
 * WIN32 or WINDOWS needs to be defined, otherwise we get a
 * warning.
 */
#ifdef MS_WINDOWS
#  ifndef WIN32
#      define WIN32
#  endif
#endif
#include <openssl/rand.h>

static char rand_doc[] = "\n\
PRNG management routines, thin wrappers.\n\
See the file RATIONALE for a short explanation of why this module was written.\n\
";

static char rand_add_doc[] = "\n\
Add data with a given entropy to the PRNG\n\
\n\
Arguments: spam - Always NULL\n\
           args - The Python argument tuple, should be:\n\
             buffer  - Buffer with random data\n\
             entropy - The entropy (in bytes) measurement of the buffer\n\
Returns:   None\n\
";

static PyObject *
rand_add(PyObject *spam, PyObject *args)
{
    char *buf;
    int size;
    double entropy;

    if (!PyArg_ParseTuple(args, "s#d:add", &buf, &size, &entropy))
        return NULL;

    RAND_add(buf, size, entropy);

    Py_INCREF(Py_None);
    return Py_None;
}

static char rand_seed_doc[] = "\n\
Alias for rand_add, with entropy equal to length\n\
\n\
Arguments: spam - Always NULL\n\
           args - The Python argument tuple, should be:\n\
             buffer - Buffer with random data\n\
Returns:   None\n\
";

static PyObject *
rand_seed(PyObject *spam, PyObject *args)
{
    char *buf;
    int size;

    if (!PyArg_ParseTuple(args, "s#:seed", &buf, &size))
        return NULL;

    RAND_seed(buf, size);

    Py_INCREF(Py_None);
    return Py_None;
}

static char rand_status_doc[] = "\n\
Retrieve the status of the PRNG\n\
\n\
Arguments: spam - Always NULL\n\
           args - The Python argument tuple, should be empty\n\
Returns:   True if the PRNG is seeded enough, false otherwise\n\
";

static PyObject *
rand_status(PyObject *spam, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":status"))
        return NULL;

    return PyInt_FromLong((long)RAND_status());
}

#ifdef MS_WINDOWS
static char rand_screen_doc[] = "\n\
Add the current contents of the screen to the PRNG state. Availability:\n\
Windows.\n\
\n\
Arguments: spam - Always NULL\n\
           args - The Python argument tuple, should be empty\n\
Returns:   None\n\
";

static PyObject *
rand_screen(PyObject *spam, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":screen"))
        return NULL;

    RAND_screen();
    Py_INCREF(Py_None);
    return Py_None;
}
#endif

static char rand_egd_doc[] = "\n\
Query an entropy gathering daemon (EGD) for random data and add it to the\n\
PRNG. I haven't found any problems when the socket is missing, the function\n\
just returns 0.\n\
\n\
Arguments: spam - Always NULL\n\
           args - The Python argument tuple, should be:\n\
             path  - The path to the EGD socket\n\
             bytes - (optional) The number of bytes to read, default is 255\n\
Returns:   The number of bytes read (NB: a value of 0 isn't necessarily an\n\
           error, check rand.status())\n\
";

static PyObject *
rand_egd(PyObject *spam, PyObject *args)
{
    char *path;
    int bytes = 255;

    if (!PyArg_ParseTuple(args, "s|i:egd", &path, &bytes))
        return NULL;

    return PyInt_FromLong((long)RAND_egd_bytes(path, bytes));
}

static char rand_cleanup_doc[] = "\n\
Erase the memory used by the PRNG.\n\
\n\
Arguments: spam - Always NULL\n\
           args - The Python argument tuple, should be empty\n\
Returns:   None\n\
";

static PyObject *
rand_cleanup(PyObject *spam, PyObject *args)
{
    if (!PyArg_ParseTuple(args, ":cleanup"))
        return NULL;

    RAND_cleanup();

    Py_INCREF(Py_None);
    return Py_None;
}

static char rand_load_file_doc[] = "\n\
Seed the PRNG with data from a file\n\
\n\
Arguments: spam - Always NULL\n\
           args - The Python argument tuple, should be:\n\
             filename - The file to read data from\n\
             maxbytes - (optional) The number of bytes to read, default is\n\
                        to read the entire file\n\
Returns:   The number of bytes read\n\
";

static PyObject *
rand_load_file(PyObject *spam, PyObject *args)
{
    char *filename;
    int maxbytes = -1;

    if (!PyArg_ParseTuple(args, "s|i:load_file", &filename, &maxbytes))
        return NULL;

    return PyInt_FromLong((long)RAND_load_file(filename, maxbytes));
}

static char rand_write_file_doc[] = "\n\
Save PRNG state to a file\n\
\n\
Arguments: spam - Always NULL\n\
           args - The Python argument tuple, should be:\n\
             filename - The file to write data to\n\
Returns:   The number of bytes written\n\
";

static PyObject *
rand_write_file(PyObject *spam, PyObject *args)
{
    char *filename;

    if (!PyArg_ParseTuple(args, "s:write_file", &filename))
        return NULL;

    return PyInt_FromLong((long)RAND_write_file(filename));
}


/* Methods in the OpenSSL.rand module */
static PyMethodDef rand_methods[] = {
    { "add",       (PyCFunction)rand_add,          METH_VARARGS, rand_add_doc },
    { "seed",      (PyCFunction)rand_seed,         METH_VARARGS, rand_seed_doc },
    { "status",    (PyCFunction)rand_status,       METH_VARARGS, rand_status_doc },
#ifdef MS_WINDOWS
    { "screen",    (PyCFunction)rand_screen,       METH_VARARGS, rand_screen_doc },
#endif
    { "egd",       (PyCFunction)rand_egd,          METH_VARARGS, rand_egd_doc },
    { "cleanup",   (PyCFunction)rand_cleanup,      METH_VARARGS, rand_cleanup_doc },
    { "load_file", (PyCFunction)rand_load_file,    METH_VARARGS, rand_load_file_doc },
    { "write_file",(PyCFunction)rand_write_file,   METH_VARARGS, rand_write_file_doc },
    { NULL, NULL }
};


/*
 * Initialize the rand sub module
 *
 * Arguments: None
 * Returns:   None
 */
void
initrand(void)
{
    PyObject *module;

    ERR_load_RAND_strings();

    if ((module = Py_InitModule3("rand", rand_methods, rand_doc)) == NULL)
        return;
}


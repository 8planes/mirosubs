
/*
 *  _fastmath.c: Accelerator module that uses GMP for faster numerics.
 *
 * Part of the Python Cryptography Toolkit
 *
 * Written by Paul Swartz, Andrew Kuchling, Joris Bontje, and others
 *
 * ===================================================================
 * The contents of this file are dedicated to the public domain.  To
 * the extent that dedication to the public domain is not available,
 * everyone is granted a worldwide, perpetual, royalty-free,
 * non-exclusive license to exercise all rights associated with the
 * contents of this file for any purpose whatsoever.
 * No rights are reserved.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
 * BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
 * ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 * ===================================================================
 *
 * $Id$
 */

#include <stdio.h>
#include <string.h>
#include <Python.h>
#include <longintrepr.h>				/* for conversions */
#include <gmp.h>

static void
longObjToMPZ (mpz_t m, PyLongObject * p)
{
	int size, i;
	mpz_t temp, temp2;
	mpz_init (temp);
	mpz_init (temp2);
	if (p->ob_size > 0)
		size = p->ob_size;
	else
		size = -p->ob_size;
	mpz_set_ui (m, 0);
	for (i = 0; i < size; i++)
	{
		mpz_set_ui (temp, p->ob_digit[i]);
		mpz_mul_2exp (temp2, temp, SHIFT * i);
		mpz_add (m, m, temp2);
	}
	mpz_clear (temp);
	mpz_clear (temp2);
}

static PyObject *
mpzToLongObj (mpz_t m)
{
	/* borrowed from gmpy */
	int size = (mpz_sizeinbase (m, 2) + SHIFT - 1) / SHIFT;
	int i;
	mpz_t temp;
	PyLongObject *l = _PyLong_New (size);
	if (!l)
		return NULL;
	mpz_init_set (temp, m);
	for (i = 0; i < size; i++)
	{
		l->ob_digit[i] = (digit) (mpz_get_ui (temp) & MASK);
		mpz_fdiv_q_2exp (temp, temp, SHIFT);
	}
	i = size;
	while ((i > 0) && (l->ob_digit[i - 1] == 0))
		i--;
	l->ob_size = i;
	mpz_clear (temp);
	return (PyObject *) l;
}

typedef struct
{
	PyObject_HEAD mpz_t y;
	mpz_t g;
	mpz_t p;
	mpz_t q;
	mpz_t x;
}
dsaKey;

typedef struct
{
	PyObject_HEAD mpz_t n;
	mpz_t e;
	mpz_t d;
	mpz_t p;
	mpz_t q;
	mpz_t u;
}
rsaKey;

static PyObject *rsaKey_new (PyObject *, PyObject *);
static PyObject *dsaKey_new (PyObject *, PyObject *);

static void dsaKey_dealloc (dsaKey *);
static PyObject *dsaKey_getattr (dsaKey *, char *);
static PyObject *dsaKey__sign (dsaKey *, PyObject *);
static PyObject *dsaKey__verify (dsaKey *, PyObject *);
static PyObject *dsaKey_size (dsaKey *, PyObject *);
static PyObject *dsaKey_has_private (dsaKey *, PyObject *);

static void rsaKey_dealloc (rsaKey *);
static PyObject *rsaKey_getattr (rsaKey *, char *);
static PyObject *rsaKey__encrypt (rsaKey *, PyObject *);
static PyObject *rsaKey__decrypt (rsaKey *, PyObject *);
static PyObject *rsaKey__verify (rsaKey *, PyObject *);
static PyObject *rsaKey__blind (rsaKey *, PyObject *);
static PyObject *rsaKey__unblind (rsaKey *, PyObject *);
static PyObject *rsaKey_size (rsaKey *, PyObject *);
static PyObject *rsaKey_has_private (rsaKey *, PyObject *);

static int
dsaSign (dsaKey * key, mpz_t m, mpz_t k, mpz_t r, mpz_t s)
{
	mpz_t temp;
	if (mpz_cmp_ui (k, 2) < 0 || mpz_cmp (k, key->q) >= 0)
	{
		return 1;
	}
	mpz_init (temp);
	mpz_powm (r, key->g, k, key->p);
	mpz_mod (r, r, key->q);
	mpz_invert (s, k, key->q);
	mpz_mul (temp, key->x, r);
	mpz_add (temp, m, temp);
	mpz_mul (s, s, temp);
	mpz_mod (s, s, key->q);
	mpz_clear (temp);
	return 0;
}

static int
dsaVerify (dsaKey * key, mpz_t m, mpz_t r, mpz_t s)
{
	int result;
	mpz_t u1, u2, v1, v2, w;
	if (mpz_cmp_ui (r, 0) <= 0 || mpz_cmp (r, key->q) >= 0 ||
	    mpz_cmp_ui (s, 0) <= 0 || mpz_cmp (s, key->q) >= 0)
		return 0;
	mpz_init (u1);
	mpz_init (u2);
	mpz_init (v1);
	mpz_init (v2);
	mpz_init (w);
	mpz_invert (w, s, key->q);
	mpz_mul (u1, m, w);
	mpz_mod (u1, u1, key->q);
	mpz_mul (u2, r, w);
	mpz_mod (u2, u2, key->q);
	mpz_powm (v1, key->g, u1, key->p);
	mpz_powm (v2, key->y, u2, key->p);
	mpz_mul (w, v1, v2);
	mpz_mod (w, w, key->p);
	mpz_mod (w, w, key->q);
	if (mpz_cmp (r, w) == 0)
		result = 1;
	else
		result = 0;
	mpz_clear (u1);
	mpz_clear (u2);
	mpz_clear (v1);
	mpz_clear (v2);
	mpz_clear (w);
	return result;
}


static int
rsaEncrypt (rsaKey * key, mpz_t v)
{
	if (mpz_cmp (v, key->n) >= 0)
	{
		return 1;
	}
	mpz_powm (v, v, key->e, key->n);
	return 0;
}

static int
rsaDecrypt (rsaKey * key, mpz_t v)
{
    mpz_t m1, m2, h;
	if (mpz_cmp (v, key->n) >= 0)
	{
		return 1;
	}
	if (mpz_size (key->d) == 0)
	{
		return 2;
	}

    if ((mpz_size (key->p) != 0) && (mpz_size (key->q) != 0) && 
        (mpz_size (key->u) != 0))
    {
        /* fast path */
        mpz_init(m1);
        mpz_init(m2);
        mpz_init(h);

        /* m1 = c ^ (d mod (p-1)) mod p */
        mpz_sub_ui(h, key->p, 1);
        mpz_fdiv_r(h, key->d, h);
        mpz_powm(m1, v, h, key->p);
        /* m2 = c ^ (d mod (q-1)) mod q */
        mpz_sub_ui(h, key->q, 1);
        mpz_fdiv_r(h, key->d, h);
        mpz_powm(m2, v, h, key->q);
        /* h = u * ( m2 - m1 ) mod q */
        mpz_sub(h, m2, m1);
        if (mpz_sgn(h)==-1)
            mpz_add(h, h, key->q);
        mpz_mul(h, key->u, h);
        mpz_mod(h, h, key->q);
        /* m = m2 + h * p */
        mpz_mul(h, h, key->p);
        mpz_add(v, m1, h);
        /* ready */

        mpz_clear(m1);
        mpz_clear(m2);
        mpz_clear(h);
        return 0;
    }

    /* slow */
	mpz_powm (v, v, key->d, key->n);
	return 0;
}

static int
rsaBlind (rsaKey * key, mpz_t v, mpz_t b)
{
    if (mpz_cmp (v, key->n) >= 0)
        {
            return 1;
        }
    if (mpz_cmp (b, key->n) >= 0)
        {
            return 2;
        }
    mpz_powm (b, b, key->e, key->n);
    mpz_mul (v, v, b);
    mpz_mod (v, v, key->n);
    return 0;
}

static int
rsaUnBlind (rsaKey * key, mpz_t v, mpz_t b)
{
    if (mpz_cmp (v, key->n) >= 0)
        {
            return 1;
        }
    if (mpz_cmp (b, key->n) >= 0)
        {
            return 2;
        }
    if (!mpz_invert (b, b, key->n))
        {
            return 3;
        }
    mpz_mul (v, v, b);
    mpz_mod (v, v, key->n);
    return 0;
}
 

static PyTypeObject dsaKeyType = {
	PyObject_HEAD_INIT (NULL) 0,
	"dsaKey",
	sizeof (dsaKey),
	0,
	(destructor) dsaKey_dealloc,	/* dealloc */
	0,				/* print */
	(getattrfunc) dsaKey_getattr,	/* getattr */
	0,				/* setattr */
	0,				/* compare */
	0,				/* repr */
	0,				/* as_number */
	0,				/* as_sequence */
	0,				/* as_mapping */
	0,				/* hash */
	0,				/* call */
};

static PyMethodDef dsaKey__methods__[] = {
	{"_sign", (PyCFunction) dsaKey__sign, METH_VARARGS, 
	 "Sign the given long."},
	{"_verify", (PyCFunction) dsaKey__verify, METH_VARARGS,
	 "Verify that the signature is valid."},
	{"size", (PyCFunction) dsaKey_size, METH_VARARGS,
	 "Return the number of bits that this key can handle."},
	{"has_private", (PyCFunction) dsaKey_has_private, METH_VARARGS,
	 "Return 1 or 0 if this key does/doesn't have a private key."},
	{NULL, NULL, 0, NULL}
};

static PyObject *fastmathError;							/* raised on errors */

static PyTypeObject rsaKeyType = {
	PyObject_HEAD_INIT (NULL) 0,
	"rsaKey",
	sizeof (rsaKey),
	0,
	(destructor) rsaKey_dealloc,	/* dealloc */
	0,				/* print */
	(getattrfunc) rsaKey_getattr,	/* getattr */
	0,                              /* setattr */
	0,				/* compare */
	0,				/* repr */
	0,				/* as_number */
	0,				/* as_sequence */
	0,				/* as_mapping */
	0,				/* hash */
	0,				/* call */
};

static PyMethodDef rsaKey__methods__[] = {
	{"_encrypt", (PyCFunction) rsaKey__encrypt, METH_VARARGS,
	 "Encrypt the given long."},
	{"_decrypt", (PyCFunction) rsaKey__decrypt, METH_VARARGS,
	 "Decrypt the given long."},
	{"_sign", (PyCFunction) rsaKey__decrypt, METH_VARARGS,
	 "Sign the given long."},
	{"_verify", (PyCFunction) rsaKey__verify, METH_VARARGS,
	 "Verify that the signature is valid."},
 	{"_blind", (PyCFunction) rsaKey__blind, METH_VARARGS,
 	 "Blind the given long."},
 	{"_unblind", (PyCFunction) rsaKey__unblind, METH_VARARGS,
 	 "Unblind the given long."},
	{"size", (PyCFunction) rsaKey_size, METH_VARARGS,
	 "Return the number of bits that this key can handle."},
	{"has_private", (PyCFunction) rsaKey_has_private, METH_VARARGS,
	 "Return 1 or 0 if this key does/doesn't have a private key."},
	{NULL, NULL, 0, NULL}
};

static PyObject *
dsaKey_new (PyObject * self, PyObject * args)
{
	PyLongObject *y = NULL, *g = NULL, *p = NULL, *q = NULL, *x = NULL;
	dsaKey *key;
	if (!PyArg_ParseTuple(args, "O!O!O!O!|O!", &PyLong_Type, &y,
			      &PyLong_Type, &g, &PyLong_Type, &p, 
			      &PyLong_Type, &q, &PyLong_Type, &x))
		return NULL;

	key = PyObject_New (dsaKey, &dsaKeyType);
	mpz_init (key->y);
	mpz_init (key->g);
	mpz_init (key->p);
	mpz_init (key->q);
	mpz_init (key->x);
	longObjToMPZ (key->y, y);
	longObjToMPZ (key->g, g);
	longObjToMPZ (key->p, p);
	longObjToMPZ (key->q, q);
	if (x)
	{
		longObjToMPZ (key->x, x);
	}
	return (PyObject *) key;
}

static void
dsaKey_dealloc (dsaKey * key)
{
	mpz_clear (key->y);
	mpz_clear (key->g);
	mpz_clear (key->p);
	mpz_clear (key->q);
	mpz_clear (key->x);
	PyObject_Del (key);
}

static PyObject *
dsaKey_getattr (dsaKey * key, char *attr)
{
	if (strcmp (attr, "y") == 0)
		return mpzToLongObj (key->y);
	else if (strcmp (attr, "g") == 0)
		return mpzToLongObj (key->g);
	else if (strcmp (attr, "p") == 0)
		return mpzToLongObj (key->p);
	else if (strcmp (attr, "q") == 0)
		return mpzToLongObj (key->q);
	else if (strcmp (attr, "x") == 0)
	{
		if (mpz_size (key->x) == 0)
		{
			PyErr_SetString (PyExc_AttributeError,
					 "dsaKey instance has no attribute 'x'");
			return NULL;
		}
		return mpzToLongObj (key->x);
	}
	else
	{
		return Py_FindMethod (dsaKey__methods__, (PyObject *) key, attr);
	}
}

static PyObject *
dsaKey__sign (dsaKey * key, PyObject * args)
{
	PyObject *lm, *lk, *lr, *ls;
	mpz_t m, k, r, s;
	int result;
	if (!PyArg_ParseTuple (args, "O!O!", &PyLong_Type, &lm,
			       &PyLong_Type, &lk))
	{
		return NULL;
	}
	mpz_init (m);
	mpz_init (k);
	mpz_init (r);
	mpz_init (s);
	longObjToMPZ (m, (PyLongObject *) lm);
	longObjToMPZ (k, (PyLongObject *) lk);
	result = dsaSign (key, m, k, r, s);
	if (result == 1)
	{
		PyErr_SetString (PyExc_ValueError, "K not between 2 and q");
		return NULL;
	}
	lr = mpzToLongObj (r);
	ls = mpzToLongObj (s);
	mpz_clear (m);
	mpz_clear (k);
	mpz_clear (r);
	mpz_clear (s);
	return Py_BuildValue ("(NN)", lr, ls);
}

static PyObject *
dsaKey__verify (dsaKey * key, PyObject * args)
{
	PyObject *lm, *lr, *ls;
	mpz_t m, r, s;
	int result;
	if (!PyArg_ParseTuple (args, "O!O!O!", &PyLong_Type, &lm,
			       &PyLong_Type, &lr, &PyLong_Type, &ls))
	{
		return NULL;
	}
	mpz_init (m);
	mpz_init (r);
	mpz_init (s);
	longObjToMPZ (m, (PyLongObject *) lm);
	longObjToMPZ (r, (PyLongObject *) lr);
	longObjToMPZ (s, (PyLongObject *) ls);
	result = dsaVerify (key, m, r, s);
	mpz_clear (m);
	mpz_clear (r);
	mpz_clear (s);
	if (result) {
		Py_INCREF(Py_True);
		return Py_True;
        } else {
		Py_INCREF(Py_False);
		return Py_False;
	}
}

static PyObject *
dsaKey_size (dsaKey * key, PyObject * args)
{
	if (!PyArg_ParseTuple (args, ""))
		return NULL;
	return Py_BuildValue ("i", mpz_sizeinbase (key->p, 2) - 1);
}

static PyObject *
dsaKey_has_private (dsaKey * key, PyObject * args)
{
	if (!PyArg_ParseTuple (args, ""))
		return NULL;
	if (mpz_size (key->x) == 0) {
		Py_INCREF(Py_False);
		return Py_False;
        } else {
		Py_INCREF(Py_True);
		return Py_True;
        }
}

static PyObject *
rsaKey_new (PyObject * self, PyObject * args)
{
	PyLongObject *n = NULL, *e = NULL, *d = NULL, *p = NULL, *q = NULL, 
                     *u = NULL;
	rsaKey *key;

	if (!PyArg_ParseTuple(args, "O!O!|O!O!O!O!", &PyLong_Type, &n,
			      &PyLong_Type, &e, &PyLong_Type, &d, 
			      &PyLong_Type, &p, &PyLong_Type, &q,
                              &PyLong_Type, &u))
		return NULL;

	key = PyObject_New (rsaKey, &rsaKeyType);
	mpz_init (key->n);
	mpz_init (key->e);
	mpz_init (key->d);
	mpz_init (key->p);
	mpz_init (key->q);
	mpz_init (key->u);
	longObjToMPZ (key->n, n);
	longObjToMPZ (key->e, e);
	if (!d)
	{
		return (PyObject *) key;
	}
	longObjToMPZ (key->d, d);
	if (p && q)
	{
		longObjToMPZ (key->p, p);
		longObjToMPZ (key->q, q);
		if (u) {
			longObjToMPZ (key->u, u);
		} else {
			mpz_invert (key->u, key->p, key->q);
		}
	}
	return (PyObject *) key;
}

static void
rsaKey_dealloc (rsaKey * key)
{
	mpz_clear (key->n);
	mpz_clear (key->e);
	mpz_clear (key->d);
	mpz_clear (key->p);
	mpz_clear (key->q);
	mpz_clear (key->u);
	PyObject_Del (key);
}

static PyObject *
rsaKey_getattr (rsaKey * key, char *attr)
{
	if (strcmp (attr, "n") == 0)
		return mpzToLongObj (key->n);
	else if (strcmp (attr, "e") == 0)
		return mpzToLongObj (key->e);
	else if (strcmp (attr, "d") == 0)
	{
		if (mpz_size (key->d) == 0)
		{
			PyErr_SetString(PyExc_AttributeError,
					"rsaKey instance has no attribute 'd'");
			return NULL;
		}
		return mpzToLongObj (key->d);
	}
	else if (strcmp (attr, "p") == 0)
	{
		if (mpz_size (key->p) == 0)
		{
			PyErr_SetString(PyExc_AttributeError,
					"rsaKey instance has no attribute 'p'");
			return NULL;
		}
		return mpzToLongObj (key->p);
	}
	else if (strcmp (attr, "q") == 0)
	{
		if (mpz_size (key->q) == 0)
		{
			PyErr_SetString(PyExc_AttributeError,
					"rsaKey instance has no attribute 'q'");
			return NULL;
		}
		return mpzToLongObj (key->q);
	}
	else if (strcmp (attr, "u") == 0)
	{
		if (mpz_size (key->u) == 0)
		{
			PyErr_SetString(PyExc_AttributeError,
					"rsaKey instance has no attribute 'u'");
			return NULL;
		}
		return mpzToLongObj (key->u);
	}
	else
	{
		return Py_FindMethod (rsaKey__methods__, 
				      (PyObject *) key, attr);
	}
}

static PyObject *
rsaKey__encrypt (rsaKey * key, PyObject * args)
{
	PyObject *l, *r;
	mpz_t v;
	int result;
	if (!PyArg_ParseTuple (args, "O!", &PyLong_Type, &l))
	{
		return NULL;
	}
	mpz_init (v);
	longObjToMPZ (v, (PyLongObject *) l);
	result = rsaEncrypt (key, v);
	if (result == 1)
	{
		PyErr_SetString (PyExc_ValueError, "Plaintext too large");
		return NULL;
	}
	r = (PyObject *) mpzToLongObj (v);
	mpz_clear (v);
	return Py_BuildValue ("N", r);
}

static PyObject *
rsaKey__decrypt (rsaKey * key, PyObject * args)
{
	PyObject *l, *r;
	mpz_t v;
	int result;
	if (!PyArg_ParseTuple (args, "O!", &PyLong_Type, &l))
	{
		return NULL;
	}
	mpz_init (v);
	longObjToMPZ (v, (PyLongObject *) l);
	result = rsaDecrypt (key, v);
	if (result == 1)
	{
		PyErr_SetString (PyExc_ValueError,
				 "Ciphertext too large");
		return NULL;
	}
	else if (result == 2)
	{
		PyErr_SetString (PyExc_TypeError,
				 "Private key not available in this object");
		return NULL;
	}
	r = mpzToLongObj (v);
	mpz_clear (v);
	return Py_BuildValue ("N", r);
}

static PyObject *
rsaKey__verify (rsaKey * key, PyObject * args)
{
	PyObject *l, *lsig;
	mpz_t v, vsig;
	if (!PyArg_ParseTuple(args, "O!O!", 
			      &PyLong_Type, &l, &PyLong_Type, &lsig))
	{
		return NULL;
	}
	mpz_init (v);
	mpz_init (vsig);
	longObjToMPZ (v, (PyLongObject *) l);
	longObjToMPZ (vsig, (PyLongObject *) lsig);
	rsaEncrypt (key, vsig);
	if (mpz_cmp (v, vsig) == 0) {
		Py_INCREF(Py_True);
		return Py_True;
	}
	else {
		Py_INCREF(Py_False);
		return Py_False;
        }
}

static PyObject *
rsaKey__blind (rsaKey * key, PyObject * args)
{
	PyObject *l, *lblind, *r;
	mpz_t v, vblind;
	int result;
	if (!PyArg_ParseTuple (args, "O!O!", &PyLong_Type, &l, 
                               &PyLong_Type, &lblind))
		{
			return NULL;
		}
	mpz_init (v);
	mpz_init (vblind);
	longObjToMPZ (v, (PyLongObject *) l);
	longObjToMPZ (vblind, (PyLongObject *) lblind);
	result = rsaBlind (key, v, vblind);
	if (result == 1)
		{
			PyErr_SetString (PyExc_ValueError, "Message too large");
			return NULL;
		}
	else if (result == 2)
		{
			PyErr_SetString (PyExc_ValueError, "Blinding factor too large");
			return NULL;
		}
	r = (PyObject *) mpzToLongObj (v);
	mpz_clear (v);
	mpz_clear (vblind);
	return Py_BuildValue ("N", r);
}

static PyObject *
rsaKey__unblind (rsaKey * key, PyObject * args)
{
	PyObject *l, *lblind, *r;
	mpz_t v, vblind;
	int result;
	if (!PyArg_ParseTuple (args, "O!O!", &PyLong_Type, &l, 
                               &PyLong_Type, &lblind))
		{
			return NULL;
		}
	mpz_init (v);
	mpz_init (vblind);
	longObjToMPZ (v, (PyLongObject *) l);
	longObjToMPZ (vblind, (PyLongObject *) lblind);
	result = rsaUnBlind (key, v, vblind);
	if (result == 1)
		{
			PyErr_SetString (PyExc_ValueError, "Message too large");
			return NULL;
		}
	else if (result == 2)
		{
			PyErr_SetString (PyExc_ValueError, "Blinding factor too large");
			return NULL;
		}
	else if (result == 3)
		{
			PyErr_SetString (PyExc_ValueError, "Inverse doesn't exist");
			return NULL;
		}
	r = (PyObject *) mpzToLongObj (v);
	mpz_clear (v);
	mpz_clear (vblind);
	return Py_BuildValue ("N", r);
}

static PyObject *
rsaKey_size (rsaKey * key, PyObject * args)
{
	if (!PyArg_ParseTuple (args, ""))
		return NULL;
	return Py_BuildValue ("i", mpz_sizeinbase (key->n, 2) - 1);
}

static PyObject *
rsaKey_has_private (rsaKey * key, PyObject * args)
{
	if (!PyArg_ParseTuple (args, ""))
		return NULL;
	if (mpz_size (key->d) == 0) {
		Py_INCREF(Py_False);
		return Py_False;
        } else {
		Py_INCREF(Py_True);
		return Py_True;
	}
}


static PyObject *
isPrime (PyObject * self, PyObject * args)
{
	PyObject *l;
	mpz_t n;
	int result;

	if (!PyArg_ParseTuple (args, "O!", &PyLong_Type, &l))
	{
		return NULL;
	}
	mpz_init (n);
	longObjToMPZ (n, (PyLongObject *) l);

	Py_BEGIN_ALLOW_THREADS;
	result = mpz_probab_prime_p(n, 5);
	Py_END_ALLOW_THREADS;

	mpz_clear (n);

	if (result == 0) {
		Py_INCREF(Py_False);
		return Py_False;
        } else {
		Py_INCREF(Py_True);
		return Py_True;
	}
}


static PyMethodDef _fastmath__methods__[] = {
	{"dsa_construct", dsaKey_new, METH_VARARGS},
	{"rsa_construct", rsaKey_new, METH_VARARGS},
        {"isPrime", isPrime, METH_VARARGS},
	{NULL, NULL}
};

void
init_fastmath (void)
{
        PyObject *_fastmath_module;
        PyObject *_fastmath_dict;

	rsaKeyType.ob_type = &PyType_Type;
	dsaKeyType.ob_type = &PyType_Type;
	_fastmath_module = Py_InitModule ("_fastmath", _fastmath__methods__);
	_fastmath_dict = PyModule_GetDict (_fastmath_module);
	fastmathError = PyErr_NewException ("_fastmath.error", NULL, NULL);
	PyDict_SetItemString (_fastmath_dict, "error", fastmathError);
}

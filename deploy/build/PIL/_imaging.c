/*
 * The Python Imaging Library.
 *
 * the imaging library bindings
 *
 * history:
 * 1995-09-24 fl   Created
 * 1996-03-24 fl   Ready for first public release (release 0.0)
 * 1996-03-25 fl   Added fromstring (for Jack's "img" library)
 * 1996-03-28 fl   Added channel operations
 * 1996-03-31 fl   Added point operation
 * 1996-04-08 fl   Added new/new_block/new_array factories
 * 1996-04-13 fl   Added decoders
 * 1996-05-04 fl   Added palette hack
 * 1996-05-12 fl   Compile cleanly as C++
 * 1996-05-19 fl   Added matrix conversions, gradient fills
 * 1996-05-27 fl   Added display_mode
 * 1996-07-22 fl   Added getbbox, offset
 * 1996-07-23 fl   Added sequence semantics
 * 1996-08-13 fl   Added logical operators, point mode
 * 1996-08-16 fl   Modified paste interface
 * 1996-09-06 fl   Added putdata methods, use abstract interface
 * 1996-11-01 fl   Added xbm encoder
 * 1996-11-04 fl   Added experimental path stuff, draw_lines, etc
 * 1996-12-10 fl   Added zip decoder, crc32 interface
 * 1996-12-14 fl   Added modulo arithmetics
 * 1996-12-29 fl   Added zip encoder
 * 1997-01-03 fl   Added fli and msp decoders
 * 1997-01-04 fl   Added experimental sun_rle and tga_rle decoders
 * 1997-01-05 fl   Added gif encoder, getpalette hack
 * 1997-02-23 fl   Added histogram mask
 * 1997-05-12 fl   Minor tweaks to match the IFUNC95 interface
 * 1997-05-21 fl   Added noise generator, spread effect
 * 1997-06-05 fl   Added mandelbrot generator
 * 1997-08-02 fl   Modified putpalette to coerce image mode if necessary
 * 1998-01-11 fl   Added INT32 support
 * 1998-01-22 fl   Fixed draw_points to draw the last point too
 * 1998-06-28 fl   Added getpixel, getink, draw_ink
 * 1998-07-12 fl   Added getextrema
 * 1998-07-17 fl   Added point conversion to arbitrary formats
 * 1998-09-21 fl   Added support for resampling filters
 * 1998-09-22 fl   Added support for quad transform
 * 1998-12-29 fl   Added support for arcs, chords, and pieslices
 * 1999-01-10 fl   Added some experimental arrow graphics stuff
 * 1999-02-06 fl   Added draw_bitmap, font acceleration stuff
 * 2001-04-17 fl   Fixed some egcs compiler nits
 * 2001-09-17 fl   Added screen grab primitives (win32)
 * 2002-03-09 fl   Added stretch primitive
 * 2002-03-10 fl   Fixed filter handling in rotate
 * 2002-06-06 fl   Added I, F, and RGB support to putdata
 * 2002-06-08 fl   Added rankfilter
 * 2002-06-09 fl   Added support for user-defined filter kernels
 * 2002-11-19 fl   Added clipboard grab primitives (win32)
 * 2002-12-11 fl   Added draw context
 * 2003-04-26 fl   Tweaks for Python 2.3 beta 1
 * 2003-05-21 fl   Added createwindow primitive (win32)
 * 2003-09-13 fl   Added thread section hooks
 * 2003-09-15 fl   Added expand helper
 * 2003-09-26 fl   Added experimental LA support
 * 2004-02-21 fl   Handle zero-size images in quantize
 * 2004-06-05 fl   Added ptr attribute (used to access Imaging objects)
 * 2004-06-05 fl   Don't crash when fetching pixels from zero-wide images
 * 2004-09-17 fl   Added getcolors
 * 2004-10-04 fl   Added modefilter
 * 2005-10-02 fl   Added access proxy
 * 2006-06-18 fl   Always draw last point in polyline
 *
 * Copyright (c) 1997-2006 by Secret Labs AB 
 * Copyright (c) 1995-2006 by Fredrik Lundh
 *
 * See the README file for information on usage and redistribution.
 */


#include "Python.h"

#include "Imaging.h"


/* Configuration stuff. Feel free to undef things you don't need. */
#define WITH_IMAGECHOPS /* ImageChops support */
#define WITH_IMAGEDRAW /* ImageDraw support */
#define WITH_MAPPING /* use memory mapping to read some file formats */
#define WITH_IMAGEPATH /* ImagePath stuff */
#define WITH_ARROW /* arrow graphics stuff (experimental) */
#define WITH_EFFECTS /* special effects */
#define WITH_QUANTIZE /* quantization support */
#define WITH_RANKFILTER /* rank filter */
#define WITH_MODEFILTER /* mode filter */
#define WITH_THREADING /* "friendly" threading support */
#define WITH_UNSHARPMASK /* Kevin Cazabon's unsharpmask module */

#define WITH_DEBUG /* extra debugging interfaces */

/* PIL Plus extensions */
#undef  WITH_CRACKCODE /* pil plus */

#undef	VERBOSE

#define CLIP(x) ((x) <= 0 ? 0 : (x) < 256 ? (x) : 255)

#define B16(p, i) ((((int)p[(i)]) << 8) + p[(i)+1])
#define L16(p, i) ((((int)p[(i)+1]) << 8) + p[(i)])
#define S16(v) ((v) < 32768 ? (v) : ((v) - 65536))

#if PY_VERSION_HEX < 0x01060000
#define PyObject_New PyObject_NEW
#define PyObject_Del PyMem_DEL
#endif

#if PY_VERSION_HEX < 0x02050000
#define Py_ssize_t int
#define ssizeargfunc intargfunc
#define ssizessizeargfunc intintargfunc
#define ssizeobjargproc intobjargproc
#define ssizessizeobjargproc intintobjargproc
#endif

/* -------------------------------------------------------------------- */
/* OBJECT ADMINISTRATION						*/
/* -------------------------------------------------------------------- */

typedef struct {
    PyObject_HEAD
    Imaging image;
    ImagingAccess access;
} ImagingObject;

staticforward PyTypeObject Imaging_Type;

#ifdef WITH_IMAGEDRAW

typedef struct
{
    /* to write a character, cut out sxy from glyph data, place
       at current position plus dxy, and advance by (dx, dy) */
    int dx, dy;
    int dx0, dy0, dx1, dy1;
    int sx0, sy0, sx1, sy1;
} Glyph;

typedef struct {
    PyObject_HEAD
    ImagingObject* ref;
    Imaging bitmap;
    int ysize;
    int baseline;
    Glyph glyphs[256];
} ImagingFontObject;

staticforward PyTypeObject ImagingFont_Type;

typedef struct {
    PyObject_HEAD
    ImagingObject* image;
    UINT8 ink[4];
    int blend;
} ImagingDrawObject;

staticforward PyTypeObject ImagingDraw_Type;

#endif

typedef struct {
    PyObject_HEAD
    ImagingObject* image;
    int readonly;
} PixelAccessObject;

staticforward PyTypeObject PixelAccess_Type;

PyObject* 
PyImagingNew(Imaging imOut)
{
    ImagingObject* imagep;

    if (!imOut)
	return NULL;

    imagep = PyObject_New(ImagingObject, &Imaging_Type);
    if (imagep == NULL) {
	ImagingDelete(imOut);
	return NULL;
    }

#ifdef VERBOSE
    printf("imaging %p allocated\n", imagep);
#endif

    imagep->image = imOut;
    imagep->access = ImagingAccessNew(imOut);

    return (PyObject*) imagep;
}

static void
_dealloc(ImagingObject* imagep)
{

#ifdef VERBOSE
    printf("imaging %p deleted\n", imagep);
#endif

    if (imagep->access)
      ImagingAccessDelete(imagep->image, imagep->access);
    ImagingDelete(imagep->image);
    PyObject_Del(imagep);
}

#define PyImaging_Check(op) ((op)->ob_type == &Imaging_Type)

Imaging PyImaging_AsImaging(PyObject *op)
{
    if (!PyImaging_Check(op)) {
	PyErr_BadInternalCall();
	return NULL;
    }

    return ((ImagingObject *)op)->image;
}


/* -------------------------------------------------------------------- */
/* THREAD HANDLING                                                      */
/* -------------------------------------------------------------------- */

void ImagingSectionEnter(ImagingSectionCookie* cookie)
{
#ifdef WITH_THREADING
    *cookie = (PyThreadState *) PyEval_SaveThread();
#endif
}

void ImagingSectionLeave(ImagingSectionCookie* cookie)
{
#ifdef WITH_THREADING
    PyEval_RestoreThread((PyThreadState*) *cookie);
#endif
}

/* -------------------------------------------------------------------- */
/* BUFFER HANDLING                                                      */
/* -------------------------------------------------------------------- */
/* Python compatibility API */

#if PY_VERSION_HEX < 0x02020000

int PyImaging_CheckBuffer(PyObject *buffer)
{
    PyBufferProcs *procs = buffer->ob_type->tp_as_buffer;
    if (procs && procs->bf_getreadbuffer && procs->bf_getsegcount &&
        procs->bf_getsegcount(buffer, NULL) == 1)
        return 1;
    return 0;
}

int PyImaging_ReadBuffer(PyObject* buffer, const void** ptr)
{
    PyBufferProcs *procs = buffer->ob_type->tp_as_buffer;
    return procs->bf_getreadbuffer(buffer, 0, ptr);
}

#else

int PyImaging_CheckBuffer(PyObject* buffer)
{
    return PyObject_CheckReadBuffer(buffer);
}

int PyImaging_ReadBuffer(PyObject* buffer, const void** ptr)
{
    /* must call check_buffer first! */
#if PY_VERSION_HEX < 0x02050000
    int n = 0;
#else
    Py_ssize_t n = 0;
#endif
    PyObject_AsReadBuffer(buffer, ptr, &n);
    return (int) n;
}

#endif

/* -------------------------------------------------------------------- */
/* EXCEPTION REROUTING                                                  */
/* -------------------------------------------------------------------- */

/* error messages */
static const char* must_be_sequence = "argument must be a sequence";
static const char* wrong_mode = "unrecognized image mode";
static const char* wrong_raw_mode = "unrecognized raw mode";
static const char* outside_image = "image index out of range";
static const char* outside_palette = "palette index out of range";
static const char* no_palette = "image has no palette";
static const char* readonly = "image is readonly";
/* static const char* no_content = "image has no content"; */

void *
ImagingError_IOError(void)
{
    PyErr_SetString(PyExc_IOError, "error when accessing file");
    return NULL;
}

void *
ImagingError_MemoryError(void)
{
    return PyErr_NoMemory();
}

void *
ImagingError_Mismatch(void)
{
    PyErr_SetString(PyExc_ValueError, "images do not match");
    return NULL;
}

void *
ImagingError_ModeError(void)
{
    PyErr_SetString(PyExc_ValueError, "image has wrong mode");
    return NULL;
}

void *
ImagingError_ValueError(const char *message)
{
    PyErr_SetString(
        PyExc_ValueError,
        (message) ? (char*) message : "unrecognized argument value"
        );
    return NULL;
}

void
ImagingError_Clear(void)
{
    PyErr_Clear();
}

/* -------------------------------------------------------------------- */
/* HELPERS								*/
/* -------------------------------------------------------------------- */

static int
getbands(const char* mode)
{
    Imaging im;
    int bands;

    /* FIXME: add primitive to libImaging to avoid extra allocation */
    im = ImagingNew(mode, 0, 0);
    if (!im)
        return -1;

    bands = im->bands;

    ImagingDelete(im);

    return bands;
}

#define TYPE_UINT8 (0x100|sizeof(UINT8))
#define TYPE_INT32 (0x200|sizeof(INT32))
#define TYPE_FLOAT32 (0x300|sizeof(FLOAT32))
#define TYPE_DOUBLE (0x400|sizeof(double))

static void*
getlist(PyObject* arg, int* length, const char* wrong_length, int type)
{
    int i, n;
    void* list;

    if (!PySequence_Check(arg)) {
	PyErr_SetString(PyExc_TypeError, must_be_sequence);
	return NULL;
    }

    n = PyObject_Length(arg);
    if (length && wrong_length && n != *length) {
	PyErr_SetString(PyExc_ValueError, wrong_length);
	return NULL;
    }

    list = malloc(n * (type & 0xff));
    if (!list)
        return PyErr_NoMemory();

    switch (type) {
    case TYPE_UINT8:
        if (PyList_Check(arg)) {
            for (i = 0; i < n; i++) {
                PyObject *op = PyList_GET_ITEM(arg, i);
                int temp = PyInt_AsLong(op);
                ((UINT8*)list)[i] = CLIP(temp);
            }
        } else {
            for (i = 0; i < n; i++) {
                PyObject *op = PySequence_GetItem(arg, i);
                int temp = PyInt_AsLong(op);
                Py_XDECREF(op);
                ((UINT8*)list)[i] = CLIP(temp);
            }
        }
        break;
    case TYPE_INT32:
        if (PyList_Check(arg)) {
            for (i = 0; i < n; i++) {
                PyObject *op = PyList_GET_ITEM(arg, i);
                int temp = PyInt_AsLong(op);
                ((INT32*)list)[i] = temp;
            }
        } else {
            for (i = 0; i < n; i++) {
                PyObject *op = PySequence_GetItem(arg, i);
                int temp = PyInt_AsLong(op);
                Py_XDECREF(op);
                ((INT32*)list)[i] = temp;
            }
        }
        break;
    case TYPE_FLOAT32:
        if (PyList_Check(arg)) {
            for (i = 0; i < n; i++) {
                PyObject *op = PyList_GET_ITEM(arg, i);
                double temp = PyFloat_AsDouble(op);
                ((FLOAT32*)list)[i] = (FLOAT32) temp;
            }
        } else {
            for (i = 0; i < n; i++) {
                PyObject *op = PySequence_GetItem(arg, i);
                double temp = PyFloat_AsDouble(op);
                Py_XDECREF(op);
                ((FLOAT32*)list)[i] = (FLOAT32) temp;
            }
        }
        break;
    case TYPE_DOUBLE:
        if (PyList_Check(arg)) {
            for (i = 0; i < n; i++) {
                PyObject *op = PyList_GET_ITEM(arg, i);
                double temp = PyFloat_AsDouble(op);
                ((double*)list)[i] = temp;
            }
        } else {
            for (i = 0; i < n; i++) {
                PyObject *op = PySequence_GetItem(arg, i);
                double temp = PyFloat_AsDouble(op);
                Py_XDECREF(op);
                ((double*)list)[i] = temp;
            }
        }
        break;
    }

    if (length)
        *length = n;

    PyErr_Clear();

    return list;
}

static inline PyObject*
getpixel(Imaging im, ImagingAccess access, int x, int y)
{
    union {
      UINT8 b[4];
      INT16 h;
      INT32 i;
      FLOAT32 f;
    } pixel;

    if (x < 0 || x >= im->xsize || y < 0 || y >= im->ysize) {
	PyErr_SetString(PyExc_IndexError, outside_image);
	return NULL;
    }

    access->get_pixel(im, x, y, &pixel);

    switch (im->type) {
    case IMAGING_TYPE_UINT8:
      switch (im->bands) {
      case 1:
        return PyInt_FromLong(pixel.b[0]);
      case 2:
        return Py_BuildValue("ii", pixel.b[0], pixel.b[1]);
      case 3:
        return Py_BuildValue("iii", pixel.b[0], pixel.b[1], pixel.b[2]);
      case 4:
        return Py_BuildValue("iiii", pixel.b[0], pixel.b[1], pixel.b[2], pixel.b[3]);
      }
      break;
    case IMAGING_TYPE_INT32:
      return PyInt_FromLong(pixel.i);
    case IMAGING_TYPE_FLOAT32:
      return PyFloat_FromDouble(pixel.f);
    case IMAGING_TYPE_SPECIAL:
      if (strncmp(im->mode, "I;16", 4) == 0)
        return PyInt_FromLong(pixel.h);
      break;
    }

    /* unknown type */
    Py_INCREF(Py_None);
    return Py_None;
}

static char*
getink(PyObject* color, Imaging im, char* ink)
{
    int r, g, b, a;
    double f;

    /* fill ink buffer (four bytes) with something that can
       be cast to either UINT8 or INT32 */

    switch (im->type) {
    case IMAGING_TYPE_UINT8:
        /* unsigned integer */
        if (im->bands == 1) {
            /* unsigned integer, single layer */
            r = PyInt_AsLong(color);
            if (r == -1 && PyErr_Occurred())
                return NULL;
            ink[0] = CLIP(r);
            ink[1] = ink[2] = ink[3] = 0;
        } else {
            a = 255;
            if (PyInt_Check(color)) {
                r = PyInt_AS_LONG(color);
                /* compatibility: ABGR */
                a = (UINT8) (r >> 24);
                b = (UINT8) (r >> 16);
                g = (UINT8) (r >> 8);
                r = (UINT8) r;
            } else {
                if (im->bands == 2) {
                    if (!PyArg_ParseTuple(color, "i|i", &r, &a))
                        return NULL;
                    g = b = r;
                } else {
                    if (!PyArg_ParseTuple(color, "iii|i", &r, &g, &b, &a))
                        return NULL;
                }
            }
            ink[0] = CLIP(r);
            ink[1] = CLIP(g);
            ink[2] = CLIP(b);
            ink[3] = CLIP(a);
        }
        return ink;
    case IMAGING_TYPE_INT32:
        /* signed integer */
        r = PyInt_AsLong(color);
        if (r == -1 && PyErr_Occurred())
            return NULL;
        *(INT32*) ink = r;
        return ink;
    case IMAGING_TYPE_FLOAT32:
        /* floating point */
        f = PyFloat_AsDouble(color);
        if (f == -1.0 && PyErr_Occurred())
            return NULL;
        *(FLOAT32*) ink = (FLOAT32) f;
        return ink;
    case IMAGING_TYPE_SPECIAL:
        if (strncmp(im->mode, "I;16", 4) == 0) {
            r = PyInt_AsLong(color);
            if (r == -1 && PyErr_Occurred())
                return NULL;
            ink[0] = (UINT8) r;
            ink[1] = (UINT8) (r >> 8);
            ink[2] = ink[3] = 0;
            return ink;
        }
    }

    PyErr_SetString(PyExc_ValueError, wrong_mode);
    return NULL;
}

/* -------------------------------------------------------------------- */
/* FACTORIES								*/
/* -------------------------------------------------------------------- */

static PyObject* 
_fill(PyObject* self, PyObject* args)
{
    char* mode;
    int xsize, ysize;
    PyObject* color;
    char buffer[4];
    Imaging im;
    
    xsize = ysize = 256;
    color = NULL;

    if (!PyArg_ParseTuple(args, "s|(ii)O", &mode, &xsize, &ysize, &color))
	return NULL;

    im = ImagingNew(mode, xsize, ysize);
    if (!im)
        return NULL;

    if (color) {
        if (!getink(color, im, buffer)) {
            ImagingDelete(im);
            return NULL;
        }
    } else
        buffer[0] = buffer[1] = buffer[2] = buffer[3] = 0;

    (void) ImagingFill(im, buffer);

    return PyImagingNew(im);
}

static PyObject* 
_new(PyObject* self, PyObject* args)
{
    char* mode;
    int xsize, ysize;

    if (!PyArg_ParseTuple(args, "s(ii)", &mode, &xsize, &ysize))
	return NULL;

    return PyImagingNew(ImagingNew(mode, xsize, ysize));
}

static PyObject* 
_new_array(PyObject* self, PyObject* args)
{
    char* mode;
    int xsize, ysize;

    if (!PyArg_ParseTuple(args, "s(ii)", &mode, &xsize, &ysize))
	return NULL;

    return PyImagingNew(ImagingNewArray(mode, xsize, ysize));
}

static PyObject* 
_new_block(PyObject* self, PyObject* args)
{
    char* mode;
    int xsize, ysize;

    if (!PyArg_ParseTuple(args, "s(ii)", &mode, &xsize, &ysize))
	return NULL;

    return PyImagingNew(ImagingNewBlock(mode, xsize, ysize));
}

static PyObject* 
_getcount(PyObject* self, PyObject* args)
{
    if (!PyArg_ParseTuple(args, ":getcount"))
	return NULL;

    return PyInt_FromLong(ImagingNewCount);
}

static PyObject* 
_linear_gradient(PyObject* self, PyObject* args)
{
    char* mode;

    if (!PyArg_ParseTuple(args, "s", &mode))
	return NULL;

    return PyImagingNew(ImagingFillLinearGradient(mode));
}

static PyObject* 
_radial_gradient(PyObject* self, PyObject* args)
{
    char* mode;

    if (!PyArg_ParseTuple(args, "s", &mode))
	return NULL;

    return PyImagingNew(ImagingFillRadialGradient(mode));
}

static PyObject* 
_open_ppm(PyObject* self, PyObject* args)
{
    char* filename;

    if (!PyArg_ParseTuple(args, "s", &filename))
	return NULL;

    return PyImagingNew(ImagingOpenPPM(filename));
}

static PyObject* 
_blend(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep1;
    ImagingObject* imagep2;
    double alpha;
    
    alpha = 0.5;
    if (!PyArg_ParseTuple(args, "O!O!|d",
			  &Imaging_Type, &imagep1,
			  &Imaging_Type, &imagep2,
			  &alpha))
	return NULL;

    return PyImagingNew(ImagingBlend(imagep1->image, imagep2->image,
				     (float) alpha));
}

/* -------------------------------------------------------------------- */
/* METHODS								*/
/* -------------------------------------------------------------------- */

static PyObject* 
_convert(ImagingObject* self, PyObject* args)
{
    char* mode;
    int dither = 0;
    ImagingObject *paletteimage = NULL;

    if (!PyArg_ParseTuple(args, "s|iO", &mode, &dither, &paletteimage))
	return NULL;
    if (paletteimage != NULL) {
      if (!PyImaging_Check(paletteimage)) {
	PyObject_Print((PyObject *)paletteimage, stderr, 0);
	PyErr_SetString(PyExc_ValueError, "palette argument must be image with mode 'P'");
	return NULL;
      }
      if (paletteimage->image->palette == NULL) {
	PyErr_SetString(PyExc_ValueError, "null palette");
	return NULL;
      }
    }

    return PyImagingNew(ImagingConvert(self->image, mode, paletteimage ? paletteimage->image->palette : NULL, dither));
}

static PyObject* 
_convert2(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep1;
    ImagingObject* imagep2;
    if (!PyArg_ParseTuple(args, "O!O!",
			  &Imaging_Type, &imagep1,
			  &Imaging_Type, &imagep2))
	return NULL;

    if (!ImagingConvert2(imagep1->image, imagep2->image))
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* 
_convert_matrix(ImagingObject* self, PyObject* args)
{
    char* mode;
    float m[12];
    if (!PyArg_ParseTuple(args, "s(ffff)", &mode, m+0, m+1, m+2, m+3)) {
	PyErr_Clear();
	if (!PyArg_ParseTuple(args, "s(ffffffffffff)", &mode,
			      m+0, m+1, m+2, m+3,
			      m+4, m+5, m+6, m+7,
			      m+8, m+9, m+10, m+11))
	    return NULL;
    }

    return PyImagingNew(ImagingConvertMatrix(self->image, mode, m));
}

static PyObject* 
_copy(ImagingObject* self, PyObject* args)
{
    if (!PyArg_ParseTuple(args, ""))
	return NULL;

    return PyImagingNew(ImagingCopy(self->image));
}

static PyObject* 
_copy2(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep1;
    ImagingObject* imagep2;
    if (!PyArg_ParseTuple(args, "O!O!",
			  &Imaging_Type, &imagep1,
			  &Imaging_Type, &imagep2))
	return NULL;

    if (!ImagingCopy2(imagep1->image, imagep2->image))
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* 
_crop(ImagingObject* self, PyObject* args)
{
    int x0, y0, x1, y1;
    if (!PyArg_ParseTuple(args, "(iiii)", &x0, &y0, &x1, &y1))
	return NULL;

    return PyImagingNew(ImagingCrop(self->image, x0, y0, x1, y1));
}

static PyObject* 
_expand(ImagingObject* self, PyObject* args)
{
    int x, y;
    int mode = 0;
    if (!PyArg_ParseTuple(args, "ii|i", &x, &y, &mode))
	return NULL;

    return PyImagingNew(ImagingExpand(self->image, x, y, mode));
}

static PyObject* 
_filter(ImagingObject* self, PyObject* args)
{
    PyObject* imOut;
    int kernelsize;
    FLOAT32* kerneldata;

    int xsize, ysize;
    float divisor, offset;
    PyObject* kernel = NULL;
    if (!PyArg_ParseTuple(args, "(ii)ffO", &xsize, &ysize,
                         &divisor, &offset, &kernel))
        return NULL;
    
    /* get user-defined kernel */
    kerneldata = getlist(kernel, &kernelsize, NULL, TYPE_FLOAT32);
    if (!kerneldata)
        return NULL;
    if (kernelsize != xsize * ysize) {
        free(kerneldata);
        return ImagingError_ValueError("bad kernel size");
    }

    imOut = PyImagingNew(
        ImagingFilter(self->image, xsize, ysize, kerneldata, offset, divisor)
        );

    free(kerneldata);

    return imOut;
}

#ifdef WITH_UNSHARPMASK
static PyObject* 
_gaussian_blur(ImagingObject* self, PyObject* args)
{
    Imaging imIn;
    Imaging imOut;

    float radius = 0;
    if (!PyArg_ParseTuple(args, "f", &radius))
        return NULL;

    imIn = self->image;
    imOut = ImagingNew(imIn->mode, imIn->xsize, imIn->ysize);
    if (!imOut)
        return NULL;

    if (!ImagingGaussianBlur(imIn, imOut, radius))
        return NULL;

    return PyImagingNew(imOut);
}
#endif

static PyObject* 
_getpalette(ImagingObject* self, PyObject* args)
{
    PyObject* palette;
    int palettesize = 256;
    int bits;
    ImagingShuffler pack;

    char* mode = "RGB";
    char* rawmode = "RGB";
    if (!PyArg_ParseTuple(args, "|ss", &mode, &rawmode))
	return NULL;

    if (!self->image->palette) {
	PyErr_SetString(PyExc_ValueError, no_palette);
	return NULL;
    }

    pack = ImagingFindPacker(mode, rawmode, &bits);
    if (!pack) {
	PyErr_SetString(PyExc_ValueError, wrong_raw_mode);
	return NULL;
    }

    palette = PyString_FromStringAndSize(NULL, palettesize * bits / 8);
    if (!palette)
	return NULL;

    pack((UINT8*) PyString_AsString(palette),
	 self->image->palette->palette, palettesize);

    return palette;
}

static inline int
_getxy(PyObject* xy, int* x, int *y)
{
    PyObject* value;

    if (!PyTuple_Check(xy) || PyTuple_GET_SIZE(xy) != 2)
        goto badarg;
        
    value = PyTuple_GET_ITEM(xy, 0);
    if (PyInt_Check(value))
        *x = PyInt_AS_LONG(value);
    else if (PyFloat_Check(value))
        *x = (int) PyFloat_AS_DOUBLE(value);
    else
        goto badval;

    value = PyTuple_GET_ITEM(xy, 1);
    if (PyInt_Check(value))
        *y = PyInt_AS_LONG(value);
    else if (PyFloat_Check(value))
        *y = (int) PyFloat_AS_DOUBLE(value);
    else
        goto badval;

    return 0;

  badarg:
    PyErr_SetString(
        PyExc_TypeError,
        "argument must be sequence of length 2"
        );
    return -1;

  badval:
    PyErr_SetString(
        PyExc_TypeError,
        "an integer is required"
        );
    return -1;
}

static PyObject* 
_getpixel(ImagingObject* self, PyObject* args)
{
    PyObject* xy;
    int x, y;

    if (PyTuple_GET_SIZE(args) != 1) {
        PyErr_SetString(
            PyExc_TypeError,
            "argument 1 must be sequence of length 2"
            );
        return NULL;
    }

    xy = PyTuple_GET_ITEM(args, 0);

    if (_getxy(xy, &x, &y))
        return NULL;

    if (self->access == NULL) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    return getpixel(self->image, self->access, x, y);
}

static PyObject*
_histogram(ImagingObject* self, PyObject* args)
{
    ImagingHistogram h;
    PyObject* list;
    int i;
    union {
        UINT8 u[2];
        INT32 i[2];
        FLOAT32 f[2];
    } extrema;
    void* ep;
    int i0, i1;
    double f0, f1;

    PyObject* extremap = NULL;
    ImagingObject* maskp = NULL;
    if (!PyArg_ParseTuple(args, "|OO!", &extremap, &Imaging_Type, &maskp))
	return NULL;

    if (extremap) {
        ep = &extrema;
        switch (self->image->type) {
        case IMAGING_TYPE_UINT8:
            if (!PyArg_ParseTuple(extremap, "ii", &i0, &i1))
                return NULL;
            /* FIXME: clip */
            extrema.u[0] = i0;
            extrema.u[1] = i1;
            break;
        case IMAGING_TYPE_INT32:
            if (!PyArg_ParseTuple(extremap, "ii", &i0, &i1))
                return NULL;
            extrema.i[0] = i0;
            extrema.i[1] = i1;
            break;
        case IMAGING_TYPE_FLOAT32:
            if (!PyArg_ParseTuple(extremap, "dd", &f0, &f1))
                return NULL;
            extrema.f[0] = (FLOAT32) f0;
            extrema.f[1] = (FLOAT32) f1;
            break;
        default:
            ep = NULL;
            break;
        }
    } else
        ep = NULL;

    h = ImagingGetHistogram(self->image, (maskp) ? maskp->image : NULL, ep);

    if (!h)
	return NULL;

    /* Build an integer list containing the histogram */
    list = PyList_New(h->bands * 256);
    for (i = 0; i < h->bands * 256; i++) {
	PyObject* item;
	item = PyInt_FromLong(h->histogram[i]);
	if (item == NULL) {
	    Py_DECREF(list);
	    list = NULL;
	    break;
	}
	PyList_SetItem(list, i, item);
    }

    ImagingHistogramDelete(h);

    return list;
}

#ifdef WITH_MODEFILTER
static PyObject* 
_modefilter(ImagingObject* self, PyObject* args)
{
    int size;
    if (!PyArg_ParseTuple(args, "i", &size))
	return NULL;

    return PyImagingNew(ImagingModeFilter(self->image, size));
}
#endif

static PyObject* 
_offset(ImagingObject* self, PyObject* args)
{
    int xoffset, yoffset;
    if (!PyArg_ParseTuple(args, "ii", &xoffset, &yoffset))
	return NULL;

    return PyImagingNew(ImagingOffset(self->image, xoffset, yoffset));
}

static PyObject* 
_paste(ImagingObject* self, PyObject* args)
{
    int status;
    char ink[4];

    PyObject* source;
    int x0, y0, x1, y1;
    ImagingObject* maskp = NULL;
    if (!PyArg_ParseTuple(args, "O(iiii)|O!",
			  &source,
			  &x0, &y0, &x1, &y1,
			  &Imaging_Type, &maskp))
	return NULL;

    if (PyImaging_Check(source))
        status = ImagingPaste(
            self->image, PyImaging_AsImaging(source),
            (maskp) ? maskp->image : NULL,
            x0, y0, x1, y1
            );

    else {
        if (!getink(source, self->image, ink))
            return NULL;
        status = ImagingFill2(
            self->image, ink,
            (maskp) ? maskp->image : NULL,
            x0, y0, x1, y1
            );
    }

    if (status < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_point(ImagingObject* self, PyObject* args)
{
    static const char* wrong_number = "wrong number of lut entries";

    int n, i;
    int bands;
    Imaging im;

    PyObject* list;
    char* mode;
    if (!PyArg_ParseTuple(args, "Oz", &list, &mode))
	return NULL;

    if (mode && !strcmp(mode, "F")) {
        FLOAT32* data;

        /* map from 8-bit data to floating point */
        n = 256;
        data = getlist(list, &n, wrong_number, TYPE_FLOAT32);
        if (!data)
            return NULL;
        im = ImagingPoint(self->image, mode, (void*) data);
        free(data);

    } else if (!strcmp(self->image->mode, "I") && mode && !strcmp(mode, "L")) {
        UINT8* data;

        /* map from 16-bit subset of 32-bit data to 8-bit */
        /* FIXME: support arbitrary number of entries (requires API change) */
        n = 65536;
        data = getlist(list, &n, wrong_number, TYPE_UINT8);
        if (!data)
            return NULL;
        im = ImagingPoint(self->image, mode, (void*) data);
        free(data);

    } else {
        INT32* data;
        UINT8 lut[1024];

        if (mode) {
            bands = getbands(mode);
            if (bands < 0)
                return NULL;
        } else
            bands = self->image->bands;

        /* map to integer data */
        n = 256 * bands;
        data = getlist(list, &n, wrong_number, TYPE_INT32);
        if (!data)
            return NULL;

        if (mode && !strcmp(mode, "I"))
            im = ImagingPoint(self->image, mode, (void*) data);
        else if (mode && bands > 1) {
            for (i = 0; i < 256; i++) {
                lut[i*4] = CLIP(data[i]);
                lut[i*4+1] = CLIP(data[i+256]);
                lut[i*4+2] = CLIP(data[i+512]);
                if (n > 768)
                    lut[i*4+3] = CLIP(data[i+768]);
            }
            im = ImagingPoint(self->image, mode, (void*) lut);
        } else {
            /* map individual bands */
            for (i = 0; i < n; i++)
                lut[i] = CLIP(data[i]);
            im = ImagingPoint(self->image, mode, (void*) lut);
        }
        free(data);
    }

    return PyImagingNew(im);
}

static PyObject*
_point_transform(ImagingObject* self, PyObject* args)
{
    double scale = 1.0;
    double offset = 0.0;
    if (!PyArg_ParseTuple(args, "|dd", &scale, &offset))
	return NULL;

    return PyImagingNew(ImagingPointTransform(self->image, scale, offset));
}

static PyObject*
_putdata(ImagingObject* self, PyObject* args)
{
    Imaging image;
    int n, i, x, y;

    PyObject* data;
    double scale = 1.0;
    double offset = 0.0;
    if (!PyArg_ParseTuple(args, "O|dd", &data, &scale, &offset))
	return NULL;

    if (!PySequence_Check(data)) {
	PyErr_SetString(PyExc_TypeError, must_be_sequence);
	return NULL;
    }

    image = self->image;

    n = PyObject_Length(data);
    if (n > (int) (image->xsize * image->ysize)) {
	PyErr_SetString(PyExc_TypeError, "too many data entries");
	return NULL;
    }

    if (image->image8) {
        if (PyString_Check(data)) {
            unsigned char* p;
            p = (unsigned char*) PyString_AS_STRING((PyStringObject*) data);
            if (scale == 1.0 && offset == 0.0)
                /* Plain string data */
                for (i = y = 0; i < n; i += image->xsize, y++) {
                    x = n - i;
                    if (x > (int) image->xsize)
                        x = image->xsize;
                    memcpy(image->image8[y], p+i, x);
                }
            else 
                /* Scaled and clipped string data */
                for (i = x = y = 0; i < n; i++) {
                    image->image8[y][x] = CLIP((int) (p[i] * scale + offset));
                    if (++x >= (int) image->xsize)
                        x = 0, y++;
                }
        } else {
            if (scale == 1.0 && offset == 0.0) {
                /* Clipped data */
                if (PyList_Check(data)) {
                    for (i = x = y = 0; i < n; i++) {
                        PyObject *op = PyList_GET_ITEM(data, i);
                        image->image8[y][x] = (UINT8) CLIP(PyInt_AsLong(op));
                        if (++x >= (int) image->xsize)
                            x = 0, y++;
                    }
                } else {
                    for (i = x = y = 0; i < n; i++) {
                        PyObject *op = PySequence_GetItem(data, i);
                        image->image8[y][x] = (UINT8) CLIP(PyInt_AsLong(op));
                        Py_XDECREF(op);
                        if (++x >= (int) image->xsize)
                            x = 0, y++;
                    }
                }
            } else {
                if (PyList_Check(data)) {
                    /* Scaled and clipped data */
                    for (i = x = y = 0; i < n; i++) {
                        PyObject *op = PyList_GET_ITEM(data, i);
                        image->image8[y][x] = CLIP(
                            (int) (PyFloat_AsDouble(op) * scale + offset));
                        if (++x >= (int) image->xsize)
                            x = 0, y++;
                    }
                } else {
                    for (i = x = y = 0; i < n; i++) {
                        PyObject *op = PySequence_GetItem(data, i);
                        image->image8[y][x] = CLIP(
                            (int) (PyFloat_AsDouble(op) * scale + offset));
                        Py_XDECREF(op);
                        if (++x >= (int) image->xsize)
                            x = 0, y++;
                    }
                }
            }
            PyErr_Clear(); /* Avoid weird exceptions */
        }
    } else {
        /* 32-bit images */
        switch (image->type) {
        case IMAGING_TYPE_INT32:
            for (i = x = y = 0; i < n; i++) {
                PyObject *op = PySequence_GetItem(data, i);
                IMAGING_PIXEL_INT32(image, x, y) =
                    (INT32) (PyFloat_AsDouble(op) * scale + offset);
                Py_XDECREF(op);
                if (++x >= (int) image->xsize)
                    x = 0, y++;
            }
            PyErr_Clear(); /* Avoid weird exceptions */
            break;
        case IMAGING_TYPE_FLOAT32:
            for (i = x = y = 0; i < n; i++) {
                PyObject *op = PySequence_GetItem(data, i);
                IMAGING_PIXEL_FLOAT32(image, x, y) =
                    (FLOAT32) (PyFloat_AsDouble(op) * scale + offset);
                Py_XDECREF(op);
                if (++x >= (int) image->xsize)
                    x = 0, y++;
            }
            PyErr_Clear(); /* Avoid weird exceptions */
            break;
        default:
            for (i = x = y = 0; i < n; i++) {
                char ink[4];
                PyObject *op = PySequence_GetItem(data, i);
                if (!op || !getink(op, image, ink)) {
                    Py_DECREF(op);
                    return NULL;
                }
                /* FIXME: what about scale and offset? */
                image->image32[y][x] = *((INT32*) ink);
                Py_XDECREF(op);
                if (++x >= (int) image->xsize)
                    x = 0, y++;
            }
            PyErr_Clear(); /* Avoid weird exceptions */
            break;
        }
    }

    Py_INCREF(Py_None);
    return Py_None;
}

#ifdef WITH_QUANTIZE

#include "Quant.h"
static PyObject* 
_quantize(ImagingObject* self, PyObject* args)
{
    int colours = 256;
    int method = 0;
    int kmeans = 0;
    if (!PyArg_ParseTuple(args, "|iii", &colours, &method, &kmeans))
	return NULL;

    if (!self->image->xsize || !self->image->ysize) {
        /* no content; return an empty image */
        return PyImagingNew(
            ImagingNew("P", self->image->xsize, self->image->ysize)
            );
    }

    return PyImagingNew(ImagingQuantize(self->image, colours, method, kmeans));
}
#endif

static PyObject* 
_putpalette(ImagingObject* self, PyObject* args)
{
    ImagingShuffler unpack;
    int bits;

    char* rawmode;
    UINT8* palette;
    int palettesize;
    if (!PyArg_ParseTuple(args, "ss#", &rawmode, &palette, &palettesize))
	return NULL;

    if (strcmp(self->image->mode, "L") != 0 && strcmp(self->image->mode, "P")) {
	PyErr_SetString(PyExc_ValueError, wrong_mode);
	return NULL;
    }

    unpack = ImagingFindUnpacker("RGB", rawmode, &bits);
    if (!unpack) {
	PyErr_SetString(PyExc_ValueError, wrong_raw_mode);
	return NULL;
    }

    ImagingPaletteDelete(self->image->palette);

    strcpy(self->image->mode, "P");

    self->image->palette = ImagingPaletteNew("RGB");

    unpack(self->image->palette->palette, palette, palettesize * 8 / bits);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* 
_putpalettealpha(ImagingObject* self, PyObject* args)
{
    int index;
    int alpha = 0;
    if (!PyArg_ParseTuple(args, "i|i", &index, &alpha))
	return NULL;

    if (!self->image->palette) {
	PyErr_SetString(PyExc_ValueError, no_palette);
	return NULL;
    }

    if (index < 0 || index >= 256) {
	PyErr_SetString(PyExc_ValueError, outside_palette);
	return NULL;
    }

    strcpy(self->image->palette->mode, "RGBA");
    self->image->palette->palette[index*4+3] = (UINT8) alpha;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* 
_putpixel(ImagingObject* self, PyObject* args)
{
    Imaging im;
    char ink[4];

    int x, y;
    PyObject* color;
    if (!PyArg_ParseTuple(args, "(ii)O", &x, &y, &color))
	return NULL;

    im = self->image;
    
    if (x < 0 || x >= im->xsize || y < 0 || y >= im->ysize) {
	PyErr_SetString(PyExc_IndexError, outside_image);
	return NULL;
    }

    if (!getink(color, im, ink))
        return NULL;

    if (self->access)
        self->access->put_pixel(im, x, y, ink);

    Py_INCREF(Py_None);
    return Py_None;
}

#ifdef WITH_RANKFILTER
static PyObject* 
_rankfilter(ImagingObject* self, PyObject* args)
{
    int size, rank;
    if (!PyArg_ParseTuple(args, "ii", &size, &rank))
	return NULL;

    return PyImagingNew(ImagingRankFilter(self->image, size, rank));
}
#endif

static PyObject* 
_resize(ImagingObject* self, PyObject* args)
{
    Imaging imIn;
    Imaging imOut;

    int xsize, ysize;
    int filter = IMAGING_TRANSFORM_NEAREST;
    if (!PyArg_ParseTuple(args, "(ii)|i", &xsize, &ysize, &filter))
	return NULL;

    imIn = self->image;

    imOut = ImagingNew(imIn->mode, xsize, ysize);
    if (imOut)
	(void) ImagingResize(imOut, imIn, filter);
    
    return PyImagingNew(imOut);
}

static PyObject* 
_rotate(ImagingObject* self, PyObject* args)
{
    Imaging imOut;
    Imaging imIn;
    
    double theta;
    int filter = IMAGING_TRANSFORM_NEAREST;
    if (!PyArg_ParseTuple(args, "d|i", &theta, &filter))
	return NULL;

    imIn = self->image;

    theta = fmod(theta, 360.0);
    if (theta < 0.0)
	theta += 360;

    if (filter && imIn->type != IMAGING_TYPE_SPECIAL) {
        /* Rotate with resampling filter */
        imOut = ImagingNew(imIn->mode, imIn->xsize, imIn->ysize);
	(void) ImagingRotate(imOut, imIn, theta, filter);
    } else if (theta == 90.0 || theta == 270.0) {
        /* Use fast version */
        imOut = ImagingNew(imIn->mode, imIn->ysize, imIn->xsize);
        if (imOut) {
            if (theta == 90.0)
                (void) ImagingRotate90(imOut, imIn);
            else
                (void) ImagingRotate270(imOut, imIn);
        }
    } else {
        imOut = ImagingNew(imIn->mode, imIn->xsize, imIn->ysize);
        if (imOut) {
            if (theta == 0.0)
                /* No rotation: simply copy the input image */
                (void) ImagingCopy2(imOut, imIn);
            else if (theta == 180.0)
                /* Use fast version */
                (void) ImagingRotate180(imOut, imIn);
            else
                /* Use ordinary version */
                (void) ImagingRotate(imOut, imIn, theta, 0);
        }
    }

    return PyImagingNew(imOut);
}

#define IS_RGB(mode)\
    (!strcmp(mode, "RGB") || !strcmp(mode, "RGBA") || !strcmp(mode, "RGBX"))

static PyObject* 
im_setmode(ImagingObject* self, PyObject* args)
{
    /* attempt to modify the mode of an image in place */

    Imaging im;

    char* mode;
    int modelen;
    if (!PyArg_ParseTuple(args, "s#:setmode", &mode, &modelen))
	return NULL;

    im = self->image;

    /* move all logic in here to the libImaging primitive */

    if (!strcmp(im->mode, mode)) {
        ; /* same mode; always succeeds */
    } else if (IS_RGB(im->mode) && IS_RGB(mode)) {
        /* color to color */
        strcpy(im->mode, mode);
        im->bands = modelen;
        if (!strcmp(mode, "RGBA"))
            (void) ImagingFillBand(im, 3, 255);
    } else {
        /* trying doing an in-place conversion */
        if (!ImagingConvertInPlace(im, mode))
            return NULL;
    }

    if (self->access)
        ImagingAccessDelete(im, self->access);
    self->access = ImagingAccessNew(im);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* 
_stretch(ImagingObject* self, PyObject* args)
{
    Imaging imIn;
    Imaging imTemp;
    Imaging imOut;

    int xsize, ysize;
    int filter = IMAGING_TRANSFORM_NEAREST;
    if (!PyArg_ParseTuple(args, "(ii)|i", &xsize, &ysize, &filter))
	return NULL;

    imIn = self->image;

    /* two-pass resize: minimize size of intermediate image */
    if (imIn->xsize * ysize < xsize * imIn->ysize)
        imTemp = ImagingNew(imIn->mode, imIn->xsize, ysize);
    else 
        imTemp = ImagingNew(imIn->mode, xsize, imIn->ysize);
    if (!imTemp)
        return NULL;

    /* first pass */
    if (!ImagingStretch(imTemp, imIn, filter)) {
        ImagingDelete(imTemp);
        return NULL;
    }

    imOut = ImagingNew(imIn->mode, xsize, ysize);
    if (!imOut) {
        ImagingDelete(imTemp);
        return NULL;
    }

    /* second pass */
    if (!ImagingStretch(imOut, imTemp, filter)) {
        ImagingDelete(imOut);
        ImagingDelete(imTemp);
        return NULL;
    }

    ImagingDelete(imTemp);
    
    return PyImagingNew(imOut);
}

static PyObject* 
_transform2(ImagingObject* self, PyObject* args)
{
    static const char* wrong_number = "wrong number of matrix entries";

    Imaging imIn;
    Imaging imOut;
    int n;
    double *a;

    ImagingObject* imagep;
    int x0, y0, x1, y1;
    int method;
    PyObject* data;
    int filter = IMAGING_TRANSFORM_NEAREST;
    int fill = 1;
    if (!PyArg_ParseTuple(args, "(iiii)O!iO|ii",
                          &x0, &y0, &x1, &y1,
			  &Imaging_Type, &imagep,
                          &method, &data,
                          &filter, &fill))
	return NULL;

    switch (method) {
    case IMAGING_TRANSFORM_AFFINE:
        n = 6;
        break;
    case IMAGING_TRANSFORM_PERSPECTIVE:
        n = 8;
        break;
    case IMAGING_TRANSFORM_QUAD:
        n = 8;
        break;
    default:
        n = -1; /* force error */
    }

    a = getlist(data, &n, wrong_number, TYPE_DOUBLE);
    if (!a)
        return NULL;

    imOut = self->image;
    imIn = imagep->image;

    /* FIXME: move transform dispatcher into libImaging */

    switch (method) {
    case IMAGING_TRANSFORM_AFFINE:
        imOut = ImagingTransformAffine(
            imOut, imIn, x0, y0, x1, y1, a, filter, 1
            );
        break;
    case IMAGING_TRANSFORM_PERSPECTIVE:
        imOut = ImagingTransformPerspective(
            imOut, imIn, x0, y0, x1, y1, a, filter, 1
            );
        break;
    case IMAGING_TRANSFORM_QUAD:
        imOut = ImagingTransformQuad(
            imOut, imIn, x0, y0, x1, y1, a, filter, 1
            );
        break;
    default:
        (void) ImagingError_ValueError("bad transform method");
    }

    free(a);

    if (!imOut)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* 
_transpose(ImagingObject* self, PyObject* args)
{
    Imaging imIn;
    Imaging imOut;

    int op;
    if (!PyArg_ParseTuple(args, "i", &op))
	return NULL;

    imIn = self->image;
    
    switch (op) {
    case 0: /* flip left right */
    case 1: /* flip top bottom */
    case 3: /* rotate 180 */
        imOut = ImagingNew(imIn->mode, imIn->xsize, imIn->ysize);
        break;
    case 2: /* rotate 90 */
    case 4: /* rotate 270 */
        imOut = ImagingNew(imIn->mode, imIn->ysize, imIn->xsize);
        break;
    default:
        PyErr_SetString(PyExc_ValueError, "No such transpose operation");
        return NULL;
    }

    if (imOut)
        switch (op) {
        case 0:
            (void) ImagingFlipLeftRight(imOut, imIn);
            break;
        case 1:
            (void) ImagingFlipTopBottom(imOut, imIn);
            break;
        case 2:
            (void) ImagingRotate90(imOut, imIn);
            break;
        case 3:
            (void) ImagingRotate180(imOut, imIn);
            break;
        case 4:
            (void) ImagingRotate270(imOut, imIn);
            break;
        }

    return PyImagingNew(imOut);
}

#ifdef WITH_UNSHARPMASK
static PyObject* 
_unsharp_mask(ImagingObject* self, PyObject* args)
{
    Imaging imIn;
    Imaging imOut;

    float radius;
    int percent, threshold;
    if (!PyArg_ParseTuple(args, "fii", &radius, &percent, &threshold))
        return NULL;


    imIn = self->image;
    imOut = ImagingNew(imIn->mode, imIn->xsize, imIn->ysize);
    if (!imOut)
        return NULL;

    if (!ImagingUnsharpMask(imIn, imOut, radius, percent, threshold))
        return NULL;

    return PyImagingNew(imOut);
}
#endif

/* -------------------------------------------------------------------- */

static PyObject* 
_isblock(ImagingObject* self, PyObject* args)
{
    return PyInt_FromLong((long) self->image->block);
}

static PyObject* 
_getbbox(ImagingObject* self, PyObject* args)
{
    int bbox[4];
    if (!ImagingGetBBox(self->image, bbox)) {
	Py_INCREF(Py_None);
	return Py_None;
    }

    return Py_BuildValue("iiii", bbox[0], bbox[1], bbox[2], bbox[3]);
}

static PyObject* 
_getcolors(ImagingObject* self, PyObject* args)
{
    ImagingColorItem* items;
    int i, colors;
    PyObject* out;

    int maxcolors = 256;
    if (!PyArg_ParseTuple(args, "i:getcolors", &maxcolors))
	return NULL;

    items = ImagingGetColors(self->image, maxcolors, &colors);
    if (!items)
        return NULL;

    if (colors > maxcolors) {
        out = Py_None;
        Py_INCREF(out);
    } else {
        out = PyList_New(colors);
        for (i = 0; i < colors; i++) {
            ImagingColorItem* v = &items[i];
            PyObject* item = Py_BuildValue(
                "iN", v->count, getpixel(self->image, self->access, v->x, v->y)
                );
            PyList_SetItem(out, i, item);
        }
    }

    free(items);

    return out;
}

static PyObject* 
_getextrema(ImagingObject* self, PyObject* args)
{
    union {
        UINT8 u[2];
        INT32 i[2];
        FLOAT32 f[2];
    } extrema;
    int status;
    
    status = ImagingGetExtrema(self->image, &extrema);
    if (status < 0)
        return NULL;

    if (status)
        switch (self->image->type) {
        case IMAGING_TYPE_UINT8:
            return Py_BuildValue("ii", extrema.u[0], extrema.u[1]);
        case IMAGING_TYPE_INT32:
            return Py_BuildValue("ii", extrema.i[0], extrema.i[1]);
        case IMAGING_TYPE_FLOAT32:
            return Py_BuildValue("dd", extrema.f[0], extrema.f[1]);
        }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* 
_getprojection(ImagingObject* self, PyObject* args)
{
    unsigned char* xprofile;
    unsigned char* yprofile;
    PyObject* result;

    xprofile = malloc(self->image->xsize);
    yprofile = malloc(self->image->ysize);

    if (xprofile == NULL || yprofile == NULL) {
	free(xprofile);
	free(yprofile);
	return PyErr_NoMemory();
    }

    ImagingGetProjection(self->image, (unsigned char *)xprofile, (unsigned char *)yprofile);

    result = Py_BuildValue("s#s#", xprofile, self->image->xsize,
			   yprofile, self->image->ysize);

    free(xprofile);
    free(yprofile);

    return result;
}

/* -------------------------------------------------------------------- */

static PyObject* 
_getband(ImagingObject* self, PyObject* args)
{
    int band;

    if (!PyArg_ParseTuple(args, "i", &band))
	return NULL;

    return PyImagingNew(ImagingGetBand(self->image, band));
}

static PyObject* 
_fillband(ImagingObject* self, PyObject* args)
{
    int band;
    int color;

    if (!PyArg_ParseTuple(args, "ii", &band, &color))
	return NULL;

    if (!ImagingFillBand(self->image, band, color))
        return NULL;
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* 
_putband(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;
    int band;
    if (!PyArg_ParseTuple(args, "O!i",
			  &Imaging_Type, &imagep,
			  &band))
	return NULL;

    if (!ImagingPutBand(self->image, imagep->image, band))
	return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

/* -------------------------------------------------------------------- */

#ifdef WITH_IMAGECHOPS

static PyObject* 
_chop_invert(ImagingObject* self, PyObject* args)
{
    return PyImagingNew(ImagingNegative(self->image));
}

static PyObject* 
_chop_lighter(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;

    if (!PyArg_ParseTuple(args, "O!", &Imaging_Type, &imagep))
	return NULL;

    return PyImagingNew(ImagingChopLighter(self->image, imagep->image));
}

static PyObject* 
_chop_darker(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;

    if (!PyArg_ParseTuple(args, "O!", &Imaging_Type, &imagep))
	return NULL;

    return PyImagingNew(ImagingChopDarker(self->image, imagep->image));
}

static PyObject* 
_chop_difference(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;

    if (!PyArg_ParseTuple(args, "O!", &Imaging_Type, &imagep))
	return NULL;

    return PyImagingNew(ImagingChopDifference(self->image, imagep->image));
}

static PyObject* 
_chop_multiply(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;

    if (!PyArg_ParseTuple(args, "O!", &Imaging_Type, &imagep))
	return NULL;

    return PyImagingNew(ImagingChopMultiply(self->image, imagep->image));
}

static PyObject* 
_chop_screen(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;

    if (!PyArg_ParseTuple(args, "O!", &Imaging_Type, &imagep))
	return NULL;

    return PyImagingNew(ImagingChopScreen(self->image, imagep->image));
}

static PyObject* 
_chop_add(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;
    float scale;
    int offset;

    scale = 1.0;
    offset = 0;

    if (!PyArg_ParseTuple(args, "O!|fi", &Imaging_Type, &imagep,
			  &scale, &offset))
	return NULL;

    return PyImagingNew(ImagingChopAdd(self->image, imagep->image,
				       scale, offset));
}

static PyObject* 
_chop_subtract(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;
    float scale;
    int offset;

    scale = 1.0;
    offset = 0;

    if (!PyArg_ParseTuple(args, "O!|fi", &Imaging_Type, &imagep,
			  &scale, &offset))
	return NULL;

    return PyImagingNew(ImagingChopSubtract(self->image, imagep->image,
					    scale, offset));
}

static PyObject* 
_chop_and(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;

    if (!PyArg_ParseTuple(args, "O!", &Imaging_Type, &imagep))
	return NULL;

    return PyImagingNew(ImagingChopAnd(self->image, imagep->image));
}

static PyObject* 
_chop_or(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;

    if (!PyArg_ParseTuple(args, "O!", &Imaging_Type, &imagep))
	return NULL;

    return PyImagingNew(ImagingChopOr(self->image, imagep->image));
}

static PyObject* 
_chop_xor(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;

    if (!PyArg_ParseTuple(args, "O!", &Imaging_Type, &imagep))
	return NULL;

    return PyImagingNew(ImagingChopXor(self->image, imagep->image));
}

static PyObject* 
_chop_add_modulo(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;

    if (!PyArg_ParseTuple(args, "O!", &Imaging_Type, &imagep))
	return NULL;

    return PyImagingNew(ImagingChopAddModulo(self->image, imagep->image));
}

static PyObject* 
_chop_subtract_modulo(ImagingObject* self, PyObject* args)
{
    ImagingObject* imagep;

    if (!PyArg_ParseTuple(args, "O!", &Imaging_Type, &imagep))
	return NULL;

    return PyImagingNew(ImagingChopSubtractModulo(self->image, imagep->image));
}

#endif


/* -------------------------------------------------------------------- */

#ifdef WITH_IMAGEDRAW

static PyObject*
_font_new(PyObject* self_, PyObject* args)
{
    ImagingFontObject *self;
    int i, y0, y1;
    static const char* wrong_length = "descriptor table has wrong size";

    ImagingObject* imagep;
    unsigned char* glyphdata;
    int glyphdata_length;
    if (!PyArg_ParseTuple(args, "O!s#",
			  &Imaging_Type, &imagep,
			  &glyphdata, &glyphdata_length))
        return NULL;

    if (glyphdata_length != 256 * 20) {
	PyErr_SetString(PyExc_ValueError, wrong_length);
	return NULL;
    }

    self = PyObject_New(ImagingFontObject, &ImagingFont_Type);
    if (self == NULL)
	return NULL;

    /* glyph bitmap */
    self->bitmap = imagep->image;

    y0 = y1 = 0;

    /* glyph glyphs */
    for (i = 0; i < 256; i++) {
        self->glyphs[i].dx = S16(B16(glyphdata, 0));
        self->glyphs[i].dy = S16(B16(glyphdata, 2));
        self->glyphs[i].dx0 = S16(B16(glyphdata, 4));
        self->glyphs[i].dy0 = S16(B16(glyphdata, 6));
        self->glyphs[i].dx1 = S16(B16(glyphdata, 8));
        self->glyphs[i].dy1 = S16(B16(glyphdata, 10));
        self->glyphs[i].sx0 = S16(B16(glyphdata, 12));
        self->glyphs[i].sy0 = S16(B16(glyphdata, 14));
        self->glyphs[i].sx1 = S16(B16(glyphdata, 16));
        self->glyphs[i].sy1 = S16(B16(glyphdata, 18));
        if (self->glyphs[i].dy0 < y0)
            y0 = self->glyphs[i].dy0;
        if (self->glyphs[i].dy1 > y1)
            y1 = self->glyphs[i].dy1;
        glyphdata += 20;
    }

    self->baseline = -y0;
    self->ysize = y1 - y0;

    /* keep a reference to the bitmap object */
    Py_INCREF(imagep);
    self->ref = imagep;

    return (PyObject*) self;
}

static void
_font_dealloc(ImagingFontObject* self)
{
    Py_XDECREF(self->ref);
    PyObject_Del(self);
}

static inline int
textwidth(ImagingFontObject* self, const unsigned char* text)
{
    int xsize;

    for (xsize = 0; *text; text++)
        xsize += self->glyphs[*text].dx;

    return xsize;
}

static PyObject*
_font_getmask(ImagingFontObject* self, PyObject* args)
{
    Imaging im;
    Imaging bitmap;
    int x, b;
    int status;
    Glyph* glyph;

    unsigned char* text;
    char* mode = "";
    if (!PyArg_ParseTuple(args, "s|s:getmask", &text, &mode))
        return NULL;

    im = ImagingNew(self->bitmap->mode, textwidth(self, text), self->ysize);
    if (!im)
        return NULL;

    b = 0;
    (void) ImagingFill(im, &b);

    b = self->baseline;
    for (x = 0; *text; text++) {
        glyph = &self->glyphs[*text];
        bitmap = ImagingCrop(
            self->bitmap,
            glyph->sx0, glyph->sy0, glyph->sx1, glyph->sy1
            );
        if (!bitmap)
            goto failed;
        status = ImagingPaste(
            im, bitmap, NULL,
            glyph->dx0+x, glyph->dy0+b, glyph->dx1+x, glyph->dy1+b
            );
        ImagingDelete(bitmap);
        if (status < 0)
            goto failed;
        x = x + glyph->dx;
        b = b + glyph->dy;
    }

    return PyImagingNew(im);

  failed:
    ImagingDelete(im);
    return NULL;
}

static PyObject*
_font_getsize(ImagingFontObject* self, PyObject* args)
{
    unsigned char* text;
    if (!PyArg_ParseTuple(args, "s:getsize", &text))
        return NULL;

    return Py_BuildValue("ii", textwidth(self, text), self->ysize);
}

static struct PyMethodDef _font_methods[] = {
    {"getmask", (PyCFunction)_font_getmask, 1},
    {"getsize", (PyCFunction)_font_getsize, 1},
    {NULL, NULL} /* sentinel */
};

static PyObject*  
_font_getattr(ImagingFontObject* self, char* name)
{
    return Py_FindMethod(_font_methods, (PyObject*) self, name);
}

/* -------------------------------------------------------------------- */

static PyObject*
_draw_new(PyObject* self_, PyObject* args)
{
    ImagingDrawObject *self;

    ImagingObject* imagep;
    int blend = 0;
    if (!PyArg_ParseTuple(args, "O!|i", &Imaging_Type, &imagep, &blend))
        return NULL;

    self = PyObject_New(ImagingDrawObject, &ImagingDraw_Type);
    if (self == NULL)
	return NULL;

    /* keep a reference to the image object */
    Py_INCREF(imagep);
    self->image = imagep;

    self->ink[0] = self->ink[1] = self->ink[2] = self->ink[3] = 0;

    self->blend = blend;

    return (PyObject*) self;
}

static void
_draw_dealloc(ImagingDrawObject* self)
{
    Py_XDECREF(self->image);
    PyObject_Del(self);
}

extern int PyPath_Flatten(PyObject* data, double **xy);

static PyObject* 
_draw_ink(ImagingDrawObject* self, PyObject* args)
{
    INT32 ink = 0;
    PyObject* color;
    char* mode = NULL; /* not used in this release */
    if (!PyArg_ParseTuple(args, "O|s", &color, &mode))
        return NULL;

    if (!getink(color, self->image->image, (char*) &ink))
        return NULL;

    return PyInt_FromLong((int) ink);
}

static PyObject* 
_draw_arc(ImagingDrawObject* self, PyObject* args)
{
    int x0, y0, x1, y1;
    int ink;
    int start, end;
    int op = 0;
    if (!PyArg_ParseTuple(args, "(iiii)iii|i",
                          &x0, &y0, &x1, &y1,
                          &start, &end, &ink))
	return NULL;

    if (ImagingDrawArc(self->image->image, x0, y0, x1, y1, start, end,
                       &ink, op) < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* 
_draw_bitmap(ImagingDrawObject* self, PyObject* args)
{
    double *xy;
    int n;

    PyObject *data;
    ImagingObject* bitmap;
    int ink;
    if (!PyArg_ParseTuple(args, "OO!i", &data, &Imaging_Type, &bitmap, &ink))
	return NULL;

    n = PyPath_Flatten(data, &xy);
    if (n < 0)
	return NULL;
    if (n != 1) {
	PyErr_SetString(
            PyExc_TypeError,
            "coordinate list must contain exactly 1 coordinate"
            );
	return NULL;
    }

    n = ImagingDrawBitmap(
        self->image->image, (int) xy[0], (int) xy[1], bitmap->image,
        &ink, self->blend
        );

    free(xy);

    if (n < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* 
_draw_chord(ImagingDrawObject* self, PyObject* args)
{
    int x0, y0, x1, y1;
    int ink, fill;
    int start, end;
    if (!PyArg_ParseTuple(args, "(iiii)iiii",
                          &x0, &y0, &x1, &y1, &start, &end, &ink, &fill))
	return NULL;

    if (ImagingDrawChord(self->image->image, x0, y0, x1, y1,
                         start, end, &ink, fill, self->blend) < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* 
_draw_ellipse(ImagingDrawObject* self, PyObject* args)
{
    double* xy;
    int n;

    PyObject* data;
    int ink;
    int fill = 0;
    if (!PyArg_ParseTuple(args, "Oi|i", &data, &ink, &fill))
	return NULL;

    n = PyPath_Flatten(data, &xy);
    if (n < 0)
	return NULL;
    if (n != 2) {
	PyErr_SetString(
            PyExc_TypeError,
            "coordinate list must contain exactly 2 coordinates"
            );
	return NULL;
    }

    n = ImagingDrawEllipse(
        self->image->image, (int) xy[0], (int) xy[1], (int) xy[2], (int) xy[3],
        &ink, fill, self->blend
        );
    
    free(xy);

    if (n < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* 
_draw_line(ImagingDrawObject* self, PyObject* args)
{
    int x0, y0, x1, y1;
    int ink;
    if (!PyArg_ParseTuple(args, "(ii)(ii)i", &x0, &y0, &x1, &y1, &ink))
	return NULL;

    if (ImagingDrawLine(self->image->image, x0, y0, x1, y1,
                        &ink, self->blend) < 0)
	return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* 
_draw_lines(ImagingDrawObject* self, PyObject* args)
{
    double *xy;
    int i, n;

    PyObject *data;
    int ink;
    int width = 0;
    if (!PyArg_ParseTuple(args, "Oi|i", &data, &ink, &width))
	return NULL;

    n = PyPath_Flatten(data, &xy);
    if (n < 0)
	return NULL;

    if (width <= 1) {
        double *p = NULL;
	for (i = 0; i < n-1; i++) {
            p = &xy[i+i];
            if (ImagingDrawLine(
                    self->image->image,
                    (int) p[0], (int) p[1], (int) p[2], (int) p[3],
                    &ink, self->blend) < 0) {
                free(xy);
                return NULL;
            }
        }
        if (p) /* draw last point */
            ImagingDrawPoint(
                    self->image->image,
                    (int) p[2], (int) p[3],
                    &ink, self->blend
                );
    } else {
        for (i = 0; i < n-1; i++) {
            double *p = &xy[i+i];
            if (ImagingDrawWideLine(
                    self->image->image,
                    (int) p[0], (int) p[1], (int) p[2], (int) p[3],
                    &ink, width, self->blend) < 0) {
                free(xy);
                return NULL;
            }
        }
    }

    free(xy);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* 
_draw_point(ImagingDrawObject* self, PyObject* args)
{
    int x, y;
    int ink;
    if (!PyArg_ParseTuple(args, "(ii)i", &x, &y, &ink))
	return NULL;

    if (ImagingDrawPoint(self->image->image, x, y, &ink, self->blend) < 0)
	return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* 
_draw_points(ImagingDrawObject* self, PyObject* args)
{
    double *xy;
    int i, n;

    PyObject *data;
    int ink;
    if (!PyArg_ParseTuple(args, "Oi", &data, &ink))
	return NULL;

    n = PyPath_Flatten(data, &xy);
    if (n < 0)
	return NULL;

    for (i = 0; i < n; i++) {
	double *p = &xy[i+i];
	if (ImagingDrawPoint(self->image->image, (int) p[0], (int) p[1],
                             &ink, self->blend) < 0) {
	    free(xy);
	    return NULL;
	}
    }

    free(xy);

    Py_INCREF(Py_None);
    return Py_None;
}

#ifdef	WITH_ARROW

/* from outline.c */
extern ImagingOutline PyOutline_AsOutline(PyObject* outline);

static PyObject* 
_draw_outline(ImagingDrawObject* self, PyObject* args)
{
    ImagingOutline outline;

    PyObject* outline_;
    int ink;
    int fill = 0;
    if (!PyArg_ParseTuple(args, "Oi|i", &outline_, &ink, &fill))
	return NULL;

    outline = PyOutline_AsOutline(outline_);
    if (!outline) {
        PyErr_SetString(PyExc_TypeError, "expected outline object");
        return NULL;
    }

    if (ImagingDrawOutline(self->image->image, outline,
                           &ink, fill, self->blend) < 0)
	return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

#endif

static PyObject* 
_draw_pieslice(ImagingDrawObject* self, PyObject* args)
{
    int x0, y0, x1, y1;
    int ink, fill;
    int start, end;
    if (!PyArg_ParseTuple(args, "(iiii)iiii",
                          &x0, &y0, &x1, &y1, &start, &end, &ink, &fill))
	return NULL;

    if (ImagingDrawPieslice(self->image->image, x0, y0, x1, y1,
                            start, end, &ink, fill, self->blend) < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* 
_draw_polygon(ImagingDrawObject* self, PyObject* args)
{
    double *xy;
    int *ixy;
    int n, i;

    PyObject* data;
    int ink;
    int fill = 0;
    if (!PyArg_ParseTuple(args, "Oi|i", &data, &ink, &fill))
	return NULL;

    n = PyPath_Flatten(data, &xy);
    if (n < 0)
	return NULL;
    if (n < 2) {
	PyErr_SetString(
            PyExc_TypeError,
            "coordinate list must contain at least 2 coordinates"
            );
	return NULL;
    }

    /* Copy list of vertices to array */
    ixy = (int*) malloc(n * 2 * sizeof(int));

    for (i = 0; i < n; i++) {
	ixy[i+i] = (int) xy[i+i];
	ixy[i+i+1] = (int) xy[i+i+1];
    }

    free(xy);

    if (ImagingDrawPolygon(self->image->image, n, ixy,
                           &ink, fill, self->blend) < 0) {
	free(ixy);
	return NULL;
    }

    free(ixy);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* 
_draw_rectangle(ImagingDrawObject* self, PyObject* args)
{
    double* xy;
    int n;

    PyObject* data;
    int ink;
    int fill = 0;
    if (!PyArg_ParseTuple(args, "Oi|i", &data, &ink, &fill))
	return NULL;

    n = PyPath_Flatten(data, &xy);
    if (n < 0)
	return NULL;
    if (n != 2) {
	PyErr_SetString(
            PyExc_TypeError,
            "coordinate list must contain exactly 2 coordinates"
            );
	return NULL;
    }

    n = ImagingDrawRectangle(
        self->image->image, (int) xy[0], (int) xy[1],
        (int) xy[2], (int) xy[3], &ink, fill, self->blend
        );
    
    free(xy);

    if (n < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static struct PyMethodDef _draw_methods[] = {
#ifdef WITH_IMAGEDRAW
    /* Graphics (ImageDraw) */
    {"draw_line", (PyCFunction)_draw_line, 1},
    {"draw_lines", (PyCFunction)_draw_lines, 1},
#ifdef WITH_ARROW
    {"draw_outline", (PyCFunction)_draw_outline, 1},
#endif
    {"draw_polygon", (PyCFunction)_draw_polygon, 1},
    {"draw_rectangle", (PyCFunction)_draw_rectangle, 1},
    {"draw_point", (PyCFunction)_draw_point, 1},
    {"draw_points", (PyCFunction)_draw_points, 1},
    {"draw_arc", (PyCFunction)_draw_arc, 1},
    {"draw_bitmap", (PyCFunction)_draw_bitmap, 1},
    {"draw_chord", (PyCFunction)_draw_chord, 1},
    {"draw_ellipse", (PyCFunction)_draw_ellipse, 1},
    {"draw_pieslice", (PyCFunction)_draw_pieslice, 1},
    {"draw_ink", (PyCFunction)_draw_ink, 1},
#endif
    {NULL, NULL} /* sentinel */
};

static PyObject*  
_draw_getattr(ImagingDrawObject* self, char* name)
{
    return Py_FindMethod(_draw_methods, (PyObject*) self, name);
}

#endif


static PyObject*
pixel_access_new(ImagingObject* imagep, PyObject* args)
{
    PixelAccessObject *self;

    int readonly = 0;
    if (!PyArg_ParseTuple(args, "|i", &readonly))
        return NULL;

    self = PyObject_New(PixelAccessObject, &PixelAccess_Type);
    if (self == NULL)
	return NULL;

    /* keep a reference to the image object */
    Py_INCREF(imagep);
    self->image = imagep;

    self->readonly = readonly;

    return (PyObject*) self;
}

static void
pixel_access_dealloc(PixelAccessObject* self)
{
    Py_XDECREF(self->image);
    PyObject_Del(self);
}

static PyObject *
pixel_access_getitem(PixelAccessObject *self, PyObject *xy)
{
    int x, y;
    if (_getxy(xy, &x, &y))
        return NULL;

    return getpixel(self->image->image, self->image->access, x, y);
}

static int
pixel_access_setitem(PixelAccessObject *self, PyObject *xy, PyObject *color)
{
    Imaging im = self->image->image;
    char ink[4];
    int x, y;

    if (self->readonly) {
        (void) ImagingError_ValueError(readonly);
        return -1;
    }

    if (_getxy(xy, &x, &y))
        return -1;

    if (x < 0 || x >= im->xsize || y < 0 || y >= im->ysize) {
	PyErr_SetString(PyExc_IndexError, outside_image);
	return -1;
    }

    if (!color) /* FIXME: raise exception? */
        return 0;

    if (!getink(color, im, ink))
        return -1;

    self->image->access->put_pixel(im, x, y, ink);

    return 0;
}

/* -------------------------------------------------------------------- */
/* EFFECTS (experimental)        					*/
/* -------------------------------------------------------------------- */

#ifdef WITH_EFFECTS

static PyObject* 
_effect_mandelbrot(ImagingObject* self, PyObject* args)
{
    int xsize = 512;
    int ysize = 512;
    double extent[4];
    int quality = 100;

    extent[0] = -3; extent[1] = -2.5;
    extent[2] = 2;  extent[3] = 2.5;

    if (!PyArg_ParseTuple(args, "|(ii)(dddd)i", &xsize, &ysize,
                          &extent[0], &extent[1], &extent[2], &extent[3],
                          &quality))
	return NULL;

    return PyImagingNew(ImagingEffectMandelbrot(xsize, ysize, extent, quality));
}

static PyObject* 
_effect_noise(ImagingObject* self, PyObject* args)
{
    int xsize, ysize;
    float sigma = 128;
    if (!PyArg_ParseTuple(args, "(ii)|f", &xsize, &ysize, &sigma))
	return NULL;

    return PyImagingNew(ImagingEffectNoise(xsize, ysize, sigma));
}

static PyObject* 
_effect_spread(ImagingObject* self, PyObject* args)
{
    int dist;

    if (!PyArg_ParseTuple(args, "i", &dist))
	return NULL;

    return PyImagingNew(ImagingEffectSpread(self->image, dist));
}

#endif

/* -------------------------------------------------------------------- */
/* UTILITIES								*/
/* -------------------------------------------------------------------- */

static PyObject* 
_crc32(PyObject* self, PyObject* args)
{
    unsigned char* buffer;
    int bytes;
    int hi, lo;
    UINT32 crc;

    hi = lo = 0;

    if (!PyArg_ParseTuple(args, "s#|(ii)", &buffer, &bytes, &hi, &lo))
	return NULL;

    crc = ((UINT32) (hi & 0xFFFF) << 16) + (lo & 0xFFFF);

    crc = ImagingCRC32(crc, (unsigned char *)buffer, bytes);

    return Py_BuildValue("ii", (crc >> 16) & 0xFFFF, crc & 0xFFFF);
}

static PyObject* 
_getcodecstatus(PyObject* self, PyObject* args)
{
    int status;
    char* msg;

    if (!PyArg_ParseTuple(args, "i", &status))
	return NULL;

    switch (status) {
    case IMAGING_CODEC_OVERRUN:
	msg = "buffer overrun"; break;
    case IMAGING_CODEC_BROKEN:
	msg = "broken data stream"; break;
    case IMAGING_CODEC_UNKNOWN:
	msg = "unrecognized data stream contents"; break;
    case IMAGING_CODEC_CONFIG:
	msg = "codec configuration error"; break;
    case IMAGING_CODEC_MEMORY:
	msg = "out of memory"; break;
    default:
	Py_INCREF(Py_None);
	return Py_None;
    }

    return PyString_FromString(msg);
}

/* -------------------------------------------------------------------- */
/* DEBUGGING HELPERS							*/
/* -------------------------------------------------------------------- */


#ifdef WITH_DEBUG

static PyObject* 
_save_ppm(ImagingObject* self, PyObject* args)
{
    char* filename;

    if (!PyArg_ParseTuple(args, "s", &filename))
	return NULL;

    if (!ImagingSavePPM(self->image, filename))
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

#endif

/* -------------------------------------------------------------------- */

/* methods */

static struct PyMethodDef methods[] = {

    /* Put commonly used methods first */
    {"getpixel", (PyCFunction)_getpixel, 1},
    {"putpixel", (PyCFunction)_putpixel, 1},

    {"pixel_access", (PyCFunction)pixel_access_new, 1},

    /* Standard processing methods (Image) */
    {"convert", (PyCFunction)_convert, 1},
    {"convert2", (PyCFunction)_convert2, 1},
    {"convert_matrix", (PyCFunction)_convert_matrix, 1},
    {"copy", (PyCFunction)_copy, 1},
    {"copy2", (PyCFunction)_copy2, 1},
#ifdef WITH_CRACKCODE
    {"crackcode", (PyCFunction)_crackcode, 1},
#endif
    {"crop", (PyCFunction)_crop, 1},
    {"expand", (PyCFunction)_expand, 1},
    {"filter", (PyCFunction)_filter, 1},
    {"histogram", (PyCFunction)_histogram, 1},
#ifdef WITH_MODEFILTER
    {"modefilter", (PyCFunction)_modefilter, 1},
#endif
    {"offset", (PyCFunction)_offset, 1},
    {"paste", (PyCFunction)_paste, 1},
    {"point", (PyCFunction)_point, 1},
    {"point_transform", (PyCFunction)_point_transform, 1},
    {"putdata", (PyCFunction)_putdata, 1},
#ifdef WITH_QUANTIZE
    {"quantize", (PyCFunction)_quantize, 1},
#endif
#ifdef WITH_RANKFILTER
    {"rankfilter", (PyCFunction)_rankfilter, 1},
#endif
    {"resize", (PyCFunction)_resize, 1},
    {"rotate", (PyCFunction)_rotate, 1},
    {"stretch", (PyCFunction)_stretch, 1},
    {"transpose", (PyCFunction)_transpose, 1},
    {"transform2", (PyCFunction)_transform2, 1},

    {"isblock", (PyCFunction)_isblock, 1},

    {"getbbox", (PyCFunction)_getbbox, 1},
    {"getcolors", (PyCFunction)_getcolors, 1},
    {"getextrema", (PyCFunction)_getextrema, 1},
    {"getprojection", (PyCFunction)_getprojection, 1},

    {"getband", (PyCFunction)_getband, 1},
    {"putband", (PyCFunction)_putband, 1},
    {"fillband", (PyCFunction)_fillband, 1},

    {"setmode", (PyCFunction)im_setmode, 1},
    
    {"getpalette", (PyCFunction)_getpalette, 1},
    {"putpalette", (PyCFunction)_putpalette, 1},
    {"putpalettealpha", (PyCFunction)_putpalettealpha, 1},

#ifdef WITH_IMAGECHOPS
    /* Channel operations (ImageChops) */
    {"chop_invert", (PyCFunction)_chop_invert, 1},
    {"chop_lighter", (PyCFunction)_chop_lighter, 1},
    {"chop_darker", (PyCFunction)_chop_darker, 1},
    {"chop_difference", (PyCFunction)_chop_difference, 1},
    {"chop_multiply", (PyCFunction)_chop_multiply, 1},
    {"chop_screen", (PyCFunction)_chop_screen, 1},
    {"chop_add", (PyCFunction)_chop_add, 1},
    {"chop_subtract", (PyCFunction)_chop_subtract, 1},
    {"chop_add_modulo", (PyCFunction)_chop_add_modulo, 1},
    {"chop_subtract_modulo", (PyCFunction)_chop_subtract_modulo, 1},
    {"chop_and", (PyCFunction)_chop_and, 1},
    {"chop_or", (PyCFunction)_chop_or, 1},
    {"chop_xor", (PyCFunction)_chop_xor, 1},
#endif

#ifdef WITH_UNSHARPMASK
    /* Kevin Cazabon's unsharpmask extension */
    {"gaussian_blur", (PyCFunction)_gaussian_blur, 1},
    {"unsharp_mask", (PyCFunction)_unsharp_mask, 1},
#endif

#ifdef WITH_EFFECTS
    /* Special effects */
    {"effect_spread", (PyCFunction)_effect_spread, 1},
#endif

    /* Misc. */
    {"new_array", (PyCFunction)_new_array, 1},
    {"new_block", (PyCFunction)_new_block, 1},

#ifdef WITH_DEBUG
    {"save_ppm", (PyCFunction)_save_ppm, 1},
#endif

    {NULL, NULL} /* sentinel */
};


/* attributes */

static PyObject*  
_getattr(ImagingObject* self, char* name)
{
    PyObject* res;

    res = Py_FindMethod(methods, (PyObject*) self, name);
    if (res)
	return res;
    PyErr_Clear();
    if (strcmp(name, "mode") == 0)
	return PyString_FromString(self->image->mode);
    if (strcmp(name, "size") == 0)
	return Py_BuildValue("ii", self->image->xsize, self->image->ysize);
    if (strcmp(name, "bands") == 0)
	return PyInt_FromLong(self->image->bands);
    if (strcmp(name, "id") == 0)
	return PyInt_FromLong((long) self->image);
    if (strcmp(name, "ptr") == 0)
        return PyCObject_FromVoidPtrAndDesc(self->image, IMAGING_MAGIC, NULL);
    PyErr_SetString(PyExc_AttributeError, name);
    return NULL;
}


/* basic sequence semantics */

static Py_ssize_t
image_length(ImagingObject *self)
{
    Imaging im = self->image;

    return im->xsize * im->ysize;
}

static PyObject *
image_item(ImagingObject *self, Py_ssize_t i)
{
    int x, y;
    Imaging im = self->image;

    if (im->xsize > 0) {
        x = i % im->xsize;
        y = i / im->xsize;
    } else
        x = y = 0; /* leave it to getpixel to raise an exception */

    return getpixel(im, self->access, x, y);
}

static PySequenceMethods image_as_sequence = {
    (inquiry) image_length, /*sq_length*/
    (binaryfunc) NULL, /*sq_concat*/
    (ssizeargfunc) NULL, /*sq_repeat*/
    (ssizeargfunc) image_item, /*sq_item*/
    (ssizessizeargfunc) NULL, /*sq_slice*/
    (ssizeobjargproc) NULL, /*sq_ass_item*/
    (ssizessizeobjargproc) NULL, /*sq_ass_slice*/
};


/* type description */

statichere PyTypeObject Imaging_Type = {
    PyObject_HEAD_INIT(NULL)
    0,				/*ob_size*/
    "ImagingCore",		/*tp_name*/
    sizeof(ImagingObject),	/*tp_size*/
    0,				/*tp_itemsize*/
    /* methods */
    (destructor)_dealloc,	/*tp_dealloc*/
    0,				/*tp_print*/
    (getattrfunc)_getattr,	/*tp_getattr*/
    0,				/*tp_setattr*/
    0,				/*tp_compare*/
    0,				/*tp_repr*/
    0,                          /*tp_as_number */
    &image_as_sequence,         /*tp_as_sequence */
    0,                          /*tp_as_mapping */
    0                           /*tp_hash*/
};

#ifdef WITH_IMAGEDRAW

statichere PyTypeObject ImagingFont_Type = {
    PyObject_HEAD_INIT(NULL)
    0,				/*ob_size*/
    "ImagingFont",		/*tp_name*/
    sizeof(ImagingFontObject),	/*tp_size*/
    0,				/*tp_itemsize*/
    /* methods */
    (destructor)_font_dealloc,	/*tp_dealloc*/
    0,				/*tp_print*/
    (getattrfunc)_font_getattr,	/*tp_getattr*/
};

statichere PyTypeObject ImagingDraw_Type = {
    PyObject_HEAD_INIT(NULL)
    0,				/*ob_size*/
    "ImagingDraw",		/*tp_name*/
    sizeof(ImagingDrawObject),	/*tp_size*/
    0,				/*tp_itemsize*/
    /* methods */
    (destructor)_draw_dealloc,	/*tp_dealloc*/
    0,				/*tp_print*/
    (getattrfunc)_draw_getattr,	/*tp_getattr*/
};

#endif

static PyMappingMethods pixel_access_as_mapping = {
    (inquiry) NULL, /*mp_length*/
    (binaryfunc) pixel_access_getitem, /*mp_subscript*/
    (objobjargproc) pixel_access_setitem, /*mp_ass_subscript*/
};

/* type description */

statichere PyTypeObject PixelAccess_Type = {
    PyObject_HEAD_INIT(NULL)
    0, "PixelAccess", sizeof(PixelAccessObject), 0,
    /* methods */
    (destructor)pixel_access_dealloc, /*tp_dealloc*/
    0, /*tp_print*/
    0, /*tp_getattr*/
    0, /*tp_setattr*/
    0, /*tp_compare*/
    0, /*tp_repr*/
    0, /*tp_as_number */
    0, /*tp_as_sequence */
    &pixel_access_as_mapping, /*tp_as_mapping */
    0 /*tp_hash*/
};

/* -------------------------------------------------------------------- */

/* FIXME: this is something of a mess.  Should replace this with
   pluggable codecs, but not before PIL 1.2 */

/* Decoders (in decode.c) */
extern PyObject* PyImaging_BitDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_FliDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_GifDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_HexDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_JpegDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_TiffLzwDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_MspDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_PackbitsDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_PcdDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_PcxDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_RawDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_SunRleDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_TgaRleDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_XbmDecoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_ZipDecoderNew(PyObject* self, PyObject* args);

/* Encoders (in encode.c) */
extern PyObject* PyImaging_EpsEncoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_GifEncoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_JpegEncoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_PcxEncoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_RawEncoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_XbmEncoderNew(PyObject* self, PyObject* args);
extern PyObject* PyImaging_ZipEncoderNew(PyObject* self, PyObject* args);

/* Display support etc (in display.c) */
#ifdef WIN32
extern PyObject* PyImaging_CreateWindowWin32(PyObject* self, PyObject* args);
extern PyObject* PyImaging_DisplayWin32(PyObject* self, PyObject* args);
extern PyObject* PyImaging_DisplayModeWin32(PyObject* self, PyObject* args);
extern PyObject* PyImaging_GrabScreenWin32(PyObject* self, PyObject* args);
extern PyObject* PyImaging_GrabClipboardWin32(PyObject* self, PyObject* args);
extern PyObject* PyImaging_ListWindowsWin32(PyObject* self, PyObject* args);
extern PyObject* PyImaging_EventLoopWin32(PyObject* self, PyObject* args);
extern PyObject* PyImaging_DrawWmf(PyObject* self, PyObject* args);
#endif

/* Experimental path stuff (in path.c) */
extern PyObject* PyPath_Create(ImagingObject* self, PyObject* args);

/* Experimental outline stuff (in outline.c) */
extern PyObject* PyOutline_Create(ImagingObject* self, PyObject* args);

extern PyObject* PyImaging_Mapper(PyObject* self, PyObject* args);
extern PyObject* PyImaging_MapBuffer(PyObject* self, PyObject* args);

static PyMethodDef functions[] = {

    /* Object factories */
    {"blend", (PyCFunction)_blend, 1},
    {"fill", (PyCFunction)_fill, 1},
    {"new", (PyCFunction)_new, 1},

    {"getcount", (PyCFunction)_getcount, 1},

    /* Functions */
    {"convert", (PyCFunction)_convert2, 1},
    {"copy", (PyCFunction)_copy2, 1},

    /* Codecs */
    {"bit_decoder", (PyCFunction)PyImaging_BitDecoderNew, 1},
    {"eps_encoder", (PyCFunction)PyImaging_EpsEncoderNew, 1},
    {"fli_decoder", (PyCFunction)PyImaging_FliDecoderNew, 1},
    {"gif_decoder", (PyCFunction)PyImaging_GifDecoderNew, 1},
    {"gif_encoder", (PyCFunction)PyImaging_GifEncoderNew, 1},
    {"hex_decoder", (PyCFunction)PyImaging_HexDecoderNew, 1},
    {"hex_encoder", (PyCFunction)PyImaging_EpsEncoderNew, 1}, /* EPS=HEX! */
#ifdef HAVE_LIBJPEG
    {"jpeg_decoder", (PyCFunction)PyImaging_JpegDecoderNew, 1},
    {"jpeg_encoder", (PyCFunction)PyImaging_JpegEncoderNew, 1},
#endif
    {"tiff_lzw_decoder", (PyCFunction)PyImaging_TiffLzwDecoderNew, 1},
    {"msp_decoder", (PyCFunction)PyImaging_MspDecoderNew, 1},
    {"packbits_decoder", (PyCFunction)PyImaging_PackbitsDecoderNew, 1},
    {"pcd_decoder", (PyCFunction)PyImaging_PcdDecoderNew, 1},
    {"pcx_decoder", (PyCFunction)PyImaging_PcxDecoderNew, 1},
    {"pcx_encoder", (PyCFunction)PyImaging_PcxEncoderNew, 1},
    {"raw_decoder", (PyCFunction)PyImaging_RawDecoderNew, 1},
    {"raw_encoder", (PyCFunction)PyImaging_RawEncoderNew, 1},
    {"sun_rle_decoder", (PyCFunction)PyImaging_SunRleDecoderNew, 1},
    {"tga_rle_decoder", (PyCFunction)PyImaging_TgaRleDecoderNew, 1},
    {"xbm_decoder", (PyCFunction)PyImaging_XbmDecoderNew, 1},
    {"xbm_encoder", (PyCFunction)PyImaging_XbmEncoderNew, 1},
#ifdef HAVE_LIBZ
    {"zip_decoder", (PyCFunction)PyImaging_ZipDecoderNew, 1},
    {"zip_encoder", (PyCFunction)PyImaging_ZipEncoderNew, 1},
#endif

    /* Memory mapping */
#ifdef WITH_MAPPING
#ifdef WIN32
    {"map", (PyCFunction)PyImaging_Mapper, 1},
#endif
    {"map_buffer", (PyCFunction)PyImaging_MapBuffer, 1},
#endif

    /* Display support */
#ifdef WIN32
    {"display", (PyCFunction)PyImaging_DisplayWin32, 1},
    {"display_mode", (PyCFunction)PyImaging_DisplayModeWin32, 1},
    {"grabscreen", (PyCFunction)PyImaging_GrabScreenWin32, 1},
    {"grabclipboard", (PyCFunction)PyImaging_GrabClipboardWin32, 1},
    {"createwindow", (PyCFunction)PyImaging_CreateWindowWin32, 1},
    {"eventloop", (PyCFunction)PyImaging_EventLoopWin32, 1},
    {"listwindows", (PyCFunction)PyImaging_ListWindowsWin32, 1},
    {"drawwmf", (PyCFunction)PyImaging_DrawWmf, 1},
#endif

    /* Utilities */
    {"crc32", (PyCFunction)_crc32, 1},
    {"getcodecstatus", (PyCFunction)_getcodecstatus, 1},

    /* Debugging stuff */
    {"open_ppm", (PyCFunction)_open_ppm, 1},

    /* Special effects (experimental) */
#ifdef WITH_EFFECTS
    {"effect_mandelbrot", (PyCFunction)_effect_mandelbrot, 1},
    {"effect_noise", (PyCFunction)_effect_noise, 1},
    {"linear_gradient", (PyCFunction)_linear_gradient, 1},
    {"radial_gradient", (PyCFunction)_radial_gradient, 1},
    {"wedge", (PyCFunction)_linear_gradient, 1}, /* Compatibility */
#endif

    /* Drawing support stuff */
#ifdef WITH_IMAGEDRAW
    {"font", (PyCFunction)_font_new, 1},
    {"draw", (PyCFunction)_draw_new, 1},
#endif

    /* Experimental path stuff */
#ifdef WITH_IMAGEPATH
    {"path", (PyCFunction)PyPath_Create, 1},
#endif
    
    /* Experimental arrow graphics stuff */
#ifdef WITH_ARROW
    {"outline", (PyCFunction)PyOutline_Create, 1},
#endif

    {NULL, NULL} /* sentinel */
};

DL_EXPORT(void)
init_imaging(void)
{
    PyObject* m;
    PyObject* d;

    /* Patch object type */
    Imaging_Type.ob_type = &PyType_Type;
#ifdef WITH_IMAGEDRAW
    ImagingFont_Type.ob_type = &PyType_Type;
    ImagingDraw_Type.ob_type = &PyType_Type;
#endif
    PixelAccess_Type.ob_type = &PyType_Type;

    ImagingAccessInit();

    m = Py_InitModule("_imaging", functions);
    d = PyModule_GetDict(m);

#ifdef HAVE_LIBJPEG
  {
    extern const char* ImagingJpegVersion(void);
    PyDict_SetItemString(d, "jpeglib_version", PyString_FromString(ImagingJpegVersion()));
  }
#endif

#ifdef HAVE_LIBZ
  {
    extern const char* ImagingZipVersion(void);
    PyDict_SetItemString(d, "zlib_version", PyString_FromString(ImagingZipVersion()));
  }
#endif
}

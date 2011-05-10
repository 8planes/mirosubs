# -*- coding: utf-8 -*-
#
#  SelfTest/Util/test_number.py: Self-test for parts of the Crypto.Util.number module
#
# Written in 2008 by Dwayne C. Litzenberger <dlitz@dlitz.net>
#
# ===================================================================
# The contents of this file are dedicated to the public domain.  To
# the extent that dedication to the public domain is not available,
# everyone is granted a worldwide, perpetual, royalty-free,
# non-exclusive license to exercise all rights associated with the
# contents of this file for any purpose whatsoever.
# No rights are reserved.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ===================================================================

"""Self-tests for (some of) Crypto.Util.number"""

__revision__ = "$Id$"

from Crypto.Util.python_compat import *

import unittest

# NB: In some places, we compare tuples instead of just output values so that
# if any inputs cause a test failure, we'll be able to tell which ones.

class MiscTests(unittest.TestCase):
    def setUp(self):
        global number, math
        from Crypto.Util import number
        import math

    def test_ceil_shift(self):
        """Util.number.ceil_shift"""
        self.assertRaises(AssertionError, number.ceil_shift, -1, 1)
        self.assertRaises(AssertionError, number.ceil_shift, 1, -1)

        # b = 0
        self.assertEqual(0, number.ceil_shift(0, 0))
        self.assertEqual(1, number.ceil_shift(1, 0))
        self.assertEqual(2, number.ceil_shift(2, 0))
        self.assertEqual(3, number.ceil_shift(3, 0))

        # b = 1
        self.assertEqual(0, number.ceil_shift(0, 1))
        self.assertEqual(1, number.ceil_shift(1, 1))
        self.assertEqual(1, number.ceil_shift(2, 1))
        self.assertEqual(2, number.ceil_shift(3, 1))

        # b = 2
        self.assertEqual(0, number.ceil_shift(0, 2))
        self.assertEqual(1, number.ceil_shift(1, 2))
        self.assertEqual(1, number.ceil_shift(2, 2))
        self.assertEqual(1, number.ceil_shift(3, 2))
        self.assertEqual(1, number.ceil_shift(4, 2))
        self.assertEqual(2, number.ceil_shift(5, 2))
        self.assertEqual(2, number.ceil_shift(6, 2))
        self.assertEqual(2, number.ceil_shift(7, 2))
        self.assertEqual(2, number.ceil_shift(8, 2))
        self.assertEqual(3, number.ceil_shift(9, 2))

        for b in range(3, 1+129, 3):    # 3, 6, ... , 129
            self.assertEqual(0, number.ceil_shift(0, b))

            n = 1L
            while n <= 2L**(b+2):
                (q, r) = divmod(n-1, 2L**b)
                expected = q + int(not not r)
                self.assertEqual((n-1, b, expected),
                                 (n-1, b, number.ceil_shift(n-1, b)))

                (q, r) = divmod(n, 2L**b)
                expected = q + int(not not r)
                self.assertEqual((n, b, expected),
                                 (n, b, number.ceil_shift(n, b)))

                (q, r) = divmod(n+1, 2L**b)
                expected = q + int(not not r)
                self.assertEqual((n+1, b, expected),
                                 (n+1, b, number.ceil_shift(n+1, b)))

                n *= 2

    def test_ceil_div(self):
        """Util.number.ceil_div"""
        self.assertRaises(TypeError, number.ceil_div, "1", 1)
        self.assertRaises(ZeroDivisionError, number.ceil_div, 1, 0)
        self.assertRaises(ZeroDivisionError, number.ceil_div, -1, 0)

        # b = -1
        self.assertEqual(0, number.ceil_div(0, -1))
        self.assertEqual(-1, number.ceil_div(1, -1))
        self.assertEqual(-2, number.ceil_div(2, -1))
        self.assertEqual(-3, number.ceil_div(3, -1))

        # b = 1
        self.assertEqual(0, number.ceil_div(0, 1))
        self.assertEqual(1, number.ceil_div(1, 1))
        self.assertEqual(2, number.ceil_div(2, 1))
        self.assertEqual(3, number.ceil_div(3, 1))

        # b = 2
        self.assertEqual(0, number.ceil_div(0, 2))
        self.assertEqual(1, number.ceil_div(1, 2))
        self.assertEqual(1, number.ceil_div(2, 2))
        self.assertEqual(2, number.ceil_div(3, 2))
        self.assertEqual(2, number.ceil_div(4, 2))
        self.assertEqual(3, number.ceil_div(5, 2))

        # b = 3
        self.assertEqual(0, number.ceil_div(0, 3))
        self.assertEqual(1, number.ceil_div(1, 3))
        self.assertEqual(1, number.ceil_div(2, 3))
        self.assertEqual(1, number.ceil_div(3, 3))
        self.assertEqual(2, number.ceil_div(4, 3))
        self.assertEqual(2, number.ceil_div(5, 3))
        self.assertEqual(2, number.ceil_div(6, 3))
        self.assertEqual(3, number.ceil_div(7, 3))

        # b = 4
        self.assertEqual(0, number.ceil_div(0, 4))
        self.assertEqual(1, number.ceil_div(1, 4))
        self.assertEqual(1, number.ceil_div(2, 4))
        self.assertEqual(1, number.ceil_div(3, 4))
        self.assertEqual(1, number.ceil_div(4, 4))
        self.assertEqual(2, number.ceil_div(5, 4))
        self.assertEqual(2, number.ceil_div(6, 4))
        self.assertEqual(2, number.ceil_div(7, 4))
        self.assertEqual(2, number.ceil_div(8, 4))
        self.assertEqual(3, number.ceil_div(9, 4))

        # b = -4
        self.assertEqual(3, number.ceil_div(-9, -4))
        self.assertEqual(2, number.ceil_div(-8, -4))
        self.assertEqual(2, number.ceil_div(-7, -4))
        self.assertEqual(2, number.ceil_div(-6, -4))
        self.assertEqual(2, number.ceil_div(-5, -4))
        self.assertEqual(1, number.ceil_div(-4, -4))
        self.assertEqual(1, number.ceil_div(-3, -4))
        self.assertEqual(1, number.ceil_div(-2, -4))
        self.assertEqual(1, number.ceil_div(-1, -4))
        self.assertEqual(0, number.ceil_div(0, -4))
        self.assertEqual(0, number.ceil_div(1, -4))
        self.assertEqual(0, number.ceil_div(2, -4))
        self.assertEqual(0, number.ceil_div(3, -4))
        self.assertEqual(-1, number.ceil_div(4, -4))
        self.assertEqual(-1, number.ceil_div(5, -4))
        self.assertEqual(-1, number.ceil_div(6, -4))
        self.assertEqual(-1, number.ceil_div(7, -4))
        self.assertEqual(-2, number.ceil_div(8, -4))
        self.assertEqual(-2, number.ceil_div(9, -4))

    def test_exact_log2(self):
        """Util.number.exact_log2"""
        self.assertRaises(TypeError, number.exact_log2, "0")
        self.assertRaises(ValueError, number.exact_log2, -1)
        self.assertRaises(ValueError, number.exact_log2, 0)
        self.assertEqual(0, number.exact_log2(1))
        self.assertEqual(1, number.exact_log2(2))
        self.assertRaises(ValueError, number.exact_log2, 3)
        self.assertEqual(2, number.exact_log2(4))
        self.assertRaises(ValueError, number.exact_log2, 5)
        self.assertRaises(ValueError, number.exact_log2, 6)
        self.assertRaises(ValueError, number.exact_log2, 7)
        e = 3
        n = 8
        while e < 16:
            if n == 2**e:
                self.assertEqual(e, number.exact_log2(n), "expected=2**%d, n=%d" % (e, n))
                e += 1
            else:
                self.assertRaises(ValueError, number.exact_log2, n)
            n += 1

        for e in range(16, 1+64, 2):
            self.assertRaises(ValueError, number.exact_log2, 2L**e-1)
            self.assertEqual(e, number.exact_log2(2L**e))
            self.assertRaises(ValueError, number.exact_log2, 2L**e+1)

    def test_exact_div(self):
        """Util.number.exact_div"""

        # Positive numbers
        self.assertEqual(1, number.exact_div(1, 1))
        self.assertRaises(ValueError, number.exact_div, 1, 2)
        self.assertEqual(1, number.exact_div(2, 2))
        self.assertRaises(ValueError, number.exact_div, 3, 2)
        self.assertEqual(2, number.exact_div(4, 2))

        # Negative numbers
        self.assertEqual(-1, number.exact_div(-1, 1))
        self.assertEqual(-1, number.exact_div(1, -1))
        self.assertRaises(ValueError, number.exact_div, -1, 2)
        self.assertEqual(1, number.exact_div(-2, -2))
        self.assertEqual(-2, number.exact_div(-4, 2))

        # Zero dividend
        self.assertEqual(0, number.exact_div(0, 1))
        self.assertEqual(0, number.exact_div(0, 2))

        # Zero divisor (allow_divzero == False)
        self.assertRaises(ZeroDivisionError, number.exact_div, 0, 0)
        self.assertRaises(ZeroDivisionError, number.exact_div, 1, 0)

        # Zero divisor (allow_divzero == True)
        self.assertEqual(0, number.exact_div(0, 0, allow_divzero=True))
        self.assertRaises(ValueError, number.exact_div, 1, 0, allow_divzero=True)

    def test_floor_div(self):
        """Util.number.floor_div"""
        self.assertRaises(TypeError, number.floor_div, "1", 1)
        for a in range(-10, 10):
            for b in range(-10, 10):
                if b == 0:
                    self.assertRaises(ZeroDivisionError, number.floor_div, a, b)
                else:
                    self.assertEqual((a, b, int(math.floor(float(a) / b))),
                                     (a, b, number.floor_div(a, b)))

def get_tests(config={}):
    from Crypto.SelfTest.st_common import list_test_cases
    return list_test_cases(MiscTests)

if __name__ == '__main__':
    suite = lambda: unittest.TestSuite(get_tests())
    unittest.main(defaultTest='suite')

# vim:set ts=4 sw=4 sts=4 expandtab:

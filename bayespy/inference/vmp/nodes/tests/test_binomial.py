######################################################################
# Copyright (C) 2014 Jaakko Luttinen
#
# This file is licensed under Version 3.0 of the GNU General Public
# License. See LICENSE for a text of the license.
######################################################################

######################################################################
# This file is part of BayesPy.
#
# BayesPy is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# BayesPy is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BayesPy.  If not, see <http://www.gnu.org/licenses/>.
######################################################################

"""
Unit tests for `binomial` module.
"""

import numpy as np
import scipy

from bayespy.nodes import Binomial
from bayespy.nodes import Beta

from bayespy.utils import utils
from bayespy.utils import random

from bayespy.utils.utils import TestCase


class TestBinomial(TestCase):
    """
    Unit tests for Binomial node
    """

    
    def test_init(self):
        """
        Test the creation of binomial nodes.
        """

        # Some simple initializations
        X = Binomial(10, 0.5)
        X = Binomial(10, Beta([2,3]))

        # Check that plates are correct
        X = Binomial(10, 0.7, plates=(4,3))
        self.assertEqual(X.plates,
                         (4,3))
        X = Binomial(10, 0.7*np.ones((4,3)))
        self.assertEqual(X.plates,
                         (4,3))
        n = np.ones((4,3), dtype=np.int)
        X = Binomial(n, 0.7)
        self.assertEqual(X.plates,
                         (4,3))
        X = Binomial(10, Beta([4,3], plates=(4,3)))
        self.assertEqual(X.plates,
                         (4,3))
        
        # Invalid probability
        self.assertRaises(ValueError,
                          Binomial,
                          10,
                          -0.5)
        self.assertRaises(ValueError,
                          Binomial,
                          10,
                          1.5)

        # Invalid number of trials
        self.assertRaises(ValueError,
                          Binomial,
                          -1,
                          0.5)
        self.assertRaises(ValueError,
                          Binomial,
                          8.5,
                          0.5)

        # Inconsistent plates
        self.assertRaises(ValueError,
                          Binomial,
                          10,
                          0.5*np.ones(4),
                          plates=(3,))

        # Explicit plates too small
        self.assertRaises(ValueError,
                          Binomial,
                          10,
                          0.5*np.ones(4),
                          plates=(1,))

        pass

    
    def test_moments(self):
        """
        Test the moments of binomial nodes.
        """

        # Simple test
        X = Binomial(1, 0.7)
        u = X._message_to_child()
        self.assertEqual(len(u), 1)
        self.assertAllClose(u[0],
                            0.7)

        # Test n
        X = Binomial(10, 0.7)
        u = X._message_to_child()
        self.assertAllClose(u[0],
                            10*0.7)

        # Test plates in p
        n = np.random.randint(1, 10)
        p = np.random.rand(3)
        X = Binomial(n, p)
        u = X._message_to_child()
        self.assertAllClose(u[0],
                            p*n)
        
        # Test plates in n
        n = np.random.randint(1, 10, size=(3,))
        p = np.random.rand()
        X = Binomial(n, p)
        u = X._message_to_child()
        self.assertAllClose(u[0],
                            p*n)

        # Test plates in p and n
        n = np.random.randint(1, 10, size=(4,1))
        p = np.random.rand(3)
        X = Binomial(n, p)
        u = X._message_to_child()
        self.assertAllClose(u[0],
                            p*n)

        # Test with beta prior
        P = Beta([7, 3])
        logp = P._message_to_child()[0]
        p0 = np.exp(logp[0]) / (np.exp(logp[0]) + np.exp(logp[1]))
        X = Binomial(1, P)
        u = X._message_to_child()
        self.assertAllClose(u[0],
                            p0)

        # Test with broadcasted plates
        P = Beta([7, 3], plates=(10,))
        X = Binomial(5, P)
        u = X._message_to_child()
        self.assertAllClose(u[0] * np.ones(X.get_shape(0)),
                            5*p0*np.ones(10))

        pass

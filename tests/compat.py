# -*- coding: utf-8 -*-
# This code is distributed under the two-clause BSD license.
# Copyright (c) 2010-2013 Raphaël Barrois


import sys

version = sys.version_info

if version[0] == 2 and version[1] < 7: # pragma: no cover
    # Python 2.6 or earlier
    import unittest2 as unittest
else:
    import unittest

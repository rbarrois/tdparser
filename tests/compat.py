# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Raphaël Barrois


import sys

version = sys.version_info

if version[0] == 2 and version[1] < 7:
    # Python 2.6 or earlier
    import unittest2 as unittest
else:
    import unittest

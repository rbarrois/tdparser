#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Raphaël Barrois

"""Tests for token-related code."""


from .compat import unittest

import tdparser


class TokenTestCase(unittest.TestCase):
    def test_repr(self):
        token = tdparser.Token()
        self.assertIn("Token", repr(token))

        token2 = tdparser.Token('foo')
        self.assertIn("Token", repr(token2))
        self.assertIn("foo", repr(token2))

    def test_end_token(self):
        token = tdparser.EndToken()
        self.assertIn("End", repr(token))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Raphaël Barrois

"""Full tests."""

import re
import unittest

import tdparser


class ParenthesizedLexerTestCase(unittest.TestCase):
    """Test lexing parenthesized expressions."""

    def setUp(self):

        class RightParen(tdparser.Token):
            """A right parenthesis"""
            pass

        class LeftParen(tdparser.Token):
            """A left parenthesis"""

            def nud(self, context):
                """Read the content of the (...) block."""

                # Contains parsed data.
                contents = []
                while not isinstance(context.current_token, RightParen):
                    contents.append(context.expression())

                next_token = context.consume(RightParen)
                return [self.text] + contents + [next_token.text]

        l = tdparser.Lexer(default_tokens=False)
        l.register_token(LeftParen, re.compile(r'\('))
        l.register_token(RightParen, re.compile(r'\)'))

        self.lexer = l

    def test_trivial(self):

        expr = self.lexer.parse('()')
        self.assertEqual(['(', ')'], expr)

    def test_reads_a_single_expression(self):
        expr = self.lexer.parse('()()')
        self.assertEqual(['(', ')'], expr)

    def test_nested(self):
        expr = self.lexer.parse('(())')
        self.assertEqual(['(', ['(', ')'], ')'], expr)

    def test_chained_nested(self):
        expr = self.lexer.parse('(()())')
        self.assertEqual(['(', ['(', ')'], ['(', ')'], ')'], expr)

    def test_complex(self):
        expr = self.lexer.parse('(((()())())()(()(())(()()()()())))')
        self.assertEqual(
            ['(',
                ['(',
                    ['(',
                        ['(', ')'],
                        ['(', ')'],
                    ')'],
                    ['(', ')'],
                ')'],
                ['(', ')'],
                ['(',
                    ['(', ')'],
                    ['(',
                        ['(', ')'],
                    ')'],
                    ['(',
                        ['(', ')'],
                        ['(', ')'],
                        ['(', ')'],
                        ['(', ')'],
                        ['(', ')'],
                    ')'],
                ')'],
            ')'], expr)


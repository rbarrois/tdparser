#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2010-2012 Raphaël Barrois

"""Tests for token-related code."""


import unittest

import tdparser


class ParserTestCase(unittest.TestCase):
    def test_tokens_required(self):
        self.assertRaises(ValueError, tdparser.Parser, [])

    def test_advance_no_expect(self):
        l = tdparser.LeftParen('(')
        r = tdparser.RightParen(')')
        parser = tdparser.Parser([l, r])
        next_token = parser.advance()
        self.assertEqual(r, next_token)

    def test_advance_expect_success(self):
        l = tdparser.LeftParen('(')
        r = tdparser.RightParen(')')
        parser = tdparser.Parser([l, r])
        next_token = parser.advance(tdparser.LeftParen)
        self.assertEqual(r, next_token)

    def test_advance_expect_fail(self):
        l = tdparser.LeftParen('(')
        r = tdparser.RightParen(')')
        parser = tdparser.Parser([l, r])
        self.assertRaises(tdparser.ParserSyntaxError,
            parser.advance, tdparser.RightParen)

    def test_expression_obeys_rbp(self):
        class AToken(tdparser.Token):
            def nud(self, context):
                return 42

        class BToken(tdparser.Token):
            lbp = 20

            def led(self, left, context):
                return 13 * left

        class CToken(tdparser.Token):
            lbp = 10

        # BToken has a left binding power of 20, CToken of 10.
        # This means that BToken has a 20-strong will to get an expression
        # when it's on the left of something.
        # CToken is only 10-strong on that aspect.
        #
        # We'll pretend to be filling an argument for a token with a 15-strong
        # will to retrieve a right expression.

        # We'll be computing "X (42 * 13) + ..." with X being the previous token
        # with a 15 rbp, 42 being A, 13 being B and + being C.

        a = AToken()
        b = BToken()
        c = CToken()

        p = tdparser.Parser([a, b, c])
        res = p.expression(15)
        self.assertEqual(42 * 13, res)
        self.assertEqual(c, p.current_token)

    def test_trivial_expression(self):
        class AToken(tdparser.Token):
            def nud(self, context):
                return 1

        a = AToken()
        b = tdparser.EndToken()

        p = tdparser.Parser([a, b])
        res = p.parse()
        self.assertEqual(1, res)
        self.assertEqual(b, p.current_token)

    def test_trivial_parenthesized_expression(self):
        class AToken(tdparser.Token):
            def nud(self, context):
                return 1

        l = tdparser.LeftParen('(')
        a = AToken()
        r = tdparser.RightParen(')')
        b = tdparser.EndToken()

        p = tdparser.Parser([l, a, r, b])
        res = p.parse()
        self.assertEqual(1, res)
        self.assertEqual(b, p.current_token)

    def test_iterable_tokens(self):
        class AToken(tdparser.Token):
            def nud(self, context):
                return 1

        # Incomplete list of tokens, to make sure the parser reads them while
        # running
        tokens = [
            tdparser.LeftParen('('),
        ]

        def yield_tokens():
            # A generator, to enforce the minimal generator behaviour.
            for t in tokens:
                yield t

        p = tdparser.Parser(yield_tokens())
        # Add extra tokens now
        end = tdparser.EndToken()
        tokens.append(AToken())
        tokens.append(tdparser.RightParen(')'))
        tokens.append(end)

        # Parse. The newly added token are properly parsed
        res = p.parse()
        self.assertEqual(1, res)
        self.assertEqual(end, p.current_token)

    def test_misparenthsized_expression(self):
        p = tdparser.Parser([tdparser.LeftParen(), tdparser.EndToken()])
        self.assertRaises(tdparser.ParserSyntaxError, p.parse)

    def test_nested_parenthesized_expression(self):
        class TimesToken(tdparser.Token):
            lbp = 10
            def led(self, left, context):
                return left * context.expression(10)

        class PlusToken(tdparser.Token):
            lbp = 5
            def led(self, left, context):
                return left + context.expression(5)

        class NumToken(tdparser.Token):
            def __init__(self, text):
                super(NumToken, self).__init__(text)
                self.value = int(text)

            def nud(self, context):
                return self.value

        e = [
            tdparser.LeftParen(),
            NumToken('4'),
            PlusToken(),
            tdparser.LeftParen(),
            NumToken('1'),
            PlusToken(),
            NumToken('2'),
            TimesToken(),
            NumToken('3'),
            TimesToken(),
            tdparser.LeftParen(),
            NumToken('4'),
            PlusToken(),
            NumToken('5'),
            tdparser.RightParen(),
            PlusToken(),
            NumToken('6'),
            tdparser.RightParen(),
            tdparser.RightParen(),
            TimesToken(),
            NumToken('7'),
            PlusToken(),
            NumToken('8'),
            tdparser.EndToken(),
        ]

        p = tdparser.Parser(e)
        res = p.parse()
        self.assertEqual(
            (4 + (1 + 2 * 3 * (4 + 5) + 6)) * 7 + 8,
            res)

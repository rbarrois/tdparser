#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Raphaël Barrois

"""Tests for lexer-related code."""

import re
from .compat import unittest

import tdparser


class BaseLexerTestCase(unittest.TestCase):
    """Tests base functions of the Lexer class."""

    def test_default_tokens(self):
        lexer = tdparser.Lexer()
        self.assertEqual(2, len(lexer.tokens))
        self.assertEqual([tdparser.LeftParen, tdparser.RightParen],
            [token_class for token_class, _token_re in lexer.tokens])

    def test_no_default_tokens(self):
        lexer = tdparser.Lexer(default_tokens=False)
        self.assertEqual(0, len(lexer.tokens))

    def test_add_token(self):
        class AToken(tdparser.Token):
            pass

        class BToken(tdparser.Token):
            pass

        lexer = tdparser.Lexer(default_tokens=False)
        self.assertEqual(0, len(lexer.tokens))

        a_re = re.compile(r'a+')
        b_re = re.compile(r'b+')

        lexer.register_token(AToken, a_re)
        self.assertEqual(1, len(lexer.tokens))
        self.assertEqual([(AToken, a_re)], lexer.tokens)

        lexer.register_token(BToken, b_re)
        self.assertEqual(2, len(lexer.tokens))
        self.assertEqual((BToken, b_re), lexer.tokens[1])

    def test_dual_registration(self):
        class AToken(tdparser.Token):
            pass

        lexer = tdparser.Lexer(default_tokens=False)
        self.assertEqual(0, len(lexer.tokens))

        a_re = re.compile(r'a+')
        b_re = re.compile(r'b+')

        lexer.register_token(AToken, a_re)
        self.assertEqual(1, len(lexer.tokens))
        self.assertEqual([(AToken, a_re)], lexer.tokens)

        lexer.register_token(AToken, b_re)
        self.assertEqual(2, len(lexer.tokens))
        self.assertEqual((AToken, b_re), lexer.tokens[1])

    def test_get_token_no_text(self):
        lexer = tdparser.Lexer()
        token_class, re_match = lexer._get_token('')
        self.assertIsNone(token_class)
        self.assertIsNone(re_match)

    def test_get_token_no_text_no_tokens(self):
        lexer = tdparser.Lexer(default_tokens=False)
        token_class, re_match = lexer._get_token('')
        self.assertIsNone(token_class)
        self.assertIsNone(re_match)

    def test_get_token_unmatched(self):
        lexer = tdparser.Lexer()
        token_class, re_match = lexer._get_token('aaa')
        self.assertIsNone(token_class)
        self.assertIsNone(re_match)

    def test_get_token_no_tokens(self):
        lexer = tdparser.Lexer(default_tokens=False)
        token_class, re_match = lexer._get_token('aaa')
        self.assertIsNone(token_class)
        self.assertIsNone(re_match)

    def test_get_token(self):
        lexer = tdparser.Lexer()
        token_class, re_match = lexer._get_token('(((')
        self.assertEqual(tdparser.LeftParen, token_class)
        self.assertIsNotNone(re_match)

    def test_get_token_picks_first(self):
        lexer = tdparser.Lexer()
        token_class, re_match = lexer._get_token('aa(((')
        self.assertIsNone(token_class)
        self.assertIsNone(re_match)

    def test_get_token_scans_all_possible_tokens(self):
        lexer = tdparser.Lexer()
        token_class, re_match = lexer._get_token(')(')
        self.assertEqual(tdparser.RightParen, token_class)
        self.assertIsNotNone(re_match)

    def test_lex_empty(self):
        lexer = tdparser.Lexer()
        tokens = list(lexer.lex(''))
        self.assertEqual(1, len(tokens))
        self.assertEqual(tdparser.EndToken, tokens[0].__class__)

    def test_lex_tokens(self):
        text = '((((((()()()))))))((((((('
        lexer = tdparser.Lexer()
        tokens = list(lexer.lex(text))
        self.assertEqual(1 + len(text), len(tokens))
        for i, token in enumerate(tokens[:-1]):
            self.assertEqual(text[i], token.text)
            if token.text == '(':
                self.assertEqual(tdparser.LeftParen, token.__class__)
            else:
                self.assertEqual(tdparser.RightParen, token.__class__)
        self.assertEqual(tdparser.EndToken, tokens[-1].__class__)

    def test_lex_skips_blank(self):
        lexer = tdparser.Lexer()
        tokens = list(lexer.lex('  ('))
        self.assertEqual(2, len(tokens))
        self.assertEqual('(', tokens[0].text)
        self.assertEqual(tdparser.LeftParen, tokens[0].__class__)
        self.assertEqual(tdparser.EndToken, tokens[-1].__class__)

    def test_lex_custom_blank_chars(self):
        lexer = tdparser.Lexer(blank_chars=('a', ' '))
        tokens = list(lexer.lex(' a('))
        self.assertEqual(2, len(tokens))
        self.assertEqual('(', tokens[0].text)
        self.assertEqual(tdparser.LeftParen, tokens[0].__class__)
        self.assertEqual(tdparser.EndToken, tokens[-1].__class__)

    def test_lex_invalid_char(self):
        lexer = tdparser.Lexer(default_tokens=False)
        with self.assertRaises(ValueError):
            list(lexer.lex('foo'))

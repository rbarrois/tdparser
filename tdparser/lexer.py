# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Raphaël Barrois


from __future__ import unicode_literals

import re

from .topdown import Parser, LeftParen, RightParen, EndToken


class TokenRegistry(object):
    """Holds a bunch of token rules.

    Attributes:
        _tokens ((Token, re) list): the registered tokens.
    """

    def __init__(self):
        self._tokens = []

    def register(self, token, regexp):
        """Register a token.

        Args:
            token (Token): the token class to register
            regexp (str): the regexp for that token
        """
        self._tokens.append((token, re.compile(regexp)))

    def matching_tokens(self, text, start=0):
        """Retrieve all token definitions matching the beginning of a text.

        Args:
            text (str): the text to test
            start (int): the position where matches should be searched in the
                string (see re.match(rx, txt, pos))

        Yields:
            (token_class, re.Match): all token class whose regexp matches the
                text, and the related re.Match object.
        """
        for token_class, regexp in self._tokens:
            match = regexp.match(text, pos=start)
            if match:
                yield token_class, match

    def get_token(self, text, start=0):
        """Retrieve the next token from some text.

        Args:
            text (str): the text from which tokens should be extracted

        Returns:
            (token_kind, token_text): the token kind and its content.
        """
        best_class = best_match = None

        for token_class, match in self.matching_tokens(text):
            if best_match and best_match.end() >= match.end():
                continue
            best_match = match
            best_class = token_class

        return best_class, best_match

    def __len__(self):
        return len(self._tokens)


class Lexer(object):
    """The core lexer.

    From its list of tokens (provided through the TOKENS class attribute or
    overridden in the _tokens method), it will parse the given text, with the
    following rules:
    - For each (token, regexp) pair, try to match the regexp at the beginning
      of the text
    - If this matches, add token_class(match) to the list of tokens and continue
    - Otherwise, if the first character is either ' ' or '\t', skip it
    - Otherwise, raise a ValueError.

    Attributes:
        tokens (Token, re) list: The known tokens, as a (token class, regexp) list.
    """

    def __init__(self, with_parens=False, blank_chars=(' ', '\t'), end_token=EndToken,
        *args, **kwargs):
        self.tokens = TokenRegistry()
        self.blank_chars = set(blank_chars)
        self.end_token = end_token

        if with_parens:
            self.register_token(LeftParen, re.compile(r'\('))
            self.register_token(RightParen, re.compile(r'\)'))

        super(Lexer, self).__init__(*args, **kwargs)

    def register_token(self, token_class, regexp=None):
        """Register a token class.

        Args:
            token_class (tdparser.Token): the token class to register
            regexp (optional str): the regexp for elements of that token.
                Defaults to the `regexp` attribute of the token class.
        """
        if regexp is None:
            regexp = token_class.regexp

        self.tokens.register(token_class, regexp)

    def register_tokens(self, *token_classes):
        """Helper for registering a set of token classes.

        Each token class should have a `regexp` attribute.
        """
        for token_class in token_classes:
            self.register_token(token_class)

    def lex(self, text):
        """Split self.text into a list of tokens.

        Args:
            text (str): text to parse

        Yields:
            Token: the tokens generated from the given text.
        """
        while text:
            token_class, match = self.tokens.get_token(text)
            if token_class is not None:
                matched_text = text[match.start():match.end()]
                yield token_class(matched_text)
                text = text[match.end():]
            elif text[0] in self.blank_chars:
                text = text[1:]
            else:
                raise ValueError('Invalid character %s in %s' % (text[0], text))

        yield self.end_token()

    def parse(self, text):
        """Parse self.text.

        Args:
            text (str): the text to lex

        Returns:
            object: a node representing the current rule.
        """
        tokens = self.lex(text)
        parser = Parser(tokens)
        return parser.parse()

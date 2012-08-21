# coding: utf-8
# Copyright (c) 2010-2012 Raphaël Barrois

"""Basic implementation of top-down operator precedence.

In order to use it for parsing:
- Define tokens derivating from the Token class
- Subclass the Lexer class and replace or extend its TOKENS attribute
- Call MyLexer(my_text).parse()
"""

from __future__ import unicode_literals

import re


class ParserError(Exception):
    pass


class ParserSyntaxError(ParserError):
    pass


class Token(object):
    """Base class for tokens.

    Ref:
        http://effbot.org/zone/simple-top-down-parsing.htm
        http://javascript.crockford.com/tdop/tdop.html
    """

    # Left binding power
    # Controls how much this token binds to a token on its right
    lbp = 0

    def __init__(self, text=''):
        self.text = text

    def __repr__(self):
        return "<%s: %r>" % (self.__class__.__name__, self.text)

    def nud(self):  # pragma: no cover
        """Null denotation.

        Describes what happens to this token when located at the beginning of
        an expression.

        Returns:
            _ConditionNode: the node representing this token
        """
        raise NotImplementedError()

    def led(self, left, context):  # pragma: no cover
        """Left denotation.

        Describe what happens to this token when appearing inside a construct
        (at the left of the rest of the construct).

        Args:
            context (_Parser): the parser from which 'next' data can be
                retrieved
            left (_ConditionNode): the representation of the construct on the
                left of this token

        Returns:
            _ConditionNode built from this token, what is on its right, and
                what was on its left.
        """
        raise NotImplementedError()


class LeftParen(Token):
    def nud(self, context):
        expr = context.expression()
        context.advance(expect_class=RightParen)
        return expr

    def __repr__(self):  # pragma: no cover
        return '<(>'


class RightParen(Token):
    def __repr__(self):  # pragma: no cover
        return '<)>'


class EndToken(Token):
    """Marks the end of the input."""
    lbp = 0

    def __repr__(self):
        return '<End>'


class Parser(object):
    """Converts lexed tokens into their representation.

    Attributes:
        tokens (iterable of Token): the tokens.
        current_token (Token): the current token
    """

    def __init__(self, tokens):
        self.tokens = iter(tokens)
        try:
            self.current_token = next(self.tokens)
        except StopIteration:
            raise ValueError("No tokens provided.")

    def advance(self, expect_class=None):
        """Retrieve the next token.

        If an expected class is provided, it will assert that the next token
        matches that class (is an instance).

        Returns:
            Token: the new current token.
        """
        if expect_class and not isinstance(self.current_token, expect_class):
            raise ParserSyntaxError("Unexpected token: got %r, expected %s" % (
                self.current_token, expect_class.__name__))

        try:
            self.current_token = next(self.tokens)
        except StopIteration:
            raise ParserSyntaxError("Unexpected end of token stream.")
        return self.current_token

    def expression(self, rbp=0):
        """Extract an expression from the flow of tokens.

        Args:
            rbp (int): the "right binding power" of the previous token.
                This represents the (right) precedence of the previous token,
                and will be compared to the (left) precedence of next tokens.

        Returns:
            Whatever the led/nud functions of tokens returned.
        """
        prev_token = self.current_token
        self.advance()

        # Retrieve the value from the previous token situated at the
        # leftmost point in the expression
        left = prev_token.nud(context=self)

        while rbp < self.current_token.lbp:
            # Read incoming tokens with a higher 'left binding power'.
            # Those are tokens that prefer binding to the left of an expression
            # than to the right of an expression.
            prev_token = self.current_token
            self.advance()
            left = prev_token.led(left, context=self)

        return left

    def parse(self):
        """Parse the flow of tokens, and return their evaluation."""
        return self.expression()


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

    Class attributes:
        TOKENS (list of (Token, regexp)): the list of tokens to try, in order.

    Attributes:
        text (str): the text to lex and parse.
    """

    TOKENS = (
        (LeftParen, re.compile(r'\(')),
        (RightParen, re.compile(r'\)')),
    )

    def __init__(self, text, *args, **kwargs):
        self.text = text
        super(Lexer, self).__init__(*args, **kwargs)

    def _tokens(self):
        """Expansion point to retrieve a list of valid tokens."""
        return self.TOKENS

    def _get_token(self, text):
        """Retrieve the next token from some text.

        Args:
            text (str): the text from which tokens should be extracted

        Returns:
            (token_kind, token_text): the token kind and its content.
        """
        for (kind, regexp) in self._tokens():
            match = regexp.match(text)
            if match:
                return kind, match
        return None, None

    def lex(self):
        """Split self.text into a list of tokens.

        Returns:
            list of (str, str): the list of (token kind, token text) generated
                from self.text.
        """
        text = self.text

        tokens = []

        while text:
            token_class, match = self._get_token(text)
            if token_class:
                matched_text = text[match.start():match.end()]
                tokens.append((token_class(matched_text)))
                text = text[match.end():]
            elif text[0] in (' ', '\t'):
                text = text[1:]
            else:
                raise ValueError('Invalid character %s in %s' % (text[0], text))

        tokens.append(EndToken())
        return tokens

    def parse(self):
        """Parse self.text.

        Returns:
            object: a node representing the current rule.
        """
        parser = Parser(self.lex())
        return parser.parse()

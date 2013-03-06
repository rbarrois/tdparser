Reference
=========

.. module:: tdparser

This document describes all components of the tdparser package:

- :class:`~tdparser.Token`
- :class:`~tdparser.Parser`
- :class:`~tdparser.Lexer`


Exception classes
-----------------

.. exception:: Error

    This exception is the base class for all tdparser-related exceptions.


.. exception:: ParserError(Error)

    This exception will be raised whenever an unexpected token is encountered in
    the flow of tokens.


.. exception:: MissingTokensError(ParserError)

    This exception is raised when the parsing logic would expect more tokens than
    are available

.. exception:: InvalidTokenError(ParserError)

    This exception is raised when an unexpected token is encountered while
    parsing the data flow.


Defining tokens
---------------


A token must inherit from the :class:`Token` class, and override a few elements depending on its role.


.. class:: Token

    The base class for all tokens.

    .. attribute:: regexp

        Class attribute.

        Optional regular expression (see :mod:`re`) describing text that should be
        lexed into this token class.

        :type: str


    .. attribute:: lbp

        Class attribute.

        "Left binding power". This integer describes the precedence of the
        token when it stands at the left of an expression.

        Tokens with a higher binding power will absorb the next tokens in priority:

        In ``1 + 2 * 3 + 4``, if ``+`` has a lbp of 10 and ``*`` of 20, the ``2 * 3`` part
        will be computed and its result passed as a right expression to the first ``+``.

        :type: int


    .. attribute:: text

        The text that matched :attr:`regexp`.

        :type: str


    .. method:: nud(self, context)

        Compute the "Null denotation" of this token.

        This method should only be overridden for tokens that may appear at the beginning
        of an expression.

        For instance, a number, a variable name, the "-" sign when denoting
        "the opposite of the next expression".

        The :obj:`context` argument is the :class:`Parser` currently running.
        This gives easy access to:

        - The next token in the flow (:attr:`Parser.current_token`)
        - The position in the flow of tokens (:attr:`Parser.current_pos`)
        - Retrieving the next sub-expression from the parser (:meth:`Parser.expression`)

        :param tdparser.Parser context: The active :class:`Parser`
        :return: The value this token evaluates to

    .. method:: led(self, left, context)

        Compute the "Left denotation" of this token.

        This method is called whenever a token appears to the right of another token
        within an expression — typically infix or postfix operators.

        It receives two arguments:

        - :obj:`left` is the value of the previous token or expression in the flow
        - :obj:`context` is the active :class:`Parser` instance, providing calls to
          :meth:`Parser.expression` to fetch the next expression.

        :param left: Whaterver the previous expression evaluated to
        :param tdparser.Parser context: The active :class:`Parser`
        :return: The value this token evaluates to


.. class:: LeftParen(Token)

    A simple :class:`Token` subclass matching an opening bracket, ``(``.

    When parsed, this will token will fetch the next subexpression, assert that
    this expression is followed by a :class:`RightParen` token, and return the value
    of the fetched expression.

    .. attribute:: match


        The token class to expect at the end of the subexpression.
        This simplifies writing similar "bracket" tokens with different opening/closing
        signs.

        :type: :class:`Token`


.. class:: RightParen(Token)

    A simple, passive :class:`Token` (returns no value).

    Used by the :class:`LeftParen` token to check that the sub-expression was properly
    enclosed in left/right brackets.


.. class:: EndToken(Token)

    This specific :class:`Token` marks the end of the input stream.


Parsing a flow of tokens
------------------------

The actual parsing occurs in the :class:`Parser` class, which takes a flow of :class:`Token`.

Parsing is performed through the :meth:`~Parser.parse` method, which will return the next
parsed expression.


.. class:: Parser

    Handles parsing of a flow of tokens. Maintains a pointer to the current :class:`Token`.

    .. attribute:: current_pos

        Stores the current position within the token flow. Starts at 0.

        :type: int


    .. attribute:: current_token

        The next :class:`Token` to parse. When calling a token's :meth:`~Token.nud` or :meth:`~Token.led`,
        this attribute points to the *next* token, not the token whose method has been
        called.

        :type: :class:`Token`


    .. attribute:: tokens

        Iterable of tokens to parse. Can be any kind of iterable — will only be
        walked once.

        :type: iterable of :class:`Token`


    .. function:: consume(self, expect_class=None)

        Consume the active :attr:`current_token`, and advance to the next token.

        If the :obj:`expect_class` is provided, this will ensure that the :attr:`current_token`
        matches that token class, and raise a :exc:`InvalidTokenError` otherwise.

        :param tdparser.Token expect_class: Optionnal :class:`Token` subclass that the
                                            :attr:`current_token` should be an instance of
        :returns: the :attr:`current_token` at the time of calling.


    .. function:: expression(self, rbp=0)

        Retrieve the next expression from the flow of tokens.

        The :obj:`rbp` argument describes the "right binding power" of the calling token.
        This means that the parsing of the expression will stop at the first token whose
        left binding power is lower than this right binding power.

        This obscure definition describes the right precedence of a token. In other
        words, it means "fetch an expression, and stop whenever you meet an operator
        with a lower precedence".

        .. rubric:: Example

        In the ``1 + 2 * 3 ** 4 + 5``, the :meth:`~Token.led` method of the ``*`` token
        will call ``context.expression(20)``. This call will absorb the ``3 ** 4``
        part as a single expression, and stop when meeting the ``+``, whose
        left binding power, 10, is lower than 20.

        :param int rbp: The (optional) right binding power to use when fetching the
                        next subexpression.


    .. function:: parse(self)

        Compute the first expression from the flow of tokens.


Generating tokens from a string
-------------------------------

The :class:`Parser` class works on an iterable of :class:`tokens <Token>`.

In order to retrieve those tokens, the simplest way is to use the :class:`Lexer` class.

.. class:: Lexer

    This class handles converting a string into an iterable of :class:`tokens <Token>`.

    Once initialized, a :class:`Lexer` must be passed a set of tokens to handle.

    The lexer parses strings according to the following algorithm:

    - Try each regexp in order for a match at the start of the string
    - If none match:

      - If the first character is a blank (see :attr:`blank_chars`), remove it from the
        beginning of the string and go back to step 1
      - Otherwise, raise a :exc:`ValueError`.
    - If more than one regexp match, keep the one with the longest match.
    - Among those with the same, longest, match, keep the first registered one
    - Instantiate the :class:`Token` associated with that best regexp,
      passing its constructor the substring that was matched by the regexp
    - Yield that :class:`Token` instance
    - Strip the matched substring from the text, and go back to step 1.


    .. note:: The :class:`Lexer` can be used as a standalone parser: the tokens
              passed to :meth:`Lexer.register_token` are simply instantiated with
              the matching text as first argument.


    .. attribute:: tokens

        A :class:`~lexer.TokenRegistry` holding the set of known tokens.

        :type: :class:`~lexer.TokenRegistry`


    .. attribute:: blank_chars

        An iterable of chars that should be considered as "blank" and thus not parsed into
        a :class:`Token`.

        :type: iterable of :obj:`str`


    .. attribute:: end_token

        The :class:`Token` subclass to use to mark the end of the flow

        :type: :class:`EndToken`


    .. method:: register_token(self, token_class[, regexp=None])

        Registers a token class in the lexer (actually, in the :class:`~lexer.TokenRegistry`
        at :attr:`tokens`).

        There are two methods to provide the regular expression for token extraction:

        - In the :obj:`regepx` parameter to :meth:`register_token`
        - If that parameter isn't provided, the :class:`Lexer` will look for a
          :attr:`~Token.regexp` string attribute on the provided :obj:`token_class`.

        :param tdparser.Token token_class: The :class:`Token` subclass to add to the list of available
                            tokens

        :param str regexp: The regular expression to use when extracting tokens from
                           some text; if empty, the :attr:`~Token.regexp` attribute of
                           the :obj:`token_class` will be used instead.


    .. method:: register_tokens(self, token_class[, token_class[, ...]])

        Register a batch of :class:`Token` subclasses.
        This is equivalent to calling ``lexer.register_token(token_class)`` for
        each passed :obj:`token_class`.

        The regular expression associated to each token *must* be set on its
        :attr:`~Token.regexp` attribute; no overrides are available with this method.

        :param tdparser.Token token_class: token classes to register


    .. method:: lex(self, text)

        Read a text, and lex it, yielding :class:`Token` instances.

        This will walk the text, eating chunks that can be paired to a :class:`Token`
        through its associated regular expression.

        It will yield :class:`Token` instances while parsing the text,
        and end with an instance of the :class:`EndToken` class as set in the
        :class:`lexer <Lexer>`'s :attr:`end_token` attribute.

        :param str text: The text to lex
        :return: Iterable of :class:`Token` instances


    .. method:: parse(self, text)

        Shortcut method for lexing and parsing a text.

        Will :meth:`lex` the text, then instantiate a :class:`Parser` with the
        resulting :class:`Token` flow and call its :meth:`~Parser.parse` method.

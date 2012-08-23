Reference
=========

.. module:: tdparser

This document describes all components of the tdparser package:

- :class:`~tdparser.Token`
- :class:`~tdparser.Parser`
- :class:`~tdparser.Lexer`


Exception classes
-----------------

.. exception:: ParserError

    This exception is the base class for all tdparser-related exceptions.


.. exception:: ParserSyntaxError

    This exception will be raised whenever an unexpected token is encountered in
    the flow of tokens.


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


    .. method:: led(self, left, context)

        Compute the "Left denotation" of this token.

        This method is called whenever a token appears to the right of another token
        within an expression — typically infix or postfix operators.

        It receives two arguments:

        - :obj:`left` is the value of the previous token or expression in the flow
        - :obj:`context` is the active :class:`Parser` instance, providing calls to
          :meth:`Parser.expression` to fetch the next expression.


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
        matches that token class, and raise a :exc:`ParserSyntaxError` otherwise.

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


    .. function:: parse(self)

        Compute the first expression from the flow of tokens.

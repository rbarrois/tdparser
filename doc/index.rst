.. TDParser documentation master file, created by
   sphinx-quickstart on Fri Aug 17 15:43:26 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

TDParser: a simple parsing library in Python
============================================

Getting started
---------------

Installation
~~~~~~~~~~~~

First, you'll need to get the latest version of TDParser.

TDParser is compatible with all Python versions from 2.6 to 3.2.

The simplest way is to get it from `PyPI <http://pypi.python.org/>`_::

    $ pip install tdparser

You may also fetch the latest development version from https://github.com/rbarrois/tdparser::

    $ git clone git://github.com/rbarrois/tdparser.git
    $ cd parser
    $ python setup.py install


Defining the tokens
~~~~~~~~~~~~~~~~~~~

TDParser provides a simple framework for building parsers; thus, it doesn't provide
default token kinds.

Defining a token type requires 4 elements:

- Input for the token: TDParser uses a regexp, in the :attr:`tdparser.Token.regexp` attribute
- Precedence, an integer stored in the :attr:`tdparser.Token.lbp` attribute
- Value that the token should get when it appears at the beginning of a standalone expression;
  this behavior is defined in the :meth:`tdparser.Token.nud` method
- Behavior of the token when it appears between two expressions;
  this is defined in the :meth:`tdparser.Token.led` method.


An example definition of a simple arithmetic parser that returns the expression's value would be::

    from tdparser import Token

    class Integer(Token):
        regexp = r'\d+'
        def nud(self, context):
            return int(self.text)

    class Addition(Token):
        regexp = r'\+'
        lbp = 10

        def led(self, left, context):
            return left + context.expression(self.lbp)

    class Multiplication(Token):
        regexp = r'\*'
        lbp = 20

        def led(self, left, context):
            return left * context.expression(self.lbp)

Building the Lexer/Parser
~~~~~~~~~~~~~~~~~~~~~~~~~

The parser has a simple interface: it takes as input an iterable of :class:`tdparser.Token`,
and returns the expression that the tokens' :meth:`~tdparser.Token.nud` and :meth:`~tdparser.Token.led`
methods return.

The lexer simply needs to get a list of valid tokens::

    lexer = tdparser.Lexer(with_parens=True)
    lexer.register_tokens(Integer, Addition, Multiplication)

The ``with_parens=True`` options adds a pair of builtin tokens, :class:`tdparser.LeftParen` and
:class:`tdparser.RightParen`, which provide left/right parenthesis behavior.

.. note:: The default lexer will skip space and tabulations. This can be modified by
          settings the :attr:`~tdparser.Lexer.blank_chars` argument when initializing the
          lexer.

We now only need to feed our text to the lexer::

    >>> lexer.parse('1 + 1')
    2
    >>> lexer.parse('2 * 3 + 4')
    10

Contents
--------

.. toctree::
   :maxdepth: 2

   reference
   internals
   changelog

Links
-----

TDParser resources
~~~~~~~~~~~~~~~~~~

- Project home page on GitHub: https://github.com/rbarrois/tdparser
- Documentation hosted on ReadTheDocs: http://tdparser.readthedocs.org/
- Continuous integration on Travis-CI: http://travis-ci.org/rbarrois/tdparser

External references
~~~~~~~~~~~~~~~~~~~

A few articles on Top-Down parsing (the algorithm used by tdparser):

- http://effbot.org/zone/simple-top-down-parsing.htm : A simple implementation in Python
- http://javascript.crockford.com/tdop/tdop.html : A full tutorial in JS
- http://dl.acm.org/citation.cfm?id=512931 : Original description of the algorithm

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


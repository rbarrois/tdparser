tdparser
========


This library aims to provide an efficient way to write simple lexer/parsers in Python, using the
`Top-Down parsing algorithm <http://dl.acm.org/citation.cfm?id=512931>`_.

Code is maintained on `GitHub <http://github.com/rbarrois/tdparser>`_, documentation is available on `ReadTheDocs <http://tdparser.readthedocs.org/>`_.

Other python libraries provide parsing/lexing tools (see http://nedbatchelder.com/text/python-parsers.html for a few examples); distinctive features of tdparser are:

- Avoid docstring-based grammar definitions
- Provide a generic parser structure, able to handle any grammar
- Don't generate code
- Let the user decide the nature of parsing results: abstract syntax tree, final expression, ...


Example
=======

Here is the definition for a simple arithmetic parser::

    import re

    from tdparser import Lexer, Token

    class Integer(Token):
        def __init__(self, text):
            self.value = int(text)

        def nud(self, context):
            """What the token evaluates to"""
            return self.value

    class Addition(Token):
        lbp = 10  # Precedence

        def led(self, left, context):
            """Compute the value of this token when between two expressions."""
            # Fetch the expression to the right, stoping at the next boundary
            # of same precedence
            right_side = context.expression(self.lbp)
            return left + right_side

    class Substraction(Token):
        lbp = 10  # Same precedence as addition

        def led(self, left, context):
            return left - context.expression(self.lbp)

        def nud(self, context):
            """When a '-' is present on the left of an expression."""
            # This means that we are returning the opposite of the next expression
            return - context.expression(self.lbp)

    class Multiplication(Token):
        lbp = 20  # Higher precedence than addition/substraction

        def led(self, left, context):
            return left * context.expression(self.lbp)


    lexer = Lexer(with_parens=True)
    lexer.register_token(Integer, re.compile(r'\d+'))
    lexer.register_token(Addition, re.compile(r'\+'))
    lexer.register_token(Substraction, re.compile(r'-'))
    lexer.register_token(Multiplication, re.compile(r'\*'))

    def parse(text):
        return lexer.parse(text)

Using it returns the expected value::

    >>> parse("1+1")
    2
    >>> parse("1 + -2 * 3")
    -5

Adding new tokens is straightforward::

    class Division(Token):
        lbp = 20  # Same precedence as Multiplication

        def led(self, left, context):
            return left // context.expression(self.lbp)

    lexer.register_token(Division, re.compile(r'/'))

And using it::

    >>> parse("3 + 12 / 3")
    7

Let's add the exponentiation operator::

    class Power(Token):
        lbp = 30  # Higher than mult

        def led(self, left, context):
            # We pick expressions with a lower precedence, so that
            # 2 ** 3 ** 2 computes as 2 ** (3 ** 2)
            return left ** context.expression(self.lbp - 1)

    lexer.register_token(Power, re.compile(r'\*\*'))

And use it::

    >>> parse("2 ** 3 ** 2")
    512

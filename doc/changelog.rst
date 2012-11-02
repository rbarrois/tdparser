ChangeLog
=========

1.2.0 (planned)
---------------

*New:*

    - Batteries included (provide ready-to-use tokens for arithmetic evaluation, AST building, ...)
    - Add documentation for the top-down algorithm

1.1.3 (02/11/2012)
------------------

*Bugfix:*

    - Fix setup.py (:func:`find_packages` was installing tests as well)

1.1.2 (02/11/2012)
------------------

*Bugfix:*

    - Swap doc/changelog.rst and ChangeLog for proper sdist compatibility

1.1.1 (02/11/2012)
------------------

*Bugfix:*

    - Fix documentation packaging (invalid paths in MANIFEST.in)

1.1.0 (24/08/2012)
------------------

*New:*

    - Simpler token registration to the :class:`~tdparser.Lexer`
    - Improved documentation
    - Full test coverage
    - Python3 compatibility

*Bugfix:*

    - Choose token by longest match

1.0.0 (21/08/2012)
------------------

First stable version of tdparser.

Includes:

- Fully functional top-down parser
- Lexer
- Wide set of unit tests

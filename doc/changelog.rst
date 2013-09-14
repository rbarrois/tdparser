ChangeLog
=========

1.2.0 (planned)
---------------

*New:*

    - Batteries included (provide ready-to-use tokens for arithmetic evaluation, AST building, ...)
    - Add documentation for the top-down algorithm


1.1.6 (2013-09-14)
------------------

*Misc:*

    - Switch back to setuptools.

1.1.5 (2013-05-20)
------------------

*Bugfix:*

    - #8: Fix packaging: stop installing the tests/ dir

1.1.4 (2013-03-11)
------------------

    - Fix handling of empty token flows
    - More descriptive errors

1.1.3 (2012-11-02)
------------------

*Bugfix:*

    - Fix setup.py (:func:`find_packages` was installing tests as well)

1.1.2 (2012-11-02)
------------------

*Bugfix:*

    - Swap doc/changelog.rst and ChangeLog for proper sdist compatibility

1.1.1 (2012-11-02)
------------------

*Bugfix:*

    - Fix documentation packaging (invalid paths in MANIFEST.in)

1.1.0 (2012-08-24)
------------------

*New:*

    - Simpler token registration to the :class:`~tdparser.Lexer`
    - Improved documentation
    - Full test coverage
    - Python3 compatibility

*Bugfix:*

    - Choose token by longest match

1.0.0 (2012-08-21)
------------------

First stable version of tdparser.

Includes:

- Fully functional top-down parser
- Lexer
- Wide set of unit tests

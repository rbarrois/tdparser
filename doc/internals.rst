TDParser internals
==================

Beyond the :doc:`Reference <reference>` section, here is an in-depth description of
:mod:`tdparser`'s internals.


:class:`~tdparser.Lexer` helpers
--------------------------------


.. module:: tdparser.lexer


This module holds the :class:`tdparser.Lexer` class, which is available in
the top-level :mod:`tdparser` module.


.. class:: TokenRegistry

    This class holds a set of (token, regexp) pairs, and selects the appropriate
    pair to extract data from a string.


    .. note:: The :class:`TokenRegistry` doesn't interact with the :class:`~tdparser.Token`
              subclasses provided through :meth:`register`.

              This means that any kind of value could be provided for this field,
              and will be returned as-is by the :meth:`get_token` method.


    .. attribute:: _tokens

        Holds a list of (:class:`~tdparser.Token`, :class:`re.RegexObject`) tuples.
        These are the tokens in the order they were inserted (insertion order matters).

        :type: list of (:class:`~tdparser.Token` subclass, :class:`re.RegexObject`) tuples


    .. method:: register(self, token, regexp)

        Register a :class:`~tdparser.Token` subclass for the given :obj:`regexp`.

        :param tdparser.Token token: The :class:`~tdparser.Token` subclass to register
        :param str regexp: The regular expression (as a string) associated with the token


    .. method:: matching_tokens(self, text[, start=0])

        Retrieve all tokens matching a given text. The optional :obj:`start` argument
        can be used to alter the start position for the :meth:`~re.RegexObject.match`
        call.

        :param str text: Text for which matching (:class:`~tdparser.Token`, :class:`re.MatchObject`)
                         pairs should be searched

        :param int start: Optional start position with :obj:`text` for the regexp
                          :meth:`~re.RegexObject.match` call

        :return: Yields tuples of (:class:`~tdparser.Token`, :class:`re.MatchObject`) for each
                 token whose regexp matched the :obj:`text`.


    .. method:: get_token(self, text[, start=0])

        Retrieve the best token class and the related :class:`match <re.MatchObject>`
        at the start of the given :obj:`text`.

        The algorithm for choosing the "best" class is:

        - Fetch all matching tokens (through :meth:`matching_tokens`)
        - Select those with the longest match
        - Return the first of those tokens

        A different starting position for :meth:`~re.RegexObject.match` calls can be
        provided in the :obj:`start` parameter.

        :param str text: Text for which the (:class:`~tdparser.Token`, :class:`re.MatchObject`)
                         pair should be returned

        :param int start: Optional start position with :obj:`text` for the regexp
                          :meth:`~re.RegexObject.match` call

        :return: (:class:`~tdparser.Token`, :class:`re.MatchObject`) pair, the best match for the
                 given :obj:`text`.

                 If no token matches the text, returns (:obj:`None`, :obj:`None`).


    .. method:: __len__(self)

        The :meth:`len` of a :class:`TokenRegistry` is the length of its :attr:`_tokens`
        attribute.

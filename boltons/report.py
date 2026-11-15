# Copyright (c) 2013, Mahmoud Hashemi
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * The names of the contributors may not be used to endorse or
#      promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""``report`` is for summarizing the shape of nested data before it
goes somewhere else. JSON documents are the common case: it's useful
to know how many leaves there are, how deeply nested the document is,
and what the leaf paths look like, without writing a one-off recursive
walk every time.

>>> res = flatten_paths({'a': {'b': 1}, 'c': [1, 2]})
>>> res.paths
['a.b', 'c[0]', 'c[1]']
>>> res.max_depth
3
>>> res.leaves
3

"""

from collections import namedtuple


__all__ = ['flatten_paths', 'FlattenReport']


FlattenReport = namedtuple('FlattenReport', ['paths', 'max_depth', 'leaves'])
FlattenReport.__doc__ = """The result of :func:`flatten_paths`.

Attributes:
    paths (list): Leaf paths in document order. Mapping keys are joined
        with ``.`` (``a.b``) and sequence indexes use brackets
        (``c[0]``).
    max_depth (int): Depth of the deepest node, with the top-level
        object counted as depth 1.
    leaves (int): Number of leaves. A leaf is any value which is not a
        non-empty dict, list, or tuple. Empty containers count as
        leaves at their own path.
"""


def flatten_paths(obj):
    """Walk *obj*, a nested structure of dicts, lists, tuples, and
    scalar values, and return a :class:`FlattenReport` describing its
    leaves.

    >>> res = flatten_paths({'users': [{'name': 'alice'}, {'name': 'bob'}]})
    >>> res.paths
    ['users[0].name', 'users[1].name']
    >>> res.max_depth
    4
    >>> res.leaves
    2

    Dict keys are rendered with :func:`str`, so a top-level scalar
    gets the empty path ``''``. Keys containing ``.`` or ``[`` are not
    escaped; paths are meant for display and reporting.

    A :exc:`ValueError` is raised if a container contains itself,
    since such a structure has no finite set of leaves. Repeated
    (non-circular) references to the same container are fine and
    produce one path per occurrence.
    """
    paths = []
    max_depth = 0
    stack = [(obj, '', 1, ())]

    while stack:
        node, path, depth, ancestors = stack.pop()
        max_depth = max(max_depth, depth)

        if isinstance(node, (dict, list, tuple)) and node:
            node_id = id(node)
            if node_id in ancestors:
                raise ValueError('circular reference detected at path %r'
                                 % path)
            ancestors += (node_id,)

            if isinstance(node, dict):
                children = [(value, _join_key(path, key))
                            for key, value in node.items()]
            else:
                children = [(value, '%s[%d]' % (path, index))
                            for index, value in enumerate(node)]
            for child, child_path in reversed(children):
                stack.append((child, child_path, depth + 1, ancestors))
        else:
            paths.append(path)

    return FlattenReport(paths=paths, max_depth=max_depth,
                         leaves=len(paths))


def _join_key(path, key):
    key = str(key)
    if not path:
        return key
    return path + '.' + key

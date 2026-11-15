import pytest

from boltons.report import flatten_paths, FlattenReport


def test_mixed_nesting():
    res = flatten_paths({'a': {'b': 1}, 'c': [1, 2]})
    assert isinstance(res, FlattenReport)
    assert res.paths == ['a.b', 'c[0]', 'c[1]']
    assert res.max_depth == 3
    assert res.leaves == 3


def test_deep_nesting():
    res = flatten_paths({'a': [{'b': [0, 1]}]})
    assert res.paths == ['a[0].b[0]', 'a[0].b[1]']
    assert res.max_depth == 5
    assert res.leaves == 2


def test_empty_containers_are_leaves():
    res = flatten_paths({'a': [], 'b': {}})
    assert res.paths == ['a', 'b']
    assert res.max_depth == 2
    assert res.leaves == 2


def test_scalar_root():
    res = flatten_paths(1)
    assert res.paths == ['']
    assert res.max_depth == 1
    assert res.leaves == 1


def test_tuple_indexes():
    res = flatten_paths(({'a': 1},))
    assert res.paths == ['[0].a']
    assert res.max_depth == 3


def test_shared_container_is_not_a_cycle():
    shared = [1]
    res = flatten_paths([shared, shared])
    assert res.paths == ['[0][0]', '[1][0]']
    assert res.leaves == 2


def test_cycle_raises():
    cyclic = []
    cyclic.append(cyclic)
    with pytest.raises(ValueError):
        flatten_paths(cyclic)

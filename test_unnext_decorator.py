import io

import pytest

from unread_decorator import add_unnext


def my_generator():
    yield 'a'
    yield 'b'
    yield 'c'

@pytest.fixture
def abc_iterators(request):
    """a list of iterators each returning 'a', 'b', 'c' and wrapped with add_unnext."""
    my_iterators = [
        ['a', 'b', 'c'],
        ('a', 'b', 'c'),
        'abc',
        my_generator(),
    ]
    return map(add_unnext, my_iterators)


def test_unnext_1_item(abc_iterators):
    for items in abc_iterators:
        iteration = 0
        for item in items:
            print("item:", item)
            iteration += 1
            if iteration == 2:
                items.unnext(item)
            if iteration == 3:
                assert item == 'b'
            if iteration == 4:
                assert item == 'c'
        assert iteration == 4

def test_unnext_2_items(abc_iterators):
    for items in abc_iterators:
        iteration = 0
        for item in items:
            print("item:", item)
            iteration += 1
            if iteration == 2:
                items.unnext(item)
                items.unnext('new')
            if iteration == 3:
                assert item == 'new'
            if iteration == 4:
                assert item == 'b'
        assert iteration == 5

def test_unnext_before_start(abc_iterators):
    for items in abc_iterators:
        items.unnext('before')
        iteration = 0
        for item in items:
            print("item:", item)
            iteration += 1
            if iteration == 1:
                assert item == 'before'
            if iteration == 2:
                assert item == 'a'
        assert iteration == 4

def test_unnext_into_nested_loop(abc_iterators):
    for items in abc_iterators:
        seq = []
        for item in items:
            seq += [item]
            if item == 'b':
                items.unnext(item)
                for nested in items:
                    seq += [item]
                    if nested == 'b':
                        break
        assert seq == ['a', 'b', 'b', 'c']

def test_unnext_in_nested_loop(abc_iterators):
    for items in abc_iterators:
        seq = []
        for item in items:
            print("outer", item)
            seq += [item]
            if item == 'b':
                for nested in items:
                    print("inner", nested)
                    seq += [nested]
                    if nested == 'c':
                        items.unnext(nested)
                        items.unnext('another')
                        break
        assert seq == ['a', 'b', 'c', 'another', 'c']

def test_unnext_for_readlines():
    f = io.StringIO("a\nb\nc")
    items = add_unnext(f.readlines())

def test_example_from_documentation():
    items = add_unnext([11, 12, 13])
    results = []
    for item in items:
        results.append(item)
        if len(results) == 2:
            items.unnext(item)
            items.unnext(77)
    assert results == [11, 12, 77, 12, 13]

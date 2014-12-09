typecheck-decorator
===================
Lutz Prechelt, 2014

Two Python object decorators.

A Python decorator for file-like objects, `add_unread()`
that adds an operation `unread()` for pushing data back
into the input stream.

A Python decorator for iterables and iterators, `add_unnext()`
that returns an iterator which has an additional operation `unnext()` 
for pushing an item back into the still-to-be-iterated part.

1 Usage of add_unread
=====================

  ```Python
  from unread_decorator import add_unread
  f = add_unread(open(filename, mode, buffering))

  # assume f contains "one\ntwo\nthree"
  f = add_unread(f)  # decorate
  data = f.readline()  # 'one\n'
  data = f.readline()  # 'two\n'
  f.unread(data)
  data = f.readline()  # 'two\n'
  f.unread(data)
  f.unread("more than ")
  print(f.read())  # prints "more than two\nthree"
  ```

`add_unread()` will work correctly with streams obtained by 'open()'
for `mode in ['r', 'rt', 'rb']` and
for `buffering in [-1, 0, 1]`.
It will also work for `io.BytesIO` and `io.StringIO`.
It will also work for any other stream for which `read()`
and (if present) `readline()` work as they do for the above ones.


2 Effect of `add_unread(obj)`
=============================

- Returns the same object `obj`, with some modifications:
- Will add a function `unread(data)` that (re)inserts
  `data` at the very front of the remainder of the input stream.
- You can submit any data you like, as long as its type is that
  of the stream (any sequence, typically bytestings or strings).
- Successive `unread()` calls work in LIFO (stack-like) fashion:
  the most recently `unread()` data will be `read()` first.
- Will modify the function `read()` to act accordingly.
- Will modify the function `readline()` (if that exists)
  to act accordingly.
  The newline symbol is always `b'\n'` for bytestrings and
  `'\n'` for textstrings; `readline()` does not make sense
  for other types of streams.
- Will modify the function `seekable()` (if that exists)
  to return `False` as long as there is unread data in
  the buffer.
- Will modify the function `seek()` (if that exists)
  to raise `OSError` as long as there is unread data in
  the buffer.
- Raises `AttributeError` unless `obj` is a file-like object
  (i.e., has a `read()` operation).
- Unread data is stored in memory (as part of an internal
  dictionary `_unread` that is added to the object).
  Calling `unread()` does not modify the underlying stream at all.
- Successive `unread()` operations will lead to sequence concatenation
  via `+`, so do not unread huge quantities of data in
  small pieces unless you are patient.


3 Usage of add_unnext
=====================

  ```Python
  from unread_decorator import add_unnext

  items = add_unnext([11, 12, 13])
  results = []
  for item in items:
      results.append(item)
      if len(results) == 2:
          items.unnext(item)
          items.unnext(77)
  assert results == [11, 12, 77, 12, 13]
  ```
  
 `add_unnext()` will work correctly with all iterators (such as calls
 to generator functions) as well as
 with all iterables `it` for which `iter(it)` returns a proper iterator
 (such as sequences).
 This is so nearly everything that you will usually not need
 to think about it.


4 Effect of `add_unnext(obj)`
=============================

- Returns an iterator of type `unnext_iterator`.
- If `obj` was an iterator, the result wraps that iterator;
  otherwise the result wraps `iter(obj)`.
- The result has a function `unnext(item)` that (re)inserts
  `item` at the very front of the remainder of the iteration.
- You can submit any item you like.
- Successive `unnext()` calls work in LIFO (stack-like) fashion:
  the most recently `unnext()`ed data will be returned first
  when the iterator resumes.


Version history
===============

- **0.1b**: 2014-12-05.
  Initial version (not released on PyPI) of `add_unread()`.
  Reasonably complete and with automated tests, but not yet used in
  practice.
- **1.0**: 2014-12-09
  Added `add_unnext` and its tests, augmented documentation.


Similar packages
================

As of 2014-11, I found some very elementary implementations in stackoverflow
answers, but no package on PyPI that was found by the search term
"unread" appeared to provide such functionality.
Surprise!


TO DO
=====

- ???
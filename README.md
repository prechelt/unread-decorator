typecheck-decorator
===================
Lutz Prechelt, 2014

A Python decorator for file-like objects, `add_unread()`,
add adds an operation `unread()` for pushing data back
into the input stream.

1 Usage
=======

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


Version history
===============

- **0.1b**: 2014-12-05.
  Initial version (not released on PyPI).
  Reasonably complete and with automated tests, but not yet used in
  practice.


Similar packages
================

As of 2014-11, I found some very elementary implementations in stackoverflow
answers, but no package on PyPI that was found by the search term
"unread" appeared to provide such functionality.
Surprise!


TO DO
=====

- add `unnext()` for iterators?
- apply that to the result of `readlines()`?
- make applicable to classes?
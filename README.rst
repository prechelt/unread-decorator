Two decorators ``add_unread`` and ``add_unnext``
for file-like objects and iterators, respectively.
``add_unread`` introduces a function ``unread()`` for pushing data
obtained by ``read()`` or ``readline()`` back into the input stream.
``add_unnext`` introduces a function ``unnext()`` for pushing an item
back into an iterator (to be returned by the next ``__next__()``)

``add_unread`` will work for all kinds of streams:
memory-based or file-based, binary or text,
buffered or unbuffered.
It will also work with higher level operations
if those are properly built on top of ``read()`` or ``readline()``
and also allows to insert content not previously read, because
the actual stream is never modified (only a pushback buffer added).

::

  import io
  from unread_decorator import add_unread

  f = io.StringIO("one\ntwo\nthree")  # or: f = open("myfile.txt")
  f = add_unread(f)  # decorate
  data = f.readline()  # 'one\n'
  data = f.readline()  # 'two\n'
  f.unread(data)
  data = f.readline()  # 'two\n'
  f.unread(data)
  f.unread("more than ")
  print(f.read())  # prints "more than two\nthree"


``add_unnext`` will work for all kinds of iterators as well as
iterables.
It is useful if you want to forward some part of an interation to
a separate function based on what you encountered.
It also allows to insert content not previously received from the iterator.

::

  from unread_decorator import add_unnext

  items = add_unnext([11, 12, 13])
  results = []
  for item in items:
      results.append(item)
      if len(results) == 2:
          items.unnext(item)
          items.unnext(77)
  assert results == [11, 12, 77, 12, 13]


Find the documentation at
https://github.com/prechelt/unread-decorator

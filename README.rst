A decorator for file-like objects.
The decorator introduces a function ``unread()`` for pushing back data
obtained by ``read()`` or ``readline()`` back into the input stream.

The decorator will work for all kinds of streams:
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



Find the documentation at
https://github.com/prechelt/unread-decorator

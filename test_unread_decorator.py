import io
import os.path

import pytest

from unread_decorator import add_unread


simplestring = "one\ntwo\nthree\n"
unicodestring = "one\ntwü\nthrée\n"
bytestring = b'one\ntwo\nthree\n'

path = "testdata"
simplestringfile = os.path.join(path, "simplestring.txt")
unicodestringfile = os.path.join(path, "unicodestring.txt")
bytestringfile = os.path.join(path, "bytestring.txt")
longbytesfile = os.path.join(path, "longbytes.txt")
longstringfile = os.path.join(path, "longstring.txt")

@pytest.fixture
def threelinefiles(request):
    """a list of read streams with the following properties:
    Each contains exactly three lines, each line at least 3 characters long
    (plus the newline)."""
    files = [
       io.StringIO(simplestring),
       io.StringIO(unicodestring),
       io.BytesIO(bytestring),
       open(simplestringfile, 'rt'),
       open(unicodestringfile, 'rt'),
       open(bytestringfile, 'rb'),
       open(longbytesfile, 'rb'),
       open(longstringfile, 'rt'),
       open(simplestringfile, 'rt', buffering=1),
       open(unicodestringfile, 'rt', buffering=1),
       open(bytestringfile, 'rb', buffering=0),
       open(longbytesfile, 'rb', buffering=0),
       open(longstringfile, 'rt', buffering=1),
    ]
    def close_them():
        for file in files:
            file.close()
    request.addfinalizer(close_them)
    return map(add_unread, files)


def test_unread_1_sequence(threelinefiles):
    for f in threelinefiles:
        print(type(f))
        data1 = f.read(1)
        assert len(data1) == 1
        data2 = f.read(2)
        assert len(data2) == 2
        f.unread(data2)
        data2b = f.read(2)
        assert len(data2b) == 2
        assert data2b == data2

def test_unread_2_sequences(threelinefiles):
    for f in threelinefiles:
        print(type(f))
        data1 = f.read(3)
        data2 = f.read(3)
        f.unread(data2)
        f.unread(data1)
        data3 = f.read(6)
        assert data3 == data1 + data2

def test_unread_then_partial_read(threelinefiles):
    for f in threelinefiles:
        print(type(f))
        data1 = f.read(3)
        data2 = f.read(3)
        f.unread(data2)
        f.unread(data1)
        data3 = f.read(4)
        assert data3 == data1 + data2[0:1]

def test_unread_then_overread(threelinefiles):
    for f in threelinefiles:
        print(type(f))
        data1 = f.read(3)
        f.unread(data1)
        data2 = f.read(4)
        assert data2.startswith(data1)
        assert len(data2) > len(data1)

def test_unread_then_read_all(threelinefiles):
    for f in threelinefiles:
        print(type(f))
        data1 = f.read(3)
        f.unread(data1)
        data2 = f.read(-1)
        assert len(f.read(1)) == 0  # f is indeed exhausted
        assert data2.startswith(data1)
        assert len(data2) > len(data1)  # f was not exhausted before

def test_unread_before_read(threelinefiles):
    with add_unread(io.StringIO(unicodestring)) as f:
        f.unread("Start!")
        data1 = f.read(9)
        assert len(data1) == 9
        assert data1.startswith("Start!")

def test_unread_then_readline(threelinefiles):
    with add_unread(io.StringIO("one\ntwo\nthree\n")) as f:
        f.unread("Start!")
        data1 = f.readline()
        data2 = f.readline()
        assert data1 == "Start!one\n"
        assert data2 == "two\n"

def test_readline_then_unread(threelinefiles):
    for f in threelinefiles:
        print(type(f))
        for i in range(3):
            data1 = f.readline()
            f.unread(data1)
            data1b = f.readline()
            assert data1b == data1

def test_2_readlines_then_2_unreads(threelinefiles):
    for f in threelinefiles:
        print(type(f))
        for i in range(2):
            data1 = f.readline()
            data2 = f.readline()
            f.unread(data2)
            f.unread(data1)
            data1b = f.readline()
            data2b1 = f.read(3)  # mix readline() with read()
            data2b2 = f.readline()
            assert data1b == data1
            assert data2b1+data2b2 == data2

def test_unread_makes_unseekable(threelinefiles):
    for f in threelinefiles:
        print(type(f))
        should_be_seekable = f.seekable()
        #----- test seekable():
        data1 = f.read(9)
        assert f.seekable() == should_be_seekable
        f.unread(data1)
        assert not f.seekable()
        data1b = f.read(10)
        assert f.seekable() == should_be_seekable
        #----- test seek():
        cannot_seek_cur = [io.StringIO,
                           io.TextIOWrapper,
                          ]  # as of Python 3.4
        if should_be_seekable and type(f) not in cannot_seek_cur:
            f.seek(-5, io.SEEK_CUR)
            data2 = f.read(5)
            assert data1b[5:] == data2
            f.unread(data2[3:])
            with pytest.raises(OSError):
                f.seek(-3, io.SEEK_CUR)

def test_refuses_nonfilelike_objects():
    with pytest.raises(AttributeError):
        add_unread(["just a list"])
    with pytest.raises(AttributeError):
        obj = object()
        obj.read = 1  # non-function
        add_unread(obj)
    with pytest.raises(AttributeError):
        add_unread(io.BufferedIOBase)  # class, not object
    with pytest.raises(AttributeError):
        add_unread(io.TextIOWrapper)  # class, not object

def test_unread_example_from_documentation():
    f = io.StringIO("one\ntwo\nthree")
    f = add_unread(f)  # decorate
    data = f.readline()  # 'one\n'
    assert data == 'one\n'
    data = f.readline()  # 'two\n'
    assert data == 'two\n'
    f.unread(data)
    data = f.readline()  # 'two\n'
    assert data == 'two\n'
    f.unread(data)
    f.unread("more than ")
    data = f.read()
    assert data == "more than two\nthree"


#---------- create test data files:

if __name__ == '__main__':
    with open(simplestringfile, 'wt') as f:
        f.write(simplestring)
    with open(unicodestringfile, 'wt') as f:
        f.write(unicodestring)
    with open(bytestringfile, 'wb') as f:
        f.write(bytestring)
    with open(longbytesfile, 'wb') as f:
        f.write(11111*b'1')
        f.write(b'\n')
        f.write(22222*b'2')
        f.write(b'\n')
        f.write(33333*b'3')
        f.write(b'\n')
    with open(longstringfile, 'wt') as f:
        f.write(11111*'1')
        f.write('\n')
        f.write(22222*'2')
        f.write('\n')
        f.write(33333*'3')
        f.write('\n')
    print("created test data in path '{}'".format(path))
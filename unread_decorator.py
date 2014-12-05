import io

__version__ = "0.1b"

__all__ = ["add_unread"]

def add_unread(obj):
    if not _hasfunc(obj, 'read'):
        raise AttributeError("unread_decorator: object has no 'read()' function")
    obj._unread = dict(  # orig functions, unread data
            read=type(obj).read,
            data=None,
            )
    obj.unread = lambda data: _unread(obj, data)
    obj.read = lambda *args, **kwargs: _read(obj, *args, **kwargs)
    if _hasfunc(obj, 'readline'):
        obj._unread['readline'] = type(obj).readline
        obj.readline = lambda *args, **kwargs: _readline(obj, *args, **kwargs)
    if _hasfunc(obj, 'seekable'):
        obj._unread['seekable'] = type(obj).seekable
        obj.seekable = lambda: _seekable(obj)
    if _hasfunc(obj, 'seek'):
        obj._unread['seek'] = type(obj).seek
        obj.seek = lambda *args, **kwargs: _seek(obj, *args, **kwargs)
    return obj

def _unread(self, data):
    if self._unread['data'] is None:
        self._unread['data'] = data
    else:
        self._unread['data'] = data + self._unread['data']  # prepend: stack discipline

def _read(self, size=-1):
    unreaddata = self._unread['data']  # helper var for readability
    if unreaddata is None:  # nothing unread: normal call
        return self._unread['read'](self, size)
    else:
        if size == -1:
            data = unreaddata + self._unread['read'](self, size)
            unreaddata = None
        else:
            data = unreaddata[0:min(size,len(unreaddata))]
            if size > len(unreaddata):
                moredata = self._unread['read'](self, size-len(unreaddata))
                data = data + moredata
            unreaddata = None if size >= len(unreaddata) else unreaddata[size:]
        self._unread['data'] = unreaddata
        return data

def _readline(self, size=-1):
    unreaddata = self._unread['data']  # helper var for readability
    if unreaddata is None:
        return self._unread['readline'](self, size)
    newlinepos = _newlinepos(unreaddata)
    if newlinepos == -1:
        self._unread['data'] = None
        moredata = self._unread['readline'](self, size-len(unreaddata))
        return unreaddata + moredata
    else:
        return _read(self, newlinepos+1)

def _seekable(self):
    unreaddata = self._unread['data']  # helper var for readability
    if unreaddata is None:
        return self._unread['seekable'](self)
    else:
        return False  # we do not support seeking in unread data

def _seek(self, offset, whence=io.SEEK_SET):
    unreaddata = self._unread['data']  # helper var for readability
    if unreaddata is None:
        return self._unread['seek'](self, offset, whence)
    else:
        raise OSError  # we do not support seeking in unread data

########## helpers: ##########

def _newlinepos(unreaddata):
    newline = '\n' if isinstance(unreaddata, str) else b'\n'  # TODO: universal newline mode
    return unreaddata.find(newline)  # -1 if not found

def _hasfunc(obj, funcname):
    return hasattr(obj, funcname) and callable(getattr(obj, funcname))

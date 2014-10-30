import time

from ..errors import ButtFSError

class CachedObject(object):
    # no caching by default
    CACHE_EXPIRE = 0

    def __init__(self):
        self.last_update = time.time()
        self.dirty = False

    # to be overidden by sub-classes
    def _initialize_self(self, request, x_headers):
        pass

    def _refresh_request(self, debug=False):
        pass

    def _update_self(self, debug=False):

        result, x_headers = self._refresh_request(debug)
        self._initialize_self(result, x_headers)
        self.dirty = False
        self.last_update = time.time()
        return True

    def _prepare_to_read(self):
        if self.CACHE_EXPIRE != None and\
            (self.dirty or (time.time() - self.last_update) > self.CACHE_EXPIRE):
            self._update_self()

    def last_updated(self):
        return self.last_update

    def age(self):
        return time.time() - self.last_update

    def refresh(self, debug=False):
        return self._update_self(debug)

    def _mark_dirty(self):
        self.dirty = True

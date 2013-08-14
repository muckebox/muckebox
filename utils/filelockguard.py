from threading import Lock

from lockguard import LockGuard

class FileLockGuard(object):
    lock = Lock()
    open_files = set()

    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode

    def __enter__(self):
        self.fh = open(self.filename, self.mode)

        with LockGuard(self.lock):
            self.open_files.add(self.filename)

        return self.fh

    def __exit__(self, *ignored):
        self.fh.close()

        with LockGuard(self.lock):
            self.open_files.remove(self.filename)

    @classmethod
    def is_opened(cls, filename):
        with LockGuard(self.lock):
            return filename in self.open_files

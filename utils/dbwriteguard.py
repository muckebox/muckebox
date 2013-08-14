from threading import Lock

from lockguard import LockGuard

class DbWriteGuard(LockGuard):
    lock = Lock()

    def __init__(self):
        LockGuard.__init__(self, self.lock)

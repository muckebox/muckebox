class LockGuard(object):
    def __init__(self, lock):
        self.lock = lock

    def __enter__(self):
        self.lock.acquire()
        
        return self.lock

    def __exit__(self, *ignored):
        self.lock.release()
    

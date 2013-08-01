from threading import Timer

class DelayedTask(object):
    def __init__(self, delay):
        self.timer = False
        self.delay = delay
        self.last_cookie = None

    def post(self, fn, cookie = None):
        if self.timer and self.last_cookie == cookie:
            try:
                self.timer.cancel()
            except:
                pass

        self.timer = Timer(self.delay, fn)
        self.last_cookie = cookie
        self.timer.start()


import Queue

from watcher import Watcher
from walker import Walker
from reader import Reader
from validator import Validator

from utils.config import Config

class Scanner:
    def __init__(self, path):
        self.path = path
        self.queue = Queue.PriorityQueue()
        self.watcher = Watcher(path, self.queue)
        self.walker = Walker(path, self.queue, Config.is_rescan_forced())
        self.reader = Reader(self.queue)
        self.validator = Validator(self.queue)

    def start(self):
        self.validator.start()
        self.watcher.start()
        self.walker.start()
        self.reader.start()

    def stop(self):
        self.watcher.stop()
        self.reader.stop()

        self.validator.join()
        self.walker.join()
        self.watcher.join()
        self.reader.join()


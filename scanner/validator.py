import threading

from pathupdate import PathUpdate

from db.db import Db
from db.models.file import File

class Validator(threading.Thread):
    LOG_TAG = "VALIDATOR"

    def __init__(self, queue):
        threading.Thread.__init__(self)
        
        self.queue = queue

        self.name = self.LOG_TAG

    def run(self):
        session = Db.get_session()

        for f in session.query(File.path):
            self.queue.put(PathUpdate(f.path, False))

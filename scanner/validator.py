import threading

from db import Db
from models.file import File
from pathupdate import PathUpdate

class Validator(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        
        self.queue = queue

    def run(self):
        session = Db.get_session()

        for f in session.query(File.path):
            self.queue.put(PathUpdate(f.path, False))

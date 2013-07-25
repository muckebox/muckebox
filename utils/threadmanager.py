import collections
import threading

class ThreadManager():
    thread_status = { }

    Status = collections.namedtuple('Status', [
            'id',
            'name',
            'status'
            ])
    
    @classmethod
    def get_all(cls):
        return [ cls.Status(t.ident, t.name,
                            cls.thread_status.get(t.ident, '<unknown>'))
                 for t in threading.enumerate() ]

    @classmethod
    def status(cls, status):
        cls.thread_status[threading.current_thread().ident] = status

    @classmethod
    def name(cls, name):
        threading.current_thread().name = name

        

import threading

from abc import abstractmethod

class BaseTranscoder(threading.Thread):
    class Quality:
        LOWEST  = 1
        LOW     = 2
        MEDIUM  = 3
        HIGH    = 4
        HIGHEST = 5
        
    def __init__(self, path = False, queue = False, quality = Quality.HIGHEST):
        threading.Thread.__init__(self)

        if path:
            self.set_source_file(path)

        self.set_quality(quality)
        self.set_output_queue(queue)

        self.completed = False

    def set_output_queue(self, queue):
        self.queue = queue

    def has_finished(self):
        return not self.is_alive()

    def set_completed(self):
        self.completed = True

    def has_completed(self):
        return self.completed

    def wait(self):
        if not self.has_finished():
            self.join()

    @abstractmethod
    def set_quality(self, quality):
        pass

    @abstractmethod
    def set_source_file(self, path):
        pass
    
    @abstractmethod
    def get_suffix(self):
        pass

    @abstractmethod
    def get_mime_type(self):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def abort(self):
        pass


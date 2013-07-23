import threading

from abc import abstractmethod

class BaseTranscoder(threading.Thread):
    class Quality:
        LOWEST  = 1
        LOW     = 2
        MEDIUM  = 3
        HIGH    = 4
        HIGHEST = 5
        
    def __init__(self, input = False, queue = False, format = { }):
        threading.Thread.__init__(self)

        if input:
            self.set_source_file(input["path"])
            self.set_input_bits_per_sample(input.get("bits_per_sample"))
            self.set_input_sample_rate(input.get("sample_rate"))

        self.set_quality(format.get("quality", self.Quality.HIGHEST))

        self.set_max_bits_per_sample(format.get("bits_per_sample", 0))
        self.set_max_sample_rate(format.get("sample_rate", 0))

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

    def set_max_bits_per_sample(self, bits_per_sample):
        self.max_bits_per_sample = bits_per_sample

    def set_input_bits_per_sample(self, bits_per_sample):
        self.input_bits_per_sample = bits_per_sample

    def set_max_sample_rate(self, sample_rate):
        self.max_sample_rate = sample_rate

    def set_input_sample_rate(self, sample_rate):
        self.input_sample_rate = sample_rate

    def get_output_bits_per_sample(self):
        if self.max_bits_per_sample == 0:
            return self.input_bits_per_sample

        if self.input_bits_per_sample <= self.max_bits_per_sample:
            return self.input_bits_per_sample

        return self.max_bits_per_sample

    def get_output_sample_rate(self):
        if self.max_sample_rate == 0:
            return self.input_sample_rate

        if self.input_sample_rate <= self.max_sample_rate:
            return self.input_sample_rate

        half_rate = self.input_sample_rate / 2

        if (half_rate <= self.max_sample_rate and \
                half_rate >= self.max_sample_rate * 0.9):
            return half_rate

        return self.max_sample_rate

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


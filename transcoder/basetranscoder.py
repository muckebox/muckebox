import threading
import collections

from abc import abstractmethod
from transcodermanager import TranscoderManager

class BaseTranscoder(threading.Thread):
    LOG_TAG = "BASETRANSCODER"

    OutputConfiguration = collections.namedtuple('OutputConfiguration', [
            'path',
            'format',
            'quality',
            'max_bits_per_sample',
            'max_sample_rate'
            ])

    InputConfiguration = collections.namedtuple('InputConfiguration', [
            'id',
            'track_id',
            'path',
            'bits_per_sample',
            'sample_rate'
            ])

    class Quality:
        LOWEST  = 1
        LOW     = 2
        MEDIUM  = 3
        HIGH    = 4
        HIGHEST = 5

    listener = set()
        
    def __init__(self, input = False, queue = False, output = False):
        threading.Thread.__init__(self)

        if input:
            self.set_source_file(input.path)
            self.set_track_id(input.track_id)
            self.set_input_bits_per_sample(input.bits_per_sample)
            self.set_input_sample_rate(input.sample_rate)

        if output:
            self.set_quality(output.quality)
            self.set_max_bits_per_sample(output.max_bits_per_sample)
            self.set_max_sample_rate(output.max_sample_rate)

        self.set_output_queue(queue)
        self.completed = False

        self.name = self.LOG_TAG

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

    def set_track_id(self, track_id):
        self.track_id = track_id

    def get_track_id(self, track_id):
        return self.track_id

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

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def resume(self):
        pass

    def add_listener(self, listener):
        self.listeners.add(listener)
        
    def remove_listener(self, listener):
        self.listeners.discard(listener)

    def has_listeners(self):
        return len(self.listeners) > 0

    def done(self):
        TranscoderManager.on_transcoding_done(self)

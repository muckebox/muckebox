from basetranscoder import BaseTranscoder

class WrappingTranscoder(BaseTranscoder):
    def __init__(self, input_config = False, output_config = False):
        BaseTranscoder.__init__(self, input_config, output_config)

        self.transcoder.set_done_listener(self)

    def set_quality(self, quality):
        self.transcoder.set_quality(quality)

    def get_suffix(self):
        return self.transcoder.get_suffix()

    def get_mime_type(self):
        return self.transcoder.get_mime_type()

    def abort(self):
        self.transcoder.abort()

    def pause(self):
        self.transcoder.pause()
        
    def resume(self):
        self.transcoder.resume()

    def has_completed(self):
        return self.transcoder.has_completed()

    def get_track_id(self):
        return self.transcoder.get_track_id()

    def set_track_id(self, track_id):
        self.transcoder.set_track_id(track_id)

    def get_progress(self):
        return self.transcoder.get_progress()

    def get_stream_path(self):
        return self.transcoder.get_stream_path()

    def flush(self):
        return self.transcoder.flush()

    def is_paused(self):
        return self.transcoder.is_paused()

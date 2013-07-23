import hashlib
import os.path

from basetranscoder import BaseTranscoder
from oggtranscoder import OggTranscoder
from mp3transcoder import MP3Transcoder
from opustranscoder import OpusTranscoder
from nulltranscoder import NullTranscoder
from cachingtranscoder import CachingTranscoder

from db import Db
from models.transcoding import Transcoding
from config import Config

class AutoTranscoder(BaseTranscoder):
    TRANSCODER_MAP = {
        'mp3': MP3Transcoder,
        'ogg': OggTranscoder,
        'opus': OpusTranscoder
        }

    def __init__(self, track, format, queue):
        source = {
            'path': track.file.path,
            'sample_rate': track.sample_rate,
            'bits_per_sample': track.bits_per_sample
            }

        cached_path = self.get_cached_transcoding(source, format)

        if cached_path:
            self.transcoder = NullTranscoder({ "path": cached_path }, queue)
        else:
            transcoder_cls = self.get_transcoder(format)

            if transcoder_cls:
                output_path = self.get_cached_path(track, format)

                transcoder = transcoder_cls(source, queue, format)
                self.transcoder = CachingTranscoder(transcoder,
                                                    source["path"],
                                                    output_path)
            else:
                self.transcoder = NullTranscoder(source, queue)

        BaseTranscoder.__init__(self, source, queue, format)

    def set_quality(self, quality):
        self.transcoder.set_quality(quality)

    def set_source_file(self, path):
        pass

    def get_suffix(self):
        return self.transcoder.get_suffix()

    def get_mime_type(self):
        return self.transcoder.get_mime_type()

    def run(self):
        self.transcoder.start()
        self.transcoder.wait()

    def abort(self):
        self.transcoder.abort()

    def has_completed(self):
        return self.transcoder.has_completed()

    @classmethod
    def get_transcoder(cls, format):
        if "format" in format and format["format"] in cls.TRANSCODER_MAP:
            return cls.TRANSCODER_MAP[format["format"]]

        return False

    @classmethod
    def get_cached_transcoding(cls, source, format):
        session = Db.get_session()
        query = session.query(Transcoding). \
            filter(Transcoding.source_path == source["path"]). \
            filter(Transcoding.format == format["format"]). \
            filter(Transcoding.quality == format["quality"]). \
            filter(Transcoding.bits_per_sample <= format["bits_per_sample"]). \
            filter(Transcoding.sample_rate <= format["sample_rate"])

        for transcoding in query:
            if not cls.validate_cached_path(source["path"], transcoding.path):
                session.delete(transcoding)
                session.commit()
            else:
                return transcoding.path

        return False

    @classmethod
    def validate_cached_path(cls, source_path, dest_path):
        if not os.path.exists(dest_path):
            return False

        if os.path.getmtime(dest_path) < os.path.getmtime(source_path):
            return False

        return True

    @classmethod
    def get_cached_path(cls, track, format):
        filekey = "%s:%d" % (track.stringid, format["quality"])
        h = hashlib.sha1(filekey.encode('utf-8')).hexdigest()
        filename = "%s.%s" % (h, format["format"])

        return Config.get_cache_path() + "/" + filename


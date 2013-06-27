import hashlib
import os.path

from basetranscoder import BaseTranscoder
from oggtranscoder import OggTranscoder
from mp3transcoder import MP3Transcoder
from nulltranscoder import NullTranscoder
from cachingtranscoder import CachingTranscoder

from db import Db
from models.transcoding import Transcoding
from config import Config

class AutoTranscoder(BaseTranscoder):
    TRANSCODER_MAP = {
        'mp3': MP3Transcoder,
        'ogg': OggTranscoder
        }

    def __init__(self, track, fmt, quality, queue):
        source_path = track.file.path
        cached_path = self.get_cached_transcoding(source_path, fmt, quality)

        if cached_path:
            self.transcoder = NullTranscoder(cached_path, queue)
        else:
            transcoder_cls = self.get_transcoder(fmt)

            if transcoder_cls:
                output_path = self.get_cached_path(track, fmt, quality)

                transcoder = transcoder_cls(source_path, queue, quality)
                self.transcoder = CachingTranscoder(transcoder, source_path,
                                                    output_path)
            else:
                self.transcoder = NullTranscoder(source_path, queue)

        BaseTranscoder.__init__(self, source_path, queue, quality)

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
    def get_transcoder(cls, fmt):
        if fmt in cls.TRANSCODER_MAP:
            return cls.TRANSCODER_MAP[fmt]

        return False

    @classmethod
    def get_cached_transcoding(cls, path, fmt, quality):
        session = Db.get_session()
        query = session.query(Transcoding). \
            filter(Transcoding.source_path == path). \
            filter(Transcoding.format == fmt). \
            filter(Transcoding.quality == quality)

        for transcoding in query:
            if not cls.validate_cached_path(path, transcoding.path):
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
    def get_cached_path(cls, track, format, quality):
        h = hashlib.sha1(track.stringid + ":" + str(quality)).hexdigest()
        filename = h + "." + format

        return Config.args.cache_dir + "/" + filename


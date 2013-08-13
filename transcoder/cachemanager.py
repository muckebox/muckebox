import os
import hashlib

from db import Db
from db.models import Transcoding

from utils import Settings

class CacheManager():
    @classmethod
    def add_transcoding(cls, transcoding):
        session = Db.get_session()
        session.add(transcoding)
        session.commit()

    @classmethod
    def get_cached_path(cls, input, output):
        session = Db.get_session()
        query = session.query(Transcoding). \
            filter(Transcoding.source_path == input.path). \
            filter(Transcoding.format == output.format). \
            filter(Transcoding.quality == output.quality). \
            filter(Transcoding.bits_per_sample <= output.max_bits_per_sample). \
            filter(Transcoding.sample_rate <= output.max_sample_rate)

        for transcoding in query:
            if not cls.validate_cached_path(input.path, transcoding.path):
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
    def get_path_in_cache(cls, input, output):
        filekey = "%s:%d" % (input.id, output.quality)
        h = hashlib.sha1(filekey.encode('utf-8')).hexdigest()
        filename = "%s.%s" % (h, output.format)

        return Settings.get_cache_path() + "/" + filename

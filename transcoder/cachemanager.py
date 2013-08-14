import os
import hashlib

import cherrypy

from sqlalchemy import func
from sqlalchemy.sql.expression import asc

from db import Db
from db.models import Transcoding

from utils import Settings, FileLockGuard, DbWriteGuard

class CacheManager():
    LOG_TAG = "CACHEMANAGER"

    @classmethod
    def add_transcoding(cls, transcoding):
        with DbWriteGuard():
            session = Db.get_session()
            session.add(transcoding)
            session.commit()

            cls.vacuum(session)
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

        if not os.path.exists(source_path):
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

    @classmethod
    def get_cache_size(cls, session):
        return session.query(func.sum(Transcoding.size)).one()[0]

    @classmethod
    def remove_oldest_transcoding(cls, session):
        for t in session.query(Transcoding).order_by(asc(Transcoding.created)):
            if not FileLockGuard.is_opened(t.path):
                if os.path.exists(t.path):
                    os.unlink(t.path)

                session.delete(t)

                return

    @classmethod
    def purge_orphans(cls, session):
        for t in session.query(Transcoding):
            if not cls.validate_cached_path(t.source_path, t.path):
                if not FileLockGuard.is_opened(t.path):
                    cherrypy.log("Removed one orphaned encoding (size %d)" %
                                 (t.size), cls.LOG_TAG)

                    if os.path.exists(t.path):
                        os.unlink(t.path)

                    session.delete(t)

    @classmethod
    def vacuum(cls, session):
        cls.purge_orphans(session)
        
        num_removed = 0

        while cls.get_cache_size(session) > Settings.get_max_cache_size():
            cls.remove_oldest_transcoding(session)
            num_removed += 1

        if num_removed > 0:
            cherrypy.log("Expired %d transcoding%s (cache size: %d)" %
                         (num_removed, "s" if num_removed != 1 else "",
                          cls.get_cache_size(session)), cls.LOG_TAG)


        

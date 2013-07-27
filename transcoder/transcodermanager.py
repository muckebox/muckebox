import mmap
from threading import Lock

import cherrypy
import sqlalchemy.orm.exc

from utils import LockGuard

from basetranscoder import BaseTranscoder
from autotranscoder import AutoTranscoder

from db.models import Track
from db import Db

class TranscoderManager():
    LOG_TAG = "TRANSCODERMANAGER"

    active = set()

    queue = [ ]

    lock = Lock()

    @classmethod
    def send_progress(cls, path, offset, limit, queue):
        cherrypy.log("Sending %d bytes catchup data (%d-%d)" % \
                         (limit - offset, offset, limit), cls.LOG_TAG)
        
        with open(path, 'rb') as f:
            mm = mmap.mmap(f.fileno(), limit, mmap.MAP_PRIVATE, mmap.PROT_READ)

            try:
                while offset < limit - 1:
                    end = min(offset + BaseTranscoder.BLOCK_SIZE, limit)

                    queue.put(mm[offset:end])

                    offset = end
            finally:
                mm.close()

    @classmethod
    def get_active_transcoder(cls, track_id, config, queue):
        for t in cls.active:
            if t.get_track_id() == track_id:
                cherrypy.log("Found active transcoder for %d, re-using" % \
                                 (track_id), cls.LOG_TAG)

                t.pause()
                t.flush()

                cls.send_progress(t.get_stream_path(), config.offset,
                                  t.get_progress(), queue)

                return t

        return False

    @classmethod
    def get_track(cls, trackid, session):
        try:
            return session.query(Track).filter(Track.id == trackid).one()
        except sqlalchemy.orm.exc.NoResultFound:
            return False

    @classmethod
    def get_new_transcoder(cls, track_id, output_config):
        cherrypy.log("Creating new transcoder for %d" % (track_id),
                     cls.LOG_TAG)

        session = Db.get_session()
        track = cls.get_track(int(track_id), session)

        if not track:
            return False

        input_config = AutoTranscoder.InputConfiguration(
            id = track.stringid,
            track_id = track_id,
            path = track.file.path,
            bits_per_sample = track.bits_per_sample,
            sample_rate = track.sample_rate
            )

        transcoder = AutoTranscoder(input_config, output_config)
        transcoder.set_done_listener(cls)

        return transcoder

    @classmethod
    def pause_free_running(cls, new_transcoder):
        for t in cls.active:
            if not t.has_listeners() and t != new_transcoder:
                cherrypy.log("Pausing free-running transcoder for %d" % \
                                 (t.get_track_id()), cls.LOG_TAG)
                t.pause()

    @classmethod
    def get_transcoder(cls, track_id, output_config, queue = False):
        with LockGuard(cls.lock) as l:
            ret = cls.get_active_transcoder(track_id, output_config, queue)

            if not ret:
                ret = cls.get_new_transcoder(track_id, output_config)

                if not ret:
                    return False

                cls.active.add(ret)

            while track_id in cls.queue:
                cls.queue.remove(track_id)

            cls.pause_free_running(ret)

            if queue:
                ret.add_listener(queue)

            if not ret.is_alive():
                ret.start()

            ret.resume()

            return ret

    @classmethod
    def on_transcoding_done(cls, transcoder):
        cherrypy.log("Transcoding for %d finished" % \
                         (transcoder.get_track_id()), cls.LOG_TAG)

        with LockGuard(cls.lock) as l:
            cls.active.discard(transcoder)
            cls.try_starting_next()

    @classmethod
    def try_starting_next(cls):
        for t in cls.active:
            if not t.is_paused():
                return

        for t in cls.active:
            if t.is_paused():
                cherrypy.log("Resuming free-running transcoder for %d" % \
                                 (t.get_track_id()), cls.LOG_TAG)
                t.resume()
                return

        # XXX handle queue

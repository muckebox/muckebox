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
    paused = set()

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
        for t in cls.active.union(cls.paused):
            if t.get_track_id() == track_id:
                cherrypy.log("Found active transcoder for %d, re-using" % \
                                 (track_id), cls.LOG_TAG)

                cls.pause_transcoder(t)

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
        transcoder.set_state_listener(cls)

        return transcoder

    @classmethod
    def pause_transcoder(cls, transcoder):
        transcoder.pause()

        cls.active.discard(transcoder)
        cls.paused.add(transcoder)

    @classmethod
    def resume_transcoder(cls, transcoder):
        cls.paused.discard(transcoder)
        cls.active.add(transcoder)

        transcoder.resume()

    @classmethod
    def pause_free_running(cls, new_transcoder):
        for t in cls.active:
            if not t.has_listeners() and t != new_transcoder:
                cherrypy.log("Pausing free-running transcoder for %d" % \
                                 (t.get_track_id()), cls.LOG_TAG)
                cls.pause_transcoder(t)

    @classmethod
    def get_transcoder(cls, track_id, output_config, queue = False):
        with LockGuard(cls.lock) as l:
            ret = cls.get_active_transcoder(track_id, output_config, queue)

            if not ret:
                ret = cls.get_new_transcoder(track_id, output_config)

                if not ret:
                    return False

            while track_id in cls.queue:
                cls.queue.remove(track_id)

            cls.pause_free_running(ret)

            if queue:
                ret.add_listener(queue)

            if not ret.is_alive():
                ret.start()

            cls.resume_transcoder(ret)

            return ret

    @classmethod
    def on_transcoding_done(cls, transcoder):
        cherrypy.log("Transcoding for %d finished" % \
                         (transcoder.get_track_id()), cls.LOG_TAG)

        with LockGuard(cls.lock) as l:
            cls.active.discard(transcoder)
            cls.try_starting_next()

    @classmethod
    def on_free_running(cls, transcoder):
        with LockGuard(cls.lock) as l:
            if len(cls.active) > 1:
                cherrypy.log("Transcoder for %d became free-running, pausing" %
                             (transcoder.get_track_id()), cls.LOG_TAG)

                cls.pause_transcoder(transcoder)

    @classmethod
    def try_starting_next(cls):
        if len(cls.active) > 0:
            return

        if len(cls.paused) > 0:
            t = cls.paused.pop()

            cherrypy.log("Resuming free-running transcoder for %d" % \
                             (t.get_track_id()), cls.LOG_TAG)

            cls.resume_transcoder(t)

            return

        # XXX handle queue

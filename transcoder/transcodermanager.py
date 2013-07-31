import mmap
import collections
from threading import Lock

import cherrypy
import sqlalchemy.orm.exc

from utils import LockGuard

from basetranscoder import BaseTranscoder
from autotranscoder import AutoTranscoder
from cachingtranscoder import CachingTranscoder

from db.models import Track
from db import Db

class TranscoderManager():
    LOG_TAG = "TRANSCODERMANAGER"

    Request = collections.namedtuple('Request', [
            'track_id',
            'config'
            ])

    active = set()
    paused = set()

    queue = [ ]

    lock = Lock()

    @classmethod
    def send_progress(cls, path, offset, limit, queue):
        if limit == 0:
            return
        
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
    def get_active_transcoder(cls, request, queue):
        for t in cls.active.union(cls.paused):
            if t.get_track_id() == request.track_id:
                cherrypy.log("Found active transcoder for %d, re-using" % \
                                 (request.track_id), cls.LOG_TAG)

                cls.pause_transcoder(t)

                t.flush()

                cls.send_progress(t.get_stream_path(), request.config.offset,
                                  t.get_progress(), queue)

                return t

        return False

    @classmethod
    def get_track(cls, track_id, session):
        try:
            return session.query(Track).filter(Track.id == track_id).one()
        except sqlalchemy.orm.exc.NoResultFound:
            return False

    @classmethod
    def get_input_config(cls, request):
        session = Db.get_session()
        track = cls.get_track(int(request.track_id), session)

        if not track:
            return False

        input_config = AutoTranscoder.InputConfiguration(
            id = track.stringid,
            track_id = request.track_id,
            path = track.file.path,
            bits_per_sample = track.bits_per_sample,
            sample_rate = track.sample_rate
            )

        return input_config

    @classmethod
    def get_new_transcoder(cls, request):
        cherrypy.log("Creating new transcoder for %d" % (request.track_id),
                     cls.LOG_TAG)
        
        input_config = cls.get_input_config(request)

        if not input_config:
            return False

        transcoder = AutoTranscoder(input_config, request.config)
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
        for t in cls.active.copy():
            if not t.has_listeners() and t != new_transcoder:
                cherrypy.log("Pausing free-running transcoder for %d" % \
                                 (t.get_track_id()), cls.LOG_TAG)
                cls.pause_transcoder(t)

    @classmethod
    def ensure_transcoder(cls, request, queue = False):
        ret = cls.get_active_transcoder(request, queue)

        if not ret:
            ret = cls.get_new_transcoder(request)

        if not ret:
            return False

        cls.pause_free_running(ret)

        if queue:
            ret.add_listener(queue)

        if not ret.is_alive():
            ret.start()

        cls.resume_transcoder(ret)

        return ret

    @classmethod
    def get_transcoder(cls, request, queue):
        with LockGuard(cls.lock) as l:
            return cls.ensure_transcoder(request, queue)

    @classmethod
    def enqueue_request(cls, request):
        with LockGuard(cls.lock) as l:
            cls.queue.append(request)
            cls.try_starting_next()

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
    def try_starting_queue(cls):
        if len(cls.queue) > 0:
            request = cls.queue.pop()
            input_config = cls.get_input_config(request)

            if CachingTranscoder.get_cached_transcoding(input_config,
                                                        request.config):
                return False

            cls.ensure_transcoder(request)

            return True
            
        return False

    @classmethod
    def try_resuming(cls):
        if len(cls.paused) > 0:
            t = cls.paused.pop()

            cherrypy.log("Resuming free-running transcoder for %d" % \
                             (t.get_track_id()), cls.LOG_TAG)

            cls.resume_transcoder(t)

            return

    @classmethod
    def try_starting_next(cls):
        if len(cls.active) > 0:
            return

        if cls.try_starting_queue():
            return

        cls.try_resuming()

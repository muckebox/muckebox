class TranscoderManager():
    active = set()

    queue = [ ]

    @classmethod
    def get_active_transcoder(cls, track_id, config):
        for t in cls.active:
            if t.get_track_id() == track_id:
                t.pause()

                return t

        return False

    @classmethod
    def get_new_transcoder(cls, track_id, config):
        # XXX
        pass

    @classmethod
    def pause_free_running(cls):
        for t in cls.active:
            if not t.has_listeners():
                t.pause()

    @classmethod
    def get_queue(cls, track_id, output_config, listener):
        ret = cls.get_active_transcoder(track_id, output_config)

        if not ret:
            ret = cls.get_new_transcoder(track_id, output_config)

        cls.queue.remove(track_id)
        cls.pause_free_running()

        queue = ret.get_queue(output_config)

        ret.add_listener(listener)
        ret.resume()

        return (ret, queue)

    @classmethod
    def on_transcoding_done(cls, transcoder):
        cls.active.discard(transcoder)
            

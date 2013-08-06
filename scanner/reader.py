import threading
import os.path
import time
import logging

import sqlalchemy.orm.exc
import cherrypy

from pathupdate import PathUpdate

from utils import Config, DelayedTask
from mutabrainz.autofile import AutoFile
from db.models import File, Track, Album, Artist
from db import Db

class Reader(threading.Thread):
    LOG_TAG = 'READER'
    UPDATE_DELAY = 10

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.stop_thread = False
        self.delayed_task = DelayedTask(self.UPDATE_DELAY)

        self.name = self.LOG_TAG

    def run(self):
        session = Db().get_session()

        while True:
            (priority, update) = self.queue.get()
            
            if self.stop_thread:
                break

            try:
                self.handle_file(
                    update._replace(path = os.path.abspath(update.path)),
                    session)
                session.commit()
            except:
                cherrypy.log.error("Cannot read '%s', skipping" % (update.path),
                                   self.LOG_TAG)
                session.rollback()

    def stop(self):
        self.stop_thread = True
        self.queue.put((0, False))

    def handle_file(self, update, session):
        if not AutoFile.is_supported(update.path):
            return

        if os.path.exists(update.path):
            if self.file_updated(update.path, session) or update.force_update:
                self.handle_update(update.path, session)

        else:
            self.handle_deletion(update.path, session)

    def file_updated(self, filename, session):
        for res in session.query(File).filter(File.path == filename):
            return res.mtime < os.path.getmtime(filename)

        return True

    def handle_update(self, filename, session):
        cherrypy.log("Updating '%s'" % (filename), self.LOG_TAG)

        try:
            fh = session.query(File).filter(File.path == filename).one()
        except sqlalchemy.orm.exc.NoResultFound:
            fh = self.handle_new(filename, session)
            
        fh.mtime = os.path.getmtime(filename)

        self.check_tracks(fh, session)
        self.delete_unused()
        
    def handle_new(self, filename, session):
        fh = File(path = filename, mtime = os.path.getmtime(filename))
        session.add(fh)

        return fh

    def check_tracks(self, fh, session):
        file = AutoFile(fh.path)

        for track in file.get_tracks():
            artist = self.get_artist(track.get('artist'), session)
            album_artist = self.get_album_artist(track, session)
            album = self.get_album(track, album_artist, session)

            try:
                dbtrack = self.get_dbtrack(track['stringid'], session)
            except sqlalchemy.orm.exc.NoResultFound:
                dbtrack = Track()
                fh.tracks.append(dbtrack)
                album.tracks.append(dbtrack)
                artist.tracks.append(dbtrack)

            self.verify_relations(dbtrack, album, artist, album_artist)

            dbtrack.from_dict(track)

    def get_album_artist(self, track, session):
        if 'albumartist' in track:
            name = track.get('albumartist')

            if len(name) > 0:
                return self.get_artist(name, session)

        artist = self.get_va_album_artist_id(track, session)

        if not artist:
            artist = self.get_artist(track.get('artist'), session)

            self.update_other_album_tracks(track, artist, session)

        return artist

    def update_other_album_tracks(self, track, artist, session):
        for album in session.query(Album). \
            join(Track). \
            join(Artist, Artist.id == Track.artist_id). \
            filter(Album.title == track.get('album')). \
            filter(Artist.name == track.get('artist')). \
            filter(Album.artist_id != artist.id):
            album.artist_id = artist.id

    def get_va_album_artist_id(self, track, session):
        directory = track.get('directory')
        album_title = track.get('album')
        artist_name = track.get('artist')

        va_artist = False
        found = False

        for album in session.query(Album). \
                join(Track). \
                join(Artist, Artist.id == Track.artist_id). \
                filter(Album.title == album_title). \
                filter(Track.directory == directory). \
                filter(Track.album_artist_id == None). \
                filter(Artist.name != artist_name):
            found = True

            if not va_artist:
                va_artist = self.get_va_artist(session)

            album.artist_id = va_artist.id

        if found:
            return va_artist
        else:
            return False

    def get_artist(self, name, session):
        try:
            return session.query(Artist).filter(Artist.name == name).one()
        except sqlalchemy.orm.exc.NoResultFound:
            ret = Artist(name = name)
            session.add(ret)

            return ret

    def get_album(self, track, artist, session):
        title = track.get('album')

        ret = session.query(Album). \
            filter(Album.title == title). \
            filter(Album.artist_id == artist.id). \
            first()

        if ret is None:
            ret = Album(title = title, created = int(time.time()))
            artist.albums.append(ret)
            session.add(ret)
        
        return ret

    def get_va_artist(self, session):
        try:
            return session.query(Artist). \
                filter(Artist.name == Config.get_va_artist()).one()
        except sqlalchemy.orm.exc.NoResultFound:
            va_artist = Artist(name = Config.get_va_artist())
            session.add(va_artist)

            return va_artist

    def get_dbtrack(self, stringid, session):
        return session.query(Track).filter(Track.stringid == stringid).one()
                
    def handle_deletion(self, filename, session):
        for f in session.query(File).filter(File.path.like(filename + '%')):
            cherrypy.log("Deleting '%s'" % (f.path), self.LOG_TAG)
            session.delete(f)

        self.delete_unused()

    def verify_relations(self, track, album, artist, album_artist):
        if album.artist_id != album_artist.id:
            album.artist_id = album_artist.id

        if track.album_id != album.id:
            track.album_id = album.id
        if track.artist_id != artist.id:
            track.artist_id = artist.id

        self.delete_unused()

    def delete_unused(self):
        def do_delete():
            session = Db().get_session()

            count = session.query(Album).filter(Album.tracks == None). \
                delete(synchronize_session = False)

            if count > 0:
                cherrypy.log("Deleted %d orphaned album(s)" % (count),
                             self.LOG_TAG)

            count = session.query(Artist).filter(Artist.albums == None). \
                filter(Artist.tracks == None). \
                delete(synchronize_session = False)

            if count > 0:
                cherrypy.log("Deleted %d orphaned artist(s)" % (count),
                             self.LOG_TAG)

            session.commit()
        
        self.delayed_task.post(do_delete)




            

import threading
import os.path
import time
import logging

import sqlalchemy.orm.exc
import cherrypy

from pathupdate import PathUpdate

from utils import Config
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
        self.current_timer = False

        self.name = self.LOG_TAG

    def run(self):
        session = Db().get_session()

        while True:
            (priority, update) = self.queue.get()
            
            if self.stop_thread:
                break

            try:
                self.handle_file(
                    update._replace(path = self.clean_path(update.path)),
                    session)
                session.commit()
            except:
                cherrypy.log.error("Cannot read '%s', skipping" % (update.path),
                                   self.LOG_TAG)
                session.rollback()

    def stop(self):
        self.stop_thread = True
        self.queue.put((0, False))

    def clean_path(self, path):
        path = os.path.abspath(path)

        if isinstance(path, unicode):
            return path
        else:
            return unicode(path, errors = 'replace')

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

            (album_artist, force_solo) = self.get_album_artist(track,
                                                               artist,
                                                               session)

            (album, album_artist) = self.get_album(album_artist,
                                                   track.get('album'),
                                                   track.get('directory'),
                                                   session,
                                                   force_solo)

            try:
                dbtrack = self.get_dbtrack(track['stringid'], session)
            except sqlalchemy.orm.exc.NoResultFound:
                dbtrack = Track()
                fh.tracks.append(dbtrack)
                album.tracks.append(dbtrack)
                artist.tracks.append(dbtrack)

            self.verify_relations(dbtrack, album, artist, album_artist)

            dbtrack.from_dict(track)

    def verify_relations(self, track, album, artist, album_artist):
        if album.artist_id != album_artist.id:
            album.artist_id = album_artist.id

        if track.album_id != album.id:
            track.album_id = album.id
        if track.artist_id != artist.id:
            track.artist_id = artist.id
        if track.album_artist_id != album_artist.id:
            track.album_artist_id = album_artist.id

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

        if self.current_timer:
            try:
                self.current_timer.cancel()
            except:
                pass

        self.current_timer = threading.Timer(
            self.UPDATE_DELAY, do_delete)
        self.current_timer.start()

    def get_artist(self, name, session):
        try:
            return session.query(Artist).filter(Artist.name == name).one()
        except sqlalchemy.orm.exc.NoResultFound:
            ret = Artist(name = name)
            session.add(ret)

            return ret

    def get_album_artist(self, track, artist, session):
        has_album_artist = ('albumartist' in track)

        if has_album_artist:
            album_artist = self.get_artist(track.get('albumartist'), session)
        else:
            album_artist = self.get_artist(track.get('artist'), session)
        
        return (album_artist, has_album_artist)

    def get_album(self, artist, title, directory, session, force_solo = False):
        ret = self.get_solo_album(artist, title, session)

        if not ret and not force_solo:
            ret = self.get_va_album(artist, title, directory, session)

        if not ret:
            ret = self.make_default_album(artist, title, session)

        return ret

    def get_solo_album(self, artist, title, session):
        try:
            return (session.query(Album).filter(Album.title == title).\
                filter(Album.artist_id == artist.id).one(), artist)
        except sqlalchemy.orm.exc.NoResultFound:
            return False
        except sqlalchemy.orm.exc.MultipleResultsFound:
            cherrypy.log.error("Multiple solo albums found for '%s' (%d) - '%s'" %
                               (artist.name, artist.id, title),
                               self.LOG_TAG)
            return False

    def get_va_album(self, artist, title, directory, session):
        for match in session.query(Album).join(Track). \
                filter(Album.title == title). \
                filter(Track.directory == directory):
            va_artist = self.get_va_artist(session)
            match.artist_id = va_artist.id

            session.add(match)

            return (match, va_artist)
            
        return False
    
    def get_va_artist(self, session):
        try:
            return session.query(Artist). \
                filter(Artist.name == Config.get_va_artist()).one()
        except sqlalchemy.orm.exc.NoResultFound:
            va_artist = Artist(name = Config.get_va_artist())
            session.add(va_artist)

            return va_artist

    def make_default_album(self, artist, title, session):
        ret = Album(title = title)
        session.add(ret)
        artist.albums.append(ret)
        
        return (ret, artist)

    def get_dbtrack(self, stringid, session):
        return session.query(Track).filter(Track.stringid == stringid).one()
                
    def handle_deletion(self, filename, session):
        for f in session.query(File).filter(File.path.like(filename + '%')):
            cherrypy.log("Deleting '%s'" % (f.path), self.LOG_TAG)
            session.delete(f)

        self.delete_unused()


            

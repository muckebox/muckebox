import threading
import os.path
import time

import sqlalchemy.orm.exc

from config import Config
from db import Db
from mutabrainz.autofile import AutoFile
from models.file import File
from models.track import Track
from models.album import Album
from models.artist import Artist

class Reader(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.stop_thread = False

    def run(self):
        session = Db().get_session()
        i = 0
        start = time.clock()

        while True:
            filename = self.queue.get()
            
            if self.stop_thread:
                break

            try:
                self.handle_file(filename, session)
                session.commit()
            except:
                print "[%s] Error, skipping" % (filename)
                session.rollback()
                raise

    def stop(self):
        self.stop_thread = True
        self.queue.put(False)

    def handle_file(self, filename, session):
        if not AutoFile.is_supported(filename):
            return

        if os.path.exists(filename):
            if self.file_updated(filename, session):
                self.handle_update(filename, session)

        else:
            self.handle_deletion(filename, session)

    def file_updated(self, filename, session):
        for res in session.query(File).filter(File.path == filename):
            return res.mtime < os.path.getmtime(filename)

        return True

    def handle_update(self, filename, session):
        print "Updating [%s]" % (filename)

        try:
            fh = session.query(File).filter(File.path == filename).one()
        except sqlalchemy.orm.exc.NoResultFound:
            fh = self.handle_new(filename, session)

        self.check_tracks(fh, session)
        
    def handle_new(self, filename, session):
        fh = File(path = filename, mtime = os.path.getmtime(filename))
        session.add(fh)

        return fh

    def check_tracks(self, fh, session):
        file = AutoFile(fh.path)

        for track in file.get_tracks():
            artist = self.get_artist(track['displayartist'], session)
            (album, artist) = self.get_album(artist,
                                             track.get('album'),
                                             track.get('directory'),
                                             session)

            try:
                dbtrack = self.get_dbtrack(track['stringid'], session)
            except sqlalchemy.orm.exc.NoResultFound:
                dbtrack = Track()
                fh.tracks.append(dbtrack)
                album.tracks.append(dbtrack)
                artist.tracks.append(dbtrack)

            dbtrack.from_dict(track)

    def get_artist(self, name, session):
        try:
            return session.query(Artist).filter(Artist.name == name).one()
        except sqlalchemy.orm.exc.NoResultFound:
            ret = Artist(name = name)
            session.add(ret)

            return ret

    def get_album(self, artist, title, directory, session):
        ret = self.get_solo_album(artist, title, session)

        if not ret:
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
            session.delete(f)


            

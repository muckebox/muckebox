import glob
import mimetypes
import os.path

class Artwork(object):
    FILE_NAME_LIST = (
        'folder',
        'albumart',
        'cd'
        'cover',
        'front',
        '1'
        )

    EXTENSION_LIST = ( 'jpg', 'jpeg', 'png' )

    @classmethod
    def get_cover(cls, file_path):
        album_dir = os.path.dirname(file_path)
        file_name = cls.find_file(album_dir)

        if file_name:
            with open(file_name, 'rb') as f:
                file_data = f.read()

            print "Returned folder file '%s'" % (file_name)
            return (mimetypes.guess_type(file_name)[0], file_data)

        return False

    @classmethod
    def find_file(cls, dir):
        for filename in cls.FILE_NAME_LIST:
            for extension in cls.EXTENSION_LIST:
                for match in glob.glob(dir + "/" +
                                       cls.to_ci_pattern(filename) + "." +
                                       cls.to_ci_pattern(extension)):
                    return match

        for extension in cls.EXTENSION_LIST:
            for match in glob.glob(dir + "/*." +
                                   cls.to_ci_pattern(extension)):
                return match
            
        return False

    @classmethod
    def to_ci_pattern(cls, pattern):
        return ''.join([ '[%s%s]' % (x, x.upper()) for x in pattern ])

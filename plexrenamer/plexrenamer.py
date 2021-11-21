import argparse
import gzip
import json
import os
import shutil
import sqlite3
import sys
from unidecode import unidecode
from plexrenamer import video

import progressbar as pb

# Chars to remove from titles
del_chars = '.[]()'
extra_types = ['behindthescenes', 'deleted', 'featurette', 'interview', 'scene', 'short', 'trailer', 'other']
split_names = ['cd', 'disk', 'disc', 'dvd','part', 'pt']

class Video():
    def __init__(self, row):
        "Initialize a video from a data row"
        self.id = row[0]
        self.title = unidecode(str(filter(lambda x: x not in del_chars, row[1])))
        self.year = row[2].split('-')[0]
        self.files = [row[3]]
        self.root_path = row[4]
        
    def __str__(self):
        attrs = vars(self)
        return ', '.join("%s: %s" % item for item in attrs.items())

    def stardardized_names(self):
        return list(map(lambda x: f'{self.root_path}\{self.get_name(x)}', self.files))

    def get_name(self, file):
        _, ext = os.path.splitext(file)

        template = f"{self.title} ({self.year})/{self.title} ({self.year}){ext }"
        template += " - part%d" % (i + 1) if len(files) > 1 else ""
        template += ext
        if dest:
            dest_folder = dest
        else:
            dest_folder = os.path.dirname(old_name)

        new_name = os.path.join(dest_folder, *template.split("/"))

def find_db(plex_dir, name):
    """ Search for database file in directory """

    for root, dirs, files in os.walk(plex_dir):
        for file in files:
            if file == name:
                return os.path.join(root, file)

    return None

def build_db(plex_dir, movies={}):
    """ Build movie database from sqlite database """
    print("Analyzing") 
    dbfile = find_db(plex_dir, "com.plexapp.plugins.library.db")

    print("Plex database:", dbfile)
    db = sqlite3.connect(dbfile)

    query = """
        Select m.id, m.title, m.originally_available_at, p.file, l.root_path, ls.name, ls.agent, ls.scanner
        from media_items i
        inner join media_parts p
        on i.id = p.media_item_id 
        inner join metadata_items m
        on i.metadata_item_id = m.id
        inner join section_locations l
        on i.section_location_id = l.id
        inner join library_sections ls
        on l.library_section_id = ls.id
        where ls.scanner in ('Plex Movie')
            and m.originally_available_at is not null
        order by i.id"""

    mymovies = {}
    file_count = 0
    for row in db.execute(query):
        movie = Video(row)
        file_count += 1
        if movie.id in movies:
            movies[movie.id].files.append(movie.files[0])
        else:
            movies[movie.id] = movie

    db.close()
    
    print("%d movies found in %d files" % (len(movies), file_count))
    return movies


def build_map(movies, dest, mapping=[]):
    """ Build mapping to new names """

    if dest: 
        dest = os.path.normpath(dest)

    for title, year, files in movies.values():
        for i, old_name in enumerate(files):
            _, ext = os.path.splitext(old_name)

            template = "%s (%s)/%s (%s)" % (title, year, title, year)
            template += " - part%d" % (i + 1) if len(files) > 1 else ""
            template += ext

            if dest:
                dest_folder = dest
            else:
                dest_folder = os.path.dirname(old_name)

            new_name = os.path.join(dest_folder, *template.split("/"))
            mapping.append((old_name, new_name))

    mapping = filter(lambda x,y: x.lower() != y.lower(), mapping)
    return mapping


def copy_rename(mapping, dest, dry):
    """ Copy and rename files to destination """
    if dry:
        widgets = ['']
    else:
        widgets = [pb.Percentage(), ' ', pb.Bar(), ' ', pb.ETA()]
    pbar = pb.ProgressBar(widgets=widgets)
    for old_name, new_name in pbar(mapping):
        dp = os.path.join(dest, os.path.dirname(new_name))
        fp = os.path.join(dp, os.path.basename(new_name))

        try:
            if not os.path.exists(dp):
                if not dry:
                    os.makedirs(dp)

            if not os.path.exists(fp):
                if dry:
                    print("rename %s to %s" % (old_name,fp))
                else:
                    print("shutil.copy(old_name, fp)")

        except Exception as e:
            print(str(e))


def rename_in_place(movies, dry):
    """ Rename files in place by first renaming the directory, then renaming the file """
    if dry:
        widgets = ['']
    else:
        widgets = [pb.Percentage(), ' ', pb.Bar(), ' ', pb.ETA()]
    pbar = pb.ProgressBar(widgets=widgets)

    for movie in movies.values():
        #Split the path into a folder tokens
        #TODO: Determine if the folder should be renamed
        #TODO: Determine if the path is too long
        #TODO: Rename each file
        print(str(movie.stardardized_names()))

    #for old_name, new_name in pbar(mapping):
    #    print 'Rename %s to %s' % (old_name, new_name)

if __name__ == "x__main__":
    # Parse command-line arguments
    print(sys.version)
    parser = argparse.ArgumentParser(description='Plex-based Movie Renamer.')
    parser.add_argument('--plex', metavar='<dir>', type=str,
                        help='set directory of Plex database.')
    parser.add_argument('--dest', metavar='<dir>', type=str,
                        help='copy and rename files to directory')
    parser.add_argument('--rename', action="store_true",
                        help='rename files inline in the existing directory')
    parser.add_argument('--save', metavar='<file>', type=str,
                        help='save database of movie titles and files')
    parser.add_argument('--load', metavar='<file>', type=str,
                        help='load database of movie titles and files')
    parser.add_argument('--dry', action='store_true',
                        help='show dry run of what will happen')
    parser.set_defaults(dry=False)
    args = parser.parse_args()

    if args.plex:
        movies = build_db(args.plex)
    elif args.load:
        print("Loading metadata from " + args.load)
        movies = json.load(gzip.open(args.load))
    else:
        print("Error: Provide a Plex database or stored database.")
        sys.exit(-1)

    if args.save:
        print( "Saving metadata to " + args.save)
        json.dump(movies, gzip.open(args.save, 'w'))

    if args.dest:
        print("Building file mapping for " + args.dest)
        mapping = build_map(movies, args.dest)
        print("Copying renamed files to " + args.dest)
        copy_rename(mapping, args.dest,args.dry)
    elif args.rename:
        print("Building file mapping for inline renaming")
        rename_in_place(movies, args.dry)


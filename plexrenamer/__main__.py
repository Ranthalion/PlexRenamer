import os
import argparse
import shutil
from plexrenamer import dal
import glob

def run(db_path: str, max_depth: int, dry_run: bool):
    print(f'Searching for plex database in {db_path}')
    db = find_db(db_path, max_depth)
    if db is None:
        print('No plex database found.')
        return
    else:
        print(f'Analyzing {db}')
        videos = dal.get_videos(db)
        directories_to_delete = set()
        
        for _, v in videos.items():
            try:
                dest_directory = os.path.join(v.root_path, v.get_standard_name())
                if not os.path.exists(dest_directory):
                    print(f'create {dest_directory}')
                    os.makedirs(dest_directory)
                else:
                    print(f'{dest_directory} exists')
                    
                # Figure out the directory stuff
                for (existing_file, (standard_directory, standard_filename)) in zip(v.files, v.standardized_names()):
                    current_directory = os.path.dirname(existing_file)
                    if current_directory == dest_directory:
                        print(f'\tRename {existing_file} to {standard_filename}')
                        shutil.move(existing_file, os.path.join(dest_directory, standard_filename))
                    else: 
                        directories_to_delete.add(current_directory)
                        print(f'\tMove {existing_file} to {os.path.join(dest_directory, standard_filename)}')
                        shutil.move(existing_file, os.path.join(dest_directory, standard_filename))
                        
            except Exception as e:
                print(f'Error: {e}')

        for dir in directories_to_delete:
            if os.path.exists(dir):
                if sum(len(files) for _, _, files in os.walk(dir)) == 0:
                    print(f'delete {dir}')
                    os.rmdir(dir)
                else:
                    print(f'{dir} is not empty')


def find_db(dir: str, max_depth: int = 8 ) -> str:
    name = 'com.plexapp.plugins.library.db'
    print(f'Searching {dir}')
    for root, dirs, files in os.walk(dir):
        if root[len(dir):].count(os.sep) < max_depth:
            for file in files:
                if file == name:
                    return os.path.join(root, file)
    print(f'Max depth ({max_depth}) exceeded.  Aborting search.')
    return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Rename files and folders based on Plex data")
    parser.add_argument('--db-path', metavar='<dir>', type=str, required=True,
                        help='the folder containing the plex database')
    parser.add_argument('--max-search-depth', metavar='<depth>', type=int, default=6,
                        help='the maximum depth to search in db-path')
    parser.add_argument('--dry-run', action='store_true',
                        help='show dry run of what will happen')
    args = parser.parse_args()
    
    run(args.db_path, args.max_search_depth, args.dry_run)
    
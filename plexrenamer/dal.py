import sqlite3
from plexrenamer import video

def get_videos(database: str) -> list[video.Video]:
    print("Plex database:", database)
    db = sqlite3.connect(database)

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

    videos = {}
    file_count = 0
    for row in db.execute(query):
        item = video.Video(row)
        file_count += 1
        if item.id in videos:
            videos[item.id].files.append(item.files[0])
        else:
            videos[item.id] = item

    db.close()
    
    print("%d videos found in %d files" % (len(videos), file_count))
    return videos

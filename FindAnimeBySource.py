import os
import threading
from SearchAndWrite import search_and_write

SOURCES_PATH = './Anime By Sources'
MAX_URL_INDEX = 38000
# MAX_URL_INDEX = 200  # for testing


# Deletes existing files where we want to store our information, grabs the info from MAL, then organizes it in a human
# readable way.
def find_anime_by_source():

    # Wipe the folder of files we want to write to
    with os.scandir(SOURCES_PATH) as entries:
        for entry in entries:
            if entry.is_file() or entry.is_symlink():
                os.remove(entry.path)

    # Do the actual work of pulling info from web and logging it.
    search_and_write(MAX_URL_INDEX)

    # Filter and present the data to the viewer in a nicer fashion by fing the largest size of sections that have
    # different sized strings (i.e title length, genres, etc ) and buffer the smaller ones with whitespace
    # so columns are aligned.
    with os.scandir(SOURCES_PATH) as entries:
        for entry in entries:
            if entry.is_file():
                max_title = 0
                max_ep = 0
                max_duration = 0
                max_genre = 0

                with open(os.path.join(SOURCES_PATH, entry.name), 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                    lines.sort()

                    for line in lines:
                        line_tokens = line.split('===')
                        max_title = max(max_title, len(line_tokens[0]))
                        max_ep = max(max_ep, len(line_tokens[2]))
                        max_duration = max(max_duration, len(line_tokens[3]))
                        max_genre = max(max_genre, len(', '.join(line_tokens[4].split(','))))

                    for i in range(len(lines)):
                        line_tokens = lines[i].split('===')
                        line_tokens[0] = line_tokens[0].ljust(max_title)
                        line_tokens[1] = line_tokens[1].ljust(5)  # 'Score has len 5 while scores have len 4
                        line_tokens[2] = line_tokens[2].ljust(max_ep)
                        line_tokens[3] = line_tokens[3].ljust(max_duration)
                        line_tokens[4] = ', '.join(line_tokens[4].split(',')).ljust(max_genre)
                        lines[i] = ' - '.join(line_tokens)

                with open(os.path.join(SOURCES_PATH, entry.name), 'w', encoding='utf-8') as file:
                    file.write(' - '.join(['Title'.ljust(max_title), 'Score', 'Num Eps'.ljust(max_ep),
                                           'Duration'.ljust(max_duration), 'Genre(s)'.ljust(max_genre), 'Link']) + '\n')
                    file.writelines(lines)


if __name__ == '__main__':
    find_anime_by_source()

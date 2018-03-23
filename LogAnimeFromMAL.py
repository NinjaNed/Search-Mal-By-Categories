# Collects anime data from individual MAL Pages and sorts them into files based on Source, Month, and Date of release.

import os
import errno
from SearchAndWrite import search_and_write

SOURCE_PATH = '.\\Anime By Source'
MONTH_PATH = '.\\Anime By Month'
DAY_PATH = '.\\Anime By Day'
path_list = [SOURCE_PATH, MONTH_PATH, DAY_PATH]
MAX_URL_INDEX = 40000
# MAX_URL_INDEX = 200  # for testing


# Deletes existing files where we want to store our information, grabs the info from MAL, then organizes it in a human
# readable way.
def log_anime_from_mal():

    # Create the folder(s) for for text files to go into if it doesn't exist already
    for path in path_list:
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    # Wipe the folder of files we want to write to
    for path in path_list:
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_file() or entry.is_symlink():
                    os.remove(entry.path)

    # Do the actual work of pulling info from web and logging it.
    search_and_write(MAX_URL_INDEX)

    # Filter and present the data to the viewer in a nicer fashion by finding the largest size of sections that have
    # different sized strings (i.e title length, genres, etc ) and buffer the smaller ones with whitespace
    # so columns are aligned.
    for path in path_list:
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_file():
                    max_title = 0
                    max_year = 0
                    max_ep = 0
                    max_duration = 0
                    max_genre = 0

                    with open(os.path.join(path, entry.name), 'r', encoding='utf-8') as file:
                        lines = file.readlines()
                        lines.sort()
                        for line in lines:
                            line_tokens = line.split('===')
                            max_title = max(max_title, len(line_tokens[0]))
                            max_year = max(max_year, len(line_tokens[2]))
                            max_ep = max(max_ep, len(line_tokens[3]))
                            max_duration = max(max_duration, len(line_tokens[4]))
                            max_genre = max(max_genre, len(', '.join(line_tokens[5].split(','))))

                        for i in range(len(lines)):
                            line_tokens = lines[i].split('===')
                            line_tokens[0] = line_tokens[0].ljust(max_title)
                            line_tokens[1] = line_tokens[1].ljust(5)  # 'Score' has len=5 while scores have len=4
                            line_tokens[2] = line_tokens[2].ljust(max_year)
                            line_tokens[3] = line_tokens[3].ljust(max_ep)
                            line_tokens[4] = line_tokens[4].ljust(max_duration)
                            line_tokens[5] = ', '.join(line_tokens[5].split(',')).ljust(max_genre)
                            lines[i] = ' - '.join(line_tokens)

                    with open(os.path.join(path, entry.name), 'w', encoding='utf-8') as file:
                        file.write(' - '.join(['Title'.ljust(max_title), 'Score', 'Year'.ljust(max_year),
                                               'Num Eps'.ljust(max_ep), 'Duration'.ljust(max_duration),
                                               'Genre(s)'.ljust(max_genre), 'Link']) + '\n')
                        file.writelines(lines)


if __name__ == '__main__':
    log_anime_from_mal()

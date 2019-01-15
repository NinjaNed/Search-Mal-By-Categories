# Collects anime data from individual MAL Pages and sorts them into files based on Source, Month, and Date of release.

import os
import errno
from SearchAndWrite import search_and_write

SOURCE_PATH = os.path.join('.', 'Anime By Source')
MONTH_PATH = os.path.join('.', 'Anime By Month')
DAY_PATH = os.path.join('.', 'Anime By Day')
path_list = [SOURCE_PATH, MONTH_PATH, DAY_PATH]
MAX_URL_INDEX = 40000
# MAX_URL_INDEX = 200  # for testing

EMPTY_URL_LOG_TEMP = 'empty_mal_urls.temp'
EMPTY_URL_LOG = 'empty_mal_urls.txt'


def get_relevant_indexes():
    if os.path.isfile(EMPTY_URL_LOG):
        indexes_to_search = []
        with open(EMPTY_URL_LOG) as no_hit_file:
            indexes = no_hit_file.readlines()
        for line in indexes:
            if line.strip() and '404:' not in line:
                indexes_to_search.append(line.split()[0])

        last_index = int(indexes[-1].split()[0])
        if MAX_URL_INDEX > last_index:
            indexes_to_search += list(range(last_index + 1, MAX_URL_INDEX + 1))
        return indexes_to_search
    else:
        return range(1, MAX_URL_INDEX + 1)


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
                if (entry.is_file() and '.temp' in entry.name) or entry.is_symlink():
                    os.remove(entry.path)

    # Do the actual work of pulling
    #  info from web and logging it.
    did_work = search_and_write(get_relevant_indexes(), EMPTY_URL_LOG_TEMP)

    if did_work:
        # Filter and present the data to the viewer in a nicer fashion by finding the largest size of sections that have
        # different sized strings (i.e title length, genres, etc ) and buffer the smaller ones with whitespace
        # so columns are aligned.
        for path in path_list:
            with os.scandir(path) as entries:
                for entry in entries:
                    if entry.is_file() and '.temp' in entry.name:
                        final_file_name = entry.name.replace('.temp', '.txt')

                        with open(os.path.join(path, entry.name), encoding='utf-8') as temp_file:
                            lines = [line.strip() for line in temp_file.readlines()]

                        # if the final .txt already exists, pull it's information in to the temp file
                        try:
                            with open(os.path.join(path, final_file_name), encoding='utf-8') as main_file:
                                all_lines = main_file.readlines()
                                header = all_lines[0]
                                end_title_index = header.find('-')
                                end_score_index = header.find('-', end_title_index + 1)
                                end_year_index = header.find('-', end_score_index + 1)
                                end_num_eps_index = header.find('-', end_year_index + 1)
                                end_duration_index = header.find('-', end_num_eps_index + 1)
                                end_genres_index = header.find('-', end_duration_index + 1)

                                old_lines = all_lines[1:]
                            for old_line in old_lines:
                                if old_line.strip():  # skip any blank lines in file
                                    lines.append('==='.join([old_line[:end_title_index].strip(),
                                                             old_line[end_title_index + 1: end_score_index].strip(),
                                                             old_line[end_score_index + 1: end_year_index].strip(),
                                                             old_line[end_year_index + 1: end_num_eps_index].strip(),
                                                             old_line[
                                                             end_num_eps_index + 1: end_duration_index].strip(),
                                                             old_line[end_duration_index + 1: end_genres_index].strip(),
                                                             old_line[end_genres_index + 1:].strip()]))

                        except FileNotFoundError:
                            pass  # no old file to append to currently found lines

                        lines.sort()  # sort alphabetically

                        max_title = 0
                        max_year = 0
                        max_ep = 0
                        max_duration = 0
                        max_genre = 0
                        for line in lines:
                            line_tokens = line.split('===')
                            max_title = max(max_title, len(line_tokens[0]))
                            max_year = max(max_year, len(line_tokens[2]))
                            max_ep = max(max_ep, len(line_tokens[3]))
                            max_duration = max(max_duration, len(line_tokens[4]))
                            max_genre = max(max_genre, len(line_tokens[5]))

                        for i in range(len(lines)):
                            line_tokens = lines[i].split('===')
                            line_tokens[0] = line_tokens[0].ljust(max_title)
                            line_tokens[1] = line_tokens[1].ljust(5)  # 'Score' has len=5 while scores have len=4
                            line_tokens[2] = line_tokens[2].ljust(max_year)
                            line_tokens[3] = line_tokens[3].ljust(max_ep)
                            line_tokens[4] = line_tokens[4].ljust(max_duration)
                            line_tokens[5] = line_tokens[5].ljust(max_genre)
                            lines[i] = ' - '.join(line_tokens) + '\n'

                        with open(os.path.join(path, final_file_name), 'w', encoding='utf-8') as main_file:
                            main_file.write(' - '.join(['Title'.ljust(max_title), 'Score', 'Year'.ljust(max_year),
                                                        'Num Eps'.ljust(max_ep), 'Duration'.ljust(max_duration),
                                                        'Genre(s)'.ljust(max_genre), 'Link']) + '\n\n')
                            main_file.writelines(lines)

                        os.remove(entry.path)

        empty_index_lines_dict = {}
        # bring in old empty url log info that we know doesn't have any anime info
        try:
            with open(EMPTY_URL_LOG) as no_hit_file:
                lines = no_hit_file.readlines()
                for line in lines:
                    if '404:' in line:
                        empty_index_lines_dict[line] = None
        except FileNotFoundError:
            pass

        # update with new empty anime info as some "Too Many Requests" either find anime and don't show up or 404
        with open(EMPTY_URL_LOG_TEMP) as no_hit_file:
            lines = no_hit_file.readlines()
            for line in lines:
                if line:
                    empty_index_lines_dict[line] = None

        empty_index_lines = []
        for key in empty_index_lines_dict:
            empty_index_lines.append(key)

        empty_index_lines.sort(key=lambda x: float(x.split(' - ')[0].strip()))  # sort this numerically

        # rewrite the global empty mal url log file
        with open(EMPTY_URL_LOG, 'w') as no_hit_file:
            no_hit_file.writelines(empty_index_lines)

        os.remove(EMPTY_URL_LOG_TEMP)
    else:
        print('No indexes to search. You may publish now.')


if __name__ == '__main__':
    log_anime_from_mal()

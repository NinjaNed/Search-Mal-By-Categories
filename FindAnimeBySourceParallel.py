import os
import multiprocessing
import SearchAndWrite

SOURCES_PATH = './Anime By Sources'
NUM_PROCESSES = 4
# MAX_URL_INDEX = 38000
MAX_URL_INDEX = 200  # for testing


# Does the same thing as the find_anime_by_source() but splits up the work on different processes so they can run in
# parallel. While this does work way faster, MAL likes to time out IPs that do too many connections to it in a short
# amount of time, so may not be useful right now but could possibly be in the future if they take that cap off.
def find_anime_by_source_parallel(num_processes):
    # Wipe the folder of files we want to write to
    with os.scandir(SOURCES_PATH) as entries:
        for entry in entries:
            if entry.is_file() or entry.is_symlink():
                os.remove(entry.path)

    processes = []
    work_load = int(MAX_URL_INDEX / num_processes)
    for i in range(NUM_PROCESSES):
        if i == NUM_PROCESSES-1:
            print("Process Created: Checking indexes " + str(i*work_load) + " - " + str(MAX_URL_INDEX))
            p = multiprocessing.Process(target=SearchAndWrite.search_and_write, args=(i*work_load, MAX_URL_INDEX+1))
            p.start()
            processes.append(p)
        else:
            print("Process Created: Checking indexes " + str(i*work_load) + " - " + str((i+1)*work_load))
            p = multiprocessing.Process(target=SearchAndWrite.search_and_write, args=(i*work_load, (i+1)*work_load))
            p.start()
            processes.append(p)

    for p in processes:
        p.join()

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
    find_anime_by_source_parallel(NUM_PROCESSES)


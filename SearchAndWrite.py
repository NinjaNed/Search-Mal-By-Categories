import urllib.request
import urllib.error
import os
import errno

base_url = 'https://myanimelist.net/anime/'

# Title Name Tokens
title_token_start = '<span itemprop="name">'
title_token_end = '</span>'

# Source Tokens
source_type_set = set()
source_token_start = 'Source:</span>\\n  '
source_token_end = '\\n'

# Score Tokens
score_token_start = '"ratingValue">'
alt_score_start = 'Score:</span>\\n  <span>'
score_token_end = '</span>'

# Number of Episode Tokens
num_ep_token_start = 'Episodes:</span>\\n  '
num_ep_token_end = '\\n'

# Duration Tokens
duration_token_start = 'Duration:</span>\\n  '
duration_token_end = '\\n'

# Genres Tokens
genres_token_start = '("genres", ['
genres_token_end = ']'

# Anime Titles sometimes use ridiculous symbols ¯\_(ツ)_/¯
UTF8_mappings = {
    '\\\'': '\'', '\\xc2\\xae': '®', '\\xc2\\xb0': '°', '\\xc2\\xb2': '²', '\\xc2\\xb3': '³', '\\xc2\\xbd': '½',
    '\\xc3\\x84': 'Ä', '\\xc3\\x89': 'É', '\\xc3\\x97': '×', '\\xc3\\x9c': 'Ü', '\\xc3\\xa0': 'à', '\\xc3\\xa2': 'â',
    '\\xc3\\xa8': 'è', '\\xc3\\xa4': 'ä', '\\xc3\\xa9': 'é', '\\xc3\\xb6': 'ö', '\\xc3\\xb9': 'ù', '\\xc3\\xbc': 'ü',
    '\\xc3\\x9f': 'ß', '\\xc4\\x83': 'ă', '\\xc4\\x93': 'ē', '\\xc5\\x8d': 'ō', '\\xc5\\x92': 'Œ', '\\xc5\\xa1': 'š',
    '\\xce\\x94': 'Δ', '\\xce\\xa8': 'Ψ', '\\xce\\xbc': 'μ', '\\xcf\\x87': 'χ', '\\xe2\\x80\\x8b': '',
    '\\xe2\\x80\\x94': '—', '\\xe2\\x80\\x99': '’', '\\xe2\\x80\\x9c': '“', '\\xe2\\x80\\x9d': '”',
    '\\xe2\\x80\\xa0': '†', '\\xe2\\x84\\x83': '℃', '\\xe2\\x86\\x90': '←', '\\xe2\\x86\\x91': '↑',
    '\\xe2\\x86\\x92': '→', '\\xe2\\x88\\x9e': '∞', '\\xe2\\x89\\xa0': '≠', '\\xe2\\x90\\xa3': '␣',
    '\\xe2\\x96\\xb3': '△ ', '\\xe2\\x97\\xaf': '◯', '\\xe2\\x98\\x86': '☆', '\\xe2\\x98\\x85': '★',
    '\\xe2\\x99\\xa1': '♡', '\\xe2\\x99\\xa5': '♥', '\\xe2\\x99\\xaa': '♪', '\\xe2\\x99\\x80': '♀',
    '\\xe2\\x99\\x82': '♂', '\\xe2\\x99\\xad': '♭', '\\xe2\\xa4\\xb4': '⤴', '\\xe3\\x83\\xbb': '・',
    '\\xef\\xbc\\x8a': '＊', '\\xef\\xbf\\xa5': '￥',
}


# Takes the title string and translates all the accounted for special characters in the titles
def filter_title(t):
    for key in UTF8_mappings:
        if key in t:
            t = t.replace(key, UTF8_mappings[key])
    return t


# Takes a token and returns the substring in-between the tokens.
def page_finder(page_str, token_start, token_end):
    token_index = page_str.find(token_start) + len(token_start)
    return page_str[token_index: page_str.find(token_end, token_index)]


# Where to store the txt files of the logged information
SOURCES_PATH = './Anime By Sources'


# Takes a range of indexes to check over the MAL DB, reads the webpage, scans for important data, and writes to disk
# based on type of source material.
def search_and_write(start_index, end_index=-1):
    if end_index == -1:
        end_index = start_index
        start_index = 0

    # Create the folder for for text files to go into if it doesn't exist already
    try:
        os.makedirs(SOURCES_PATH)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    # For each page that exists. Find the relevant data and store that in the text file corresponding to the source and
    # connect each one with a === for easy splitting and filtering after all the data is logged.
    for i in range(start_index, end_index):
        try:
            url = base_url + str(i)
            web_page = urllib.request.urlopen(url)
            page_xml = str(web_page.read())

            title = page_finder(page_xml, title_token_start, title_token_end)
            source = page_finder(page_xml, source_token_start, source_token_end)
            # for some reason MAL has two ways to represent score on their pages
            if page_xml.find(score_token_start) == -1:
                score = page_finder(page_xml, alt_score_start, score_token_end)
            else:
                score = page_finder(page_xml, score_token_start, score_token_end)
            num_eps = page_finder(page_xml, num_ep_token_start, num_ep_token_end)
            ep_len = page_finder(page_xml, duration_token_start, duration_token_end)
            genres = page_finder(page_xml, genres_token_start, genres_token_end)

            # Print a small snippet of info so the user knows that the program is still running.
            print('Index: ' + str(i) + ' - ' + filter_title(title) + ' - ' + source)

            # If the file we want to write to exists, then we just want to append new data.
            # If not, then we want to create a new file to write to.
            if os.path.exists(os.path.join(SOURCES_PATH, source + '.txt')):
                append_write = 'a'  # append if already exists
            else:
                append_write = 'w'  # make a new file if not

            # Write the data, but make sure to encode using 'utf-8' otherwise special characters are represented as more
            # than one space. (e.g ä will be taken as 2 spaces since it's base value is \xc3\xa4.
            with open(os.path.join(SOURCES_PATH, source + '.txt'), append_write, encoding='utf-8') as source_file:
                source_file.write(filter_title(title) + '===' + score + '===' + num_eps + ' episode(s)' + '===' +
                                  ep_len + '===' + genres.replace('"', '') + '===' + url + '\n')

        except urllib.error.HTTPError:
            pass
        except urllib.error.URLError:
            pass

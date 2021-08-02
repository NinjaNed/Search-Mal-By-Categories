import urllib.request
import urllib.error
import os
import json

jikan_base_url = 'https://api.jikan.moe/v3/anime/'
mal_base_url = 'https://myanimelist.net/anime/'

# Anime Titles sometimes use ridiculous symbols ¯\_(ツ)_/¯
UTF8_mappings = {
    '\\\'': '\'', '&quot;': '\"', '\\xc2\\xae': '®', '\\xc2\\xb0': '°', '\\xc2\\xb2': '²', '\\xc2\\xb3': '³',
    '\\xc2\\xbd': '½', '\\xc3\\x84': 'Ä', '\\xc3\\x89': 'É', '\\xc3\\x97': '×', '\\xc3\\x9c': 'Ü', '\\xc3\\xa0': 'à',
    '\\xc3\\xa2': 'â', '\\xc3\\xa8': 'è', '\\xc3\\xa4': 'ä', '\\xc3\\xa9': 'é', '\\xc3\\xb6': 'ö', '\\xc3\\xb9': 'ù',
    '\\xc3\\xbc': 'ü', '\\xc3\\x9f': 'ß', '\\xc4\\x83': 'ă', '\\xc4\\x93': 'ē', '\\xc5\\x8d': 'ō', '\\xc5\\x92': 'Œ',
    '\\xc5\\xa1': 'š', '\\xce\\x94': 'Δ', '\\xce\\xa8': 'Ψ', '\\xce\\xbc': 'μ', '\\xcf\\x87': 'χ',
    '\\xe2\\x80\\x8b': '', '\\xe2\\x80\\x94': '—', '\\xe2\\x80\\x99': '’', '\\xe2\\x80\\x9c': '“',
    '\\xe2\\x80\\x9d': '”', '\\xe2\\x80\\xa0': '†', '\\xe2\\x84\\x83': '℃', '\\xe2\\x86\\x90': '←',
    '\\xe2\\x86\\x91': '↑', '\\xe2\\x86\\x92': '→', '\\xe2\\x88\\x9e': '∞', '\\xe2\\x89\\xa0': '≠',
    '\\xe2\\x90\\xa3': '␣', '\\xe2\\x96\\xb3': '△ ', '\\xe2\\x97\\xaf': '◯', '\\xe2\\x98\\x86': '☆',
    '\\xe2\\x98\\x85': '★', '\\xe2\\x99\\xa1': '♡', '\\xe2\\x99\\xa5': '♥', '\\xe2\\x99\\xaa': '♪',
    '\\xe2\\x99\\x80': '♀', '\\xe2\\x99\\x82': '♂', '\\xe2\\x99\\xad': '♭', '\\xe2\\xa4\\xb4': '⤴',
    '\\xe3\\x83\\xbb': '・', '\\xef\\xbc\\x8a': '＊', '\\xef\\xbf\\xa5': '￥', '&#039;': '\'', '&amp;': '&',
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
SOURCE_PATH = os.path.join('.', 'Anime By Source')
MONTH_PATH = os.path.join('.', 'Anime By Month')
DAY_PATH = os.path.join('.', 'Anime By Day')


# Takes a range of indexes to check over the MAL DB, reads the webpage, scans for important data, and writes to disk
# based on type of source material.
def search_and_write(list_indexes, index_list):
    did_work = False

    # For each page that exists. Find the relevant data and store that in the text file corresponding to the source and
    # connect each one with a === for easy splitting and filtering after all the data is logged.
    for i in list_indexes:
        try:

            jikan_url = jikan_base_url + str(i)
            mal_url = mal_base_url + str(i)

            with urllib.request.urlopen(jikan_url) as url:
                data = json.loads(url.read().decode())

            title = data['title']

            source = data['source']

            score = str(data['score'])
            len_score = len(score)
            if len_score == 1:
                score += '.00'
            elif len_score == 3:
                score += '0'
            elif len_score == 'None':
                score = 'N/A'
            elif len_score > 4:
                score = score[:4]

            duration = data['duration']

            num_eps_int = data['episodes']
            if num_eps_int:
                num_eps = str(num_eps_int) + ' episode'
                if num_eps_int > 1:
                    num_eps += 's'
            else:
                num_eps = 'Ongoing'

            genres = ''
            for genre in data['genres']:
                genre_name = genre['name']
                if genres:
                    genres += ', %s' % genre_name
                else:
                    genres += genre_name

            # finding the right date data takes some filtering to hit all the possible formats
            date = data['aired']['string']
            if date.find(' to ') != -1:
                date = date.split(' to ')[0]  # ignore the ending date
            date = date.replace(',', '')  # take out the comma so we can split by spaces
            date_items = date.split(' ')  # token possibilities are Month Day Year, Month Year, Year, Or Unknown
            month = 'Unknown'
            day = 'Unknown'
            year = 'Unknown'
            if len(date_items) == 3:
                month = date_items[0]
                day = date_items[1]
                year = date_items[2]
            elif len(date_items) == 2:
                if date_items[0] != 'Not':  # skip "Not Available"
                    month = date_items[0]
                    year = date_items[1]
            elif len(date_items) == 1 and date_items[0] != 'Unknown':
                year = date_items[0]

            # Print a small snippet of info so the user knows that the program is still running.
            print('Index: ' + str(i) + ' - ' + filter_title(title) + ' [' + source + ']')

            # Write the data, but make sure to encode using 'utf-8' otherwise special characters are represented as more
            # than one space. (e.g ä will be taken as 2 spaces since it's base value is \xc3\xa4.

            with open(os.path.join(SOURCE_PATH, source + '.temp'), 'a+', encoding='utf-8') as source_file:
                source_file.write('==='.join([filter_title(title), score, year, num_eps, duration,
                                              genres.replace('"', ''), mal_url]) + '\n')

            with open(os.path.join(MONTH_PATH, month + '.temp'), 'a+', encoding='utf-8') as month_file:
                month_file.write('==='.join([filter_title(title), score, year, num_eps, duration,
                                             genres.replace('"', ''), mal_url]) + '\n')

            with open(os.path.join(DAY_PATH, day + '.temp'), 'a+', encoding='utf-8') as day_file:
                day_file.write('==='.join([filter_title(title), score, year, num_eps, duration,
                                           genres.replace('"', ''), mal_url]) + '\n')

            with open(index_list, 'a+') as empty_urls:
                empty_urls.write(str(i) + ' - 200: OK\n')
            did_work = True

        except urllib.error.HTTPError as e:
            error_message = str(i) + ' - ' + str(e).replace('HTTP Error ', '')
            with open(index_list, 'a+') as empty_urls:
                empty_urls.write(error_message + '\n')
            print('Index: ' + error_message)
            did_work = True
        except urllib.error.URLError:
            pass
    return did_work

import urllib.request
import urllib.error


# Finds the highest valid url index that contains information. Since 404 cause HTTP Errors, first url that doesn't crash
# is the last url index. Does make the assumption that no page exists past 40000, which is true now, but possibly not in
# the future.
def find_highest_mal_url_index():
    base_url = "https://myanimelist.net/anime/"
    for i in range(45000):
        try:
            index = 40000-i
            print("i = " + str(index))
            urllib.request.urlopen(base_url + str(index))
            print("LAST MAL INDEX = " + str(index))
            break

        except urllib.error.HTTPError:
            pass
        except urllib.error.URLError:
            pass


if __name__ == '__main__':
    find_highest_mal_url_index()
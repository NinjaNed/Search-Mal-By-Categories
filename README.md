# Search-Mal-By-Categories

This project was intended to provide a list of animes that are sourced from lesser used mediums than the normal manga visual novel route. Animes that are sourced from Radio, or Card Games might be hard to find for users who don't of them beforehand. MAL doesn't have a good way to search by source, so this project was created to do that for them. 

The code is written in Python3, where it could be formatted to run in Python 2.7, but since most likely the resulting lists which are in the respository would be the same and thus created for a one time use, I didn't feel the need to have it run on 2.7 as well. Running LogAnimeFromMAL.py creates the folder for the lists to go into, then runs search_and_write() from SearchAndWrite.py, and after all the indexes have been logged it then cleans the resulting files and puts it in a easy to view format for the reader. search_and_write() from SearchAndWrite.py specifically looks up a MAL anime page by index number, and then if it doesn't 404, gets the relevant information (i.e title, score, source, number of eps, duration, and genres) and writes it to the file that corresponds to the source that anime came from (e.g Manga.txt, Book.txt, etc) and what month or day it aired. 

MAL will time you out (with a "Too many requests" message) if you try to do too many connection to its servers in a certain time period. To mitigate that, LogAnimeFromMAL is designed to be run many times preferrably hours apart to allow for fresh connections. Each run will product the content .txt files but also an empty_mal_urls.txt that keeps track of indexes that return non 200 error codes (mainly 404 - Not Found and 429 - Too many requests). Then on following runs the indexes to check for are essentially the indexes that return 429 because it will either have content or 404. After all index are accounted for it prompts you saying the lists are up to date.

But I hope the lists can help the you out. 

List Updated as of April 6th 2019

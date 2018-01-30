# Search-Mal-By-Source

This project was intended to provide a list of animes that are sourced from lesser used mediums than the normal manga visual novel route. Animes that are sourced from Radio, or Card Games might be hard to find for users who don't of them beforehand. MAL doesn't have a good way to search by source, so this project was created to do that for them. 

The code is written in Python3, where it could be formatted to run in Python 2.7, but since most likely the resulting lists which are in the respository would be the same and thus created for a one time use, I didn't feel the need to have it run on 2.7 as well. Running FindAnimeBySource.py basically creates the folder for the lists to go into, runs search_and_write() from SearchAndWrite.py, and then cleans the resulting files and puts it in a easy to view format for the reader. search_and_write specifically looks up a mal anime page by index number, and then if it doesn't 404, gets the relavent information (i.e title, score, source, number of eps, duration, and genres) and writes it to the file that corresponds to the source that anime came from. 

MAL will time you out if you try to do too many connection to its servers at once. So even though there is a parallel version of the FindAnimeBySource.py which runs faster using the multiprocess package, it's not reccomended you use it, as MAL will time out the connections and you won't get useful information at that point. Since you would need to run the program serialized, connecting to MAL for each page and being wary to not time out, the runtime is quite long. I would approximate the runtime to search all of MAL to be 4-5 hours.

But I hope the lists that are linked anyway can help the layperson out. 

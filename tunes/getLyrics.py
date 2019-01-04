
import requests
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords



artist = 'Johnny Cash'
title = "I've"
title_words = title.split()
search_title = ""
for word in title_words:
    if word.find("'") < 0:
        search_title = search_title + ' ' + word
print (search_title)
# url = 'http://www.mldb.org/search-bf?mqa=neil+diamond&mqt=cherry+cherry&mql=&mqy=&ob=1&mm=0'
url=f'http://www.mldb.org/search-bf?mqa={artist}&mqt={search_title}&mql=&mqy=&ob=1&mm=0'
print('Searching for ',url)
page = requests.get(url)
soup = BeautifulSoup(page.text, 'html.parser')
song = soup.find(class_='h')
if not song:
    print("NO SONG FOUND")
    exit()
links = song.find_all('a')

song_link = links[1].get('href')
# print(song)
# print("==")
# print(links)
# print('>>>', song_link)

song_url = f'http://www.mldb.org/{song_link}'
# print(song_url)
lyrics_page = requests.get(song_url)
soup = BeautifulSoup(lyrics_page.text, 'html.parser')

lyrics = soup.find(class_='songtext').text
# print(lyrics)

lyrics_words = set(word_tokenize(lyrics))

# print (lyrics_words)
stopwords = set(stopwords.words('english'))
# print(stopwords)
good_lyrics_words = []

for w in lyrics_words:
    if w.lower() not in stopwords:
        good_lyrics_words.append(w)

# print(good_lyrics_words)
for w in good_lyrics_words:
    print(w)


"""
pages = []
for i in range(1, 5):
    url = 'https://web.archive.org/web/20121007172955/https://www.nga.gov/collection/anZ' + str(i) + '.htm'
    pages.append(url)

for item in pages:
    page = requests.get(item)

    soup = BeautifulSoup(page.text, 'html.parser')
    last_links = soup.find(class_='AlphaNav')
    last_links.decompose()
    artist_name_list = soup.find(class_='BodyText')
    artist_name_list_items = artist_name_list.find_all('a')

    for artist_name in artist_name_list_items:
        names = artist_name.contents[0]
        links = 'https://web.archive.org' + artist_name.get('href')
        print(names)
        print(links)
"""

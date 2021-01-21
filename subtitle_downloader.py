import requests
import zipfile
import os
from bs4 import BeautifulSoup
from tqdm import tqdm
from guessit import guessit

# github.com/Ainyava/Stream
# github.com/Ainyava/SubtitleDownloader

# define some variables
SITE_URL = 'https://subf2m.co'
MOVIES_DIRECTORY = 'D:/Media/Movies'

# define a function that makes a soup object from given URL
def make_soup(url):
    r = requests.get(url).content
    return BeautifulSoup(r, 'html.parser')

# list directory of movies for movie files
movies = os.listdir(MOVIES_DIRECTORY)

# loop through each movie
for movie in movies:

    # use guessit to extract movie name
    g = guessit(movie)
    # check if movie year and title found in name
    if 'title' not in g or 'year' not in g:
        continue

    # store and print current movie information
    name = g['title']
    year = str(g['year'])
    print(name+' '+year)

    # request and create object for the movie subtitle search page
    s = make_soup(f'{SITE_URL}/subtitles/searchbytitle?query={name}+&l=')
    # found all links with title class in that page
    links = s.find_all('div', {'class': 'title'})

    # linear search for the link we want
    link = None
    for l in links:
        if year in l.text:
            link = l

    # check if link found
    if link:

        # find the URL of subtitle page
        link = link.find('a')['href']

        # make object from that page and found download link
        s = make_soup(f'{SITE_URL}{link}')
        link = s.find('a', {'class': 'download'})['href']

        # make object from URL of download page and extract subtitle zip direct link
        s = make_soup(f'{SITE_URL}{link}')
        link = s.find('div', {'class': 'download'}).find('a')['href']
        

        # Download subtitle file
        response = requests.get(f'{SITE_URL}{link}', stream=True)
        with open("subtitle.zip", "wb") as handle:
            for data in tqdm(response.iter_content()):
                handle.write(data)

        # open and extract zip file of subtitle
        with zipfile.ZipFile('subtitle.zip', 'r') as zipf:
            # list files in the zip file
            files = list(zipf.namelist())
            # loop through files and extract first srt file founded
            # also rename the file same as movie name with srt extension
            for f in files:
                if f.endswith('.srt'):
                    zipf.extract(f, './srt')
                    subname = movie[:-3]+'srt'
                    os.rename(f'./srt/{f}', f'./srt/{subname}')
                    break
        
        # merge movie with found subtitle into movies directory
        os.system(f'mkvmerge --output "./movies/{movie}" "{MOVIES_DIRECTORY}/{movie}" "./srt/{subname}"')

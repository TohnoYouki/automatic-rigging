import sys
import json
import itertools
sys.path.append('../../../utils/')
from multiprocess import multi_process
from utils import base_url, get_request
from utils import find_middle_content, find_all

def convert_name(raw_name):
    name = ''
    for x in raw_name:
        if (x >= 'a' and x <= 'z') or (x >= 'A' and x <= 'Z'):
            name += x.lower()
        elif (x >= '1' and x <= '9'):
            name += x
        else: name += ' '
    name = [x + ' ' for x in name.split(' ') if x != '']
    name = (''.join(name))[:-1]
    return name

def get_all_urls():
    content = str(get_request(base_url).content)
    find_results = find_all(str(content), '"leftnav-consoles"')
    assert(len(find_results) == 1)
    start = find_results[0]
    end = content[start:].find('div') + start
    consoles = [x + start for x in find_all(content[start:end], 'href')]
    starts = [content[x:].find('"') + x + 1 for x in consoles]
    ends = [content[x:].find('"') + x for x in starts]
    consoles = [content[starts[i]:ends[i]] for i in range(len(starts))]
    consoles = [x.split('/')[1] for x in consoles]
    characters = ['0'] + [chr(ord('A') + i) for i in range(26)]
    urls = list(itertools.product(consoles, characters))
    return [[x, x + '/' + y + '.html'] for x, y in urls]

def search_games(category, lock):
    games = []
    console, url = category
    print(console, url)
    key = 'span class="gameiconheadertext"'
    content = str(get_request(base_url + url).content)
    indexs = find_all(str(content), key)
    names = [find_middle_content(content[x:], '>', '<') for x in indexs]
    indexs = [x - content[x:0:-1].find('ferh') for x in indexs]
    htmls = [find_middle_content(content[x:], '"', '"') for x in indexs]    
    for i in range(len(names)): 
        games.append([console, htmls[i][1:], convert_name(names[i])])
    return games

def get_all_games(process_number):
    urls = get_all_urls()
    games = multi_process(search_games, urls, process_number)
    assert(len(games) == len(urls))
    games = sum([x[1] for x in games], [])
    assert(len(set([x[1] for x in games])) == len(games))
    games.sort(key = lambda x:x[1])
    return games
    
if __name__ == '__main__':
    process_number = 8
    games = get_all_games(process_number)
    with open('games.json', 'w') as file:
        result = json.dumps(games)
        file.write(result)
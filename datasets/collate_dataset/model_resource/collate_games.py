import sys
import json
import itertools
sys.path.append('../../../utils/')
from multiprocess import multi_process
from utils import base_url, get_request
from utils import find_middle_content, find_all

def get_all_console():
    content = get_request(base_url)
    find_results = find_all(str(content), '"leftnav-consoles"')
    assert(len(find_results) == 1)
    start = find_results[0]
    end = content[start:].find('div') + start
    consoles = [x + start for x in find_all(content[start:end], 'href')]
    starts = [content[x:].find('"') + x + 1 for x in consoles]
    ends = [content[x:].find('"') + x for x in starts]
    consoles = [content[starts[i]:ends[i]] for i in range(len(starts))]
    return [x.split('/')[1] for x in consoles]

def get_all_console_category(consoles):
    characters = ['0'] + [chr(ord('A') + i) for i in range(26)]
    urls = list(itertools.product(consoles, characters))
    return [[x, x + '/' + y + '.html'] for x, y in urls]

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

def search_games(category):
    games = []
    console, url = category
    print(console, url)
    key = 'span class="gameiconheadertext"'
    content = get_request(base_url + url)
    indexs = find_all(str(content), key)
    names = [find_middle_content(content[x:], '>', '<') for x in indexs]
    indexs = [x - content[x:0:-1].find('ferh') for x in indexs]
    htmls = [find_middle_content(content[x:], '"', '"') for x in indexs]    
    for i in range(len(names)): 
        games.append([console, htmls[i][1:], convert_name(names[i])])
    return games
    
if __name__ == '__main__':
    process_number = 8
    consoles = get_all_console()
    categories = get_all_console_category(consoles)
    games = multi_process(search_games, categories, process_number)
    assert(len(games) == len(categories))
    games = sum([x[1] for x in games], [])

    assert(len(set([x[1] for x in games])) == len(games))
    games.sort(key = lambda x:x[1])
    
    with open('games.json', 'w') as file:
        result = json.dumps(games)
        file.write(result)
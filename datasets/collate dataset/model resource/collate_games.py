import json
import itertools
from multiprocessing.pool import Pool
from utils import base_url, find_all, find_middle_content, get_request

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
    return [console + '/' + character + '.html' for console, character in urls]

def convert_name(raw_name):
    name = ''
    for x in raw_name:
        if (x >= 'a' and x <= 'z') or (x >= 'A' and x <= 'Z') or (x >= '1' and x <= '9'):
            name += x.lower()
        else: name += ' '
    name = [x + ' ' for x in name.split(' ') if x != '']
    name = (''.join(name))[:-1]
    return name

def get_url_all_games(urls):
    games = []
    for url in urls:
        print(url)
        key = 'span class="gameiconheadertext"'
        content = get_request(base_url + url)
        indexs = find_all(str(content), key)
        names = [find_middle_content(content[x:], '>', '<') for x in indexs]
        indexs = [x - content[x:0:-1].find('ferh') for x in indexs]
        htmls = [find_middle_content(content[x:], '"', '"') for x in indexs]
        for i in range(len(names)): 
            games.append([htmls[i][1:], convert_name(names[i])])
    return games
    
if __name__ == '__main__':
    process_number = 8
    consoles = get_all_console()
    category_urls = get_all_console_category(consoles)

    params = [category_urls[i::process_number] for i in range(process_number)]
    pool = Pool(processes = process_number)
    result = pool.map(get_url_all_games, params)
    games = sum(result, [])

    result = {}
    for html, name in games:
        console = html.split('/')[0]
        if console not in result: result[console] = set()
        result[console].add((html, name))
    for console in result:
        result[console] = [[a, b] for a, b in result[console]]
        result[console].sort(key = lambda x:x[0])
    
    with open('model_resource_games.json', 'w') as file:
        result = json.dumps(result)
        file.write(result)
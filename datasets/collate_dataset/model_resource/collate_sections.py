import os, sys, json
sys.path.append('../../../utils/')
from multiprocess import multi_process
from utils import find_all, find_middle_content
from utils import base_url, get_request, split_into_slices

def find_all_models(content, game_html):
    numbers = set()
    games_start = find_all(content, game_html + 'model/')
    for start in games_start:
        for end in range(start, len(content)):
            if content[end] == '"': break
        numbers.add(content[start:end].split('/')[-2])
    numbers = [x for x in numbers if x.isdigit()]
    assert(all([x.isdigit() for x in numbers]))
    return numbers

def get_section_models(urls, lock):
    result = []
    for url in urls:
        content = str(get_request(base_url + url).content)
        indexs = find_all(content, 'sect-name')
        sections = [find_middle_content(content[x + 15:], '"', '"') 
                    for x in indexs]
        games = {x:[] for x in sections}
        for i, start in enumerate(indexs):
            end = indexs[i + 1] if i < len(indexs) - 1 else len(content)
            games[sections[i]] = find_all_models(content[start:end], url)
        games = [[x, games[x]] for x in games]
        result.append([url, games])
    lock.acquire()
    with open('section.json') as file:
        sections = json.load(file)
    for url, games in result:
        sections[url][2] = games
    with open('section.json', 'w') as file:
        file.write(json.dumps(sections))
    lock.release()
    return [True]

def load_pending_section():
    if os.path.isfile('section.json'):
        with open('section.json') as file:
            sections = json.load(file)
    else: sections = []
    if isinstance(sections, list):
        with open('games.json') as file: 
            games = json.load(file)
        sections = {x[1]:[x[0], x[2], None] for x in games}
        with open('section.json', 'w') as file:
            file.write(json.dumps(sections))
    sections = [x for x, y in sections.items() if y[2] is None]
    return sections    

def get_all_sections(process_number):
    sections = load_pending_section()
    slices = split_into_slices(sections, 50)
    _, errors = multi_process(get_section_models, slices, process_number)
    if len(errors) > 0: return None
    sections = load_pending_section()
    if len(sections) > 0: return None
    with open('section.json') as file:
        sections = json.load(file)
    return sections

if __name__ == '__main__':
    process_number = 8
    sections = get_all_sections(process_number)
    if sections is None: print('please run again!')
    else:
        result = []
        for url, value in sections.items():
            console, name, section_games = value
            for section, games in section_games:
                result.append([console, url, name, section, games]) 
        with open('section.json', 'w') as file:
            result = json.dumps(result)
            file.write(result)
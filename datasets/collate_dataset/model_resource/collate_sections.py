import os, json
from multiprocess import multi_process
from utils import base_url, get_request
from utils import find_all, find_middle_content

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

def get_all_section_models(url):
    content = get_request(base_url + url)
    indexs = find_all(content, 'sect-name')
    sections = [find_middle_content(content[x + 15:], '"', '"') for x in indexs]
    section_games = {x:[] for x in sections}
    for j, start in enumerate(indexs):
        end = indexs[j + 1] if j < len(indexs) - 1 else len(content)
        section_games[sections[j]] = find_all_models(content[start:end], url)
    section_games = [[x, section_games[x]] for x in section_games]
    return [url, section_games]

def save_section(datas):
    with open('section.json') as file:
        sections = json.load(file)
    for index, data in datas:
        url, section_games = data
        sections[url][2] = section_games
    with open('section.json', 'w') as file:
        file.write(json.dumps(sections))

def load_section():
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
    return sections    

if __name__ == '__main__':
    process_number = 8
    sections = load_section()
    pending = [x for x, y in sections.items() if y[2] is None]
    result = multi_process(get_all_section_models, pending,
                           process_number, save = save_section)
    sections = load_section()
    if len([x for x, y in sections.items() if y[2] is None]) > 0:
        print('please run again!')
    else:
        result = []
        for url, value in sections.items():
            console, name, section_games = value
            for section, games in section_games:
                result.append([console, url, name, section, games]) 
        with open('section.json', 'w') as file:
            result = json.dumps(result)
            file.write(result)
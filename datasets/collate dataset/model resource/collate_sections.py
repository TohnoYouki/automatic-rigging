import json
from utils import load_temp_json, save_temp_json, get_request
from utils import base_url, find_all, find_middle_content, multi_process

def find_all_games(content, game_html):
    numbers = set()
    games_start = find_all(content, game_html + 'model/')
    for start in games_start:
        for end in range(start, len(content)):
            if content[end] == '"': break
        numbers.add(content[start:end].split('/')[-2])
    numbers = [x for x in numbers if x.isdigit()]
    assert(all([x.isdigit() for x in numbers]))
    return numbers

def get_all_section_models(number):
    game_htmls = load_temp_json(number)
    for i in range(len(game_htmls)):
        print(i)
        if len(game_htmls[i]) > 3: continue
        html = game_htmls[i][1]
        content = get_request(base_url + html)
        indexs = find_all(content, 'sect-name')
        sections = [find_middle_content(content[x + 15:], '"', '"') for x in indexs]
        section_games = {x:[] for x in sections}
        for j, start in enumerate(indexs):
            end = indexs[j + 1] if j < len(indexs) - 1 else len(content)
            section_games[sections[j]] = find_all_games(content[start:end], html)
        game_htmls[i].append(section_games)
        if i % 10 == 0 or i == len(game_htmls) - 1:
            save_temp_json(number, game_htmls)

if __name__ == '__main__':
    process_number = 8
    with open('games.json') as file:
        games = json.load(file)
    games = [[[x, html, name] for html, name in games[x]] for x in games]
    games = sum(games, [])
    games = multi_process(get_all_section_models, games, process_number)

    result = {}
    for console, html, name, section in games:
        if console not in result: result[console] = []
        result[console].append([html, name, section])
    for console in result:
        result[console].sort(key = lambda x:x[0])
    
    with open('sections.json', 'w') as file:
        result = json.dumps(result)
        file.write(result)
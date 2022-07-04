import os, json
from utils import base_url
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def load_data():
    if os.path.isfile('section_label.json'):
        with open('section_label.json') as file:
            models = json.load(file)
            models = {(html, number):label for html, number, label in models}
    else: models = []
    return models

def save_data(models):
    with open('section_label.json', 'w') as file:
        models = [[html, number, models[(html, number)]] for html, number in models]
        models.sort(key = lambda x:x[1])
        content = json.dumps(models)
        file.write(content)

def get_unlabel_games():
    with open('section.json') as file:
        sections = json.load(file)
    with open('models.json') as file:
        models = json.load(file)
        models = {(html, number):None if label else False 
                   for html, number, label in models}
    labeled = load_data()
    for key in models.keys():
        if key in labeled:
            models[key] = labeled[key]
    save_data(models)
    unlabel_section = [x for x in sections 
                       if any([models[(x[1], y)] is None for y in x[-1]])]
    unlabel_games = {x:{} for x in set([x[1] for x in unlabel_section])}
    for section in unlabel_section:
        unlabel_games[section[1]][section[-2]] = section[-1]
    unlabel_games = [[x, unlabel_games[x]] for x in unlabel_games]
    return unlabel_games, models

max_tab_name = 8
assert(max_tab_name > 0)

unlabel_games, models = get_unlabel_games()
options = webdriver.ChromeOptions()
options.add_argument("--ignore-certificate-error")
options.add_argument("--ignore-ssl-errors")
options.add_experimental_option('excludeSwitches', ['enable-logging'])

desired_capabilities = DesiredCapabilities.CHROME
desired_capabilities['acceptInsecureCerts'] = True
desired_capabilities['acceptSslCerts'] = True
desired_capabilities["pageLoadStrategy"] = "none"

driver = webdriver.Chrome(desired_capabilities = desired_capabilities, options = options)

handles = {}
if len(unlabel_games) > 0:
    driver.get(base_url + unlabel_games[0][0])
    handles[0] = driver.window_handles[0]

unlabel_point, preload_point = 0, 1
while unlabel_point < len(unlabel_games):

    preload_upper = min(unlabel_point + max_tab_name, len(unlabel_games))
    for i in range(preload_point, preload_upper):
        newTab = 'window.open("' + base_url + unlabel_games[i][0] + '");'
        driver.execute_script(newTab)
        handles[i] = driver.window_handles[-1]
    preload_point = preload_upper
    driver.switch_to.window(handles[unlabel_point])
    
    html, sections = unlabel_games[unlabel_point]
    labels = {}
    for section in sections:
        print(html, section, len(unlabel_games) - unlabel_point)
        command = input()
        if command == 'quit()': break
        elif command == 'all': labels[section] = 'all'
        elif command == 'none': labels[section] = 'none'
        else: labels[section] = 'wrong'
    if command == 'quit()': break
    if not all([x in labels for x in sections]): break

    for section_name in sections:
        section_models = sections[section_name]
        for x in section_models: 
            if labels[section_name] == 'all':
                models[(html, x)] = True
            elif labels[section_name] == 'none':
                models[(html, x)] = False
    save_data(models)

    del handles[unlabel_point]
    driver.close()
    unlabel_point += 1
    if unlabel_point in handles:
        driver.switch_to.window(handles[unlabel_point])

for key in handles:
    driver.switch_to.window(handles[key])
    driver.close()

unlabel_games, models = get_unlabel_games()
if len(unlabel_games) > 0: print('please run again!')
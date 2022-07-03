import os
import json
import requests
from utils import multi_process, load_temp_json, save_temp_json

save_dir = './model source zip/'
def download(number):
    models = load_temp_json(number)
    pedding = [x[1] for x in models]
    for i, info in enumerate(models):
        html, index = info
        print(i, index, len(models))
        download_url = 'https://www.models-resource.com/download/' + index + '/'
        if os.path.exists(save_dir + index + '.zip'): 
            os.remove(save_dir + index + '.zip')
        try: model = requests.get(download_url, stream = True)
        except: continue
        with open(save_dir + index + '.zip', 'wb') as file:
            for chunk in model.iter_content(chunk_size = 128):
                file.write(chunk)
        pedding.remove(index)
        save_temp_json(number, pedding)

if __name__ == '__main__':
    process_number = 8
    with open('model_source_section_label.json') as file:
        download_info = json.load(file)
    download_info = [x for x in download_info if x[2]]
    downloaded = {x.split('.')[0] for x in os.listdir(save_dir)}
    downloading = [[a, b] for a, b, c in download_info if b not in downloaded]
    multi_process(download, downloading, process_number)

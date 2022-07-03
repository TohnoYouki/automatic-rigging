import os
import json
import shutil
import zipfile
from utils import multi_process, load_temp_json, save_temp_json

formats = ['dae', 'smd']
all_zip_dir = './model resource zip/'
all_unzip_dir = './model resource unzip/'
unzip_failed_dir = './model resource unzip failed/'

def copy_format_file(src_dir, dest_dir, formats):
    for sub_dir in os.listdir(src_dir):
        sub_path = os.path.join(src_dir, sub_dir)
        if os.path.isdir(sub_path):
            copy_format_file(sub_path, dest_dir, formats)
        elif os.path.isfile(sub_path):
            file_format = sub_dir.split('.')[-1].lower()
            if file_format not in formats: continue
            shutil.copy(sub_path, os.path.join(dest_dir, sub_dir))

def unzip(zip_path, unzip_path):
    try:
        with zipfile.ZipFile(zip_path, 'r') as file:
            file.extractall(unzip_path)
    except: 
        print('unzip ', zip_path, ' error')
        return False
    return True

def extract(number):
    models = load_temp_json(number)
    pedding = [x for x in models]
    for i, model in enumerate(models):
        print(i, model)
        zip_file = all_zip_dir + model + '.zip'
        temp_dir = all_unzip_dir + 't' + model
        unzip_dir = all_unzip_dir + model
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
        if not unzip(zip_file, temp_dir): 
            if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
            continue
        if os.path.exists(unzip_dir): shutil.rmtree(unzip_dir)
        os.mkdir(unzip_dir)
        copy_format_file(temp_dir, unzip_dir, formats)
        shutil.rmtree(temp_dir)
        pedding.remove(model)
        save_temp_json(number, pedding)

if __name__ == '__main__':
    process_number = 8
    models = [x.split('.')[0] for x in os.listdir(all_zip_dir)]
    unziped = [x for x in os.listdir(all_unzip_dir)]
    models = [x for x in models if x not in unziped]
    failed = multi_process(extract, models, process_number)
    with open('model_resource_unzip_failed.json', 'w') as file:
        failed = json.dumps(failed)
        file.write(failed)
    with open('model_resource_unzip_failed.json') as file:
        failed = json.load(file)
    for number in failed:
        shutil.move(all_zip_dir + number + '.zip', unzip_failed_dir + number + '.zip')

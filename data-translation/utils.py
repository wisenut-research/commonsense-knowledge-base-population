import os
import zipfile
import pandas as pd

def chk_dir_and_mkdir(fullpath):
    dirs = [fullpath]
    while True:
        directory = os.path.dirname(dirs[0])
        if directory==dirs[0] or not directory:
            break
        if directory:
            dirs.insert(0, directory)
    for dir in dirs[:-1]:
        if not os.path.isdir(dir):
            os.mkdir(dir)


def extract_file(path, out_dir):
    with zipfile.ZipFile(path, 'r') as zf:
        zf.extractall(out_dir)


def read_data(path):
    with open(path, 'rt', encoding='utf-8') as f:
        contents = f.read().splitlines()
    contents = pd.DataFrame([[s.strip() for s in c.split('\t')] for c in contents])
    contents.columns = ['context', 'intent', 'answer']
    return contents


def read_data_raw(path):
    with open(path, 'rt', encoding='utf-8') as f:
        contents = f.read().splitlines()
    return [[s.strip() for s in c.split('\t')] for c in contents]


def save_text(path, text):
    with open(path, 'w', encoding='utf-8') as w:
        w.write(text)

import os
import zipfile
import json

def read_json(path):
    with open(path, 'r', encoding='utf-8') as r:
        return json.load(r)


def write_json(path, content):
    with open(path, 'w', encoding='utf-8') as w:
        json.dump(content, w)


def chk_dir_and_mkdir(fullpath):
    dirs = [fullpath]
    while True:
        directory = os.path.dirname(dirs[0])
        if directory==dirs[0] or not directory:
            break
        if directory:
            dirs.insert(0, directory)
    for dir in dirs[:-1]:
        if not os.path.isdir(dir):
            os.mkdir(dir)


def extract_file(path, out_dir):
    with zipfile.ZipFile(path, 'r') as zf:
        zf.extractall(out_dir)


def get_all_path(path):
    all_path = []
    for d in os.listdir(path):
        sub = os.path.join(path, d)
        if os.path.isdir(sub):
            all_path += get_all_path(sub)
        else:
            all_path.append(sub)
    return all_path

import nltk
import re
import pandas as pd
from utils import *
from tqdm import tqdm
from typing import List

nltk.download('maxent_ne_chunker')
nltk.download('punkt')
nltk.download('words')
nltk.download('averaged_perceptron_tagger')


def processing(text:str) -> str:
    text = text.strip()
    text = re.sub("[Pp]erson ?[xX]", "personx", text)
    text = re.sub("[Pp]erson ?[yY]", "persony", text)
    text = re.sub("_{3,}", "___", text)
    return text


def _cond_nonblank(textlines:List, cintent:List):
    # "HinderedBy" couldn't be exist on the head and tail sentence that has the black.
    return [[h,i,t] for h,i,t in textlines
            if not (i in cintent and h.find('___')!=-1)]


def remove_dot_blanked_head(textlines:List):
    _rm_condition = lambda h,i,t : h.find('___') != -1 or t.startswith('to ') or len(t.split()) < 3
    return [[h,i,re.sub('\.$', '', t)] if _rm_condition(h,i,t) else [h,i,t] for h,i,t in textlines]


def transform(paths:List[str], save_dir:str) -> List[str]:
    chk_dir_and_mkdir(os.path.join(save_dir, 'temp.txt'))
    for path in tqdm(paths):
        if not path.endswith('.txt'):
            continue
        with open(path, 'r', encoding='utf-8') as r:
            content = r.read().splitlines()
        content = [[t if i == 1 else processing(t) for i,t in enumerate(c.split('\t')) ] for c in content]
        content = _cond_nonblank(content, cintent=['isAfter', 'isBefore','HinderedBy'])
        content = remove_dot_blanked_head(content)
        content = pd.DataFrame(content).drop_duplicates(subset=[0,1,2])
        target = os.path.join(save_dir, os.path.basename(path))
        content.to_csv(target, sep='\t', index=False, header=None)


def chk_duplicates(paths, save_dir):
    chk_dir_and_mkdir(os.path.join(save_dir, 'temp.txt'))
    # more effective on the processed files
    memory = set()
    dup_total = 0
    for path in paths:
        with open(path, 'r', encoding='utf-8') as r:
            content = r.read().splitlines()
        non_dup = []
        for line in content:
            if line in memory:
                continue
            non_dup.append(line)
            memory.add(line)
        n_dup = len(content)-len(non_dup)
        dup_total+=n_dup
        if n_dup:
            print(f"duplicated: {n_dup} // {path}")
        target = os.path.join(save_dir, os.path.basename(path))
        with open(target, 'w', encoding='utf-8') as w:
            w.write('\n'.join(non_dup))
    print(f'Total number of duplicates:{dup_total}')


def unique_sentence_num(paths):
    n_total = 0
    for path in paths:
        if not path.endswith('.txt'):
            continue
        with open(path, 'r', encoding='utf-8') as r:
            content = r.read().splitlines()
        n_total +=len(content)
    print('total:', n_total)


if __name__=='__main__':
    paths = get_all_path("neuro_symbolic_inference")
    transform(paths, "refined")

    # 각 단계별 데이터의 문장 개수
    paths = get_all_path("neuro_symbolic_inference")
    unique_sentence_num(paths)

    paths = get_all_path("refined")
    chk_duplicates(paths, "refined_rmdup")

    paths = get_all_path("refined")
    unique_sentence_num(paths)

    translated = read_json("translated.json")

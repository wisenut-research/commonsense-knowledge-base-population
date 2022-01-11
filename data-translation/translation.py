import os.path
import re
import pandas as pd
from utils import *
from tqdm import tqdm
from typing import List, Dict
from crawler import GoogleTranslator
import argparse

parser = argparse.ArgumentParser()
parser.add_arguments("--input_dir", type=str, default="./neuro_symbolic_inference", help="")
parser.add_arguments("--input_ext", type=str, default=".txt", help="")
parser.add_arguments("--merge_maxlen", type=int, default=2000, help="")
parser.add_arguments("--merge_delimiter", type=str, default="\n[CLS]\n", help="")

parser.add_arguments("--output_dir", type=str, default="./output", help="")
parser.add_arguments("--chrome_engine", type=str, default="driver/chromedriver", help="")


def postprocessing(text:str):
    if not isinstance(text, str):
        return text
    text = text.strip()
    text = re.sub("(?<=[^다])\.", "", text)
    text = re.sub("<사람 ?x>", "personx", text)
    text = re.sub("<사람 ?y>", "persony", text)
    text = re.sub("<사람 ?>", "person", text)
    return text.strip()


def merge_texts(texts:List[str], max_len=4000, sep='//\n') -> list:
    merged = ['']
    for t in texts:
        target = t+sep
        if max_len < len(merged[-1])+len(target):
            merged[-1] = re.sub(f'{sep}$', '', merged[-1])
            merged.append('')
        merged[-1] += target
    merged[-1] = re.sub(f'{sep}$','', merged[-1])
    return merged


def translate(text:str, path_engine:str, headless:bool=True) -> str:
    with GoogleTranslator(engine=path_engine, headless=headless) as translator:
        return translator.translate(text).replace('\r', '')


def extract_unique_sentences(pathlist:List[str]):
    sentences = []
    for path in tqdm(pathlist):
        with open(path, 'r', encoding='utf-8') as r:
            sentences += [v for c in r.read().splitlines()
                          for i, v in enumerate(c.split('\t'))
                          if i in [0, 2]]
    return list(set(sentences))


def sentence2idx4files(pathlist:List[str], save_dir:str, mapping_dict:Dict):
    chk_dir_and_mkdir(os.path.join(save_dir, 'temp.txt'))
    for path in pathlist:
        with open(path, 'r', encoding='utf-8') as r:
            content = '\n'.join(['\t'.join([v if i == 1 else mapping_dict[v] for i, v in enumerate(c.split('\t'))]) for c in r.read().splitlines()])

        target = os.path.join(save_dir, os.path.basename(path))
        with open(target, 'w', encoding='utf-8') as w:
            w.write(content)


def translate_sentences(texts:List[str], chrome_engine:str, max_len=2000, sep='\n[CLS]\n',headless:bool=True) -> Dict[str, str]:
    texts = merge_texts(texts, max_len=max_len, sep=sep)
    src_tar = {}
    for text in texts:
        translated = translate(text, chrome_engine=chrome_engine,headless=headless)
        sources, targets = text.split(sep), translated.split(sep.strip())
        if len(sources) != len(targets):
            targets = [translate(origin) for origin in sources]
        src_tar.update({s:t for s,t in zip(sources, targets)})
    return src_tar


if __name__ == '__main__':
    args = parser.parse_args()
    paths = [p for p in get_all_path(args.input_dir) if p.endswith(args.input_ext)]

    sentences = extract_unique_sentences(paths)
    mapping_dict = {sentence: i for i, sentence in enumerate(sentences)}
    path_sentence_mapping = os.path.join(args.output_dir, 'mapping_dictionary.json')
    chk_dir_and_mkdir(path_sentence_mapping)
    write_json(path_sentence_mapping, mapping_dict)
    path_ids = os.path.join(args.output_dir, 'categorized')
    sentence2idx4files(paths, path_ids, mapping_dict)

    map_src_tar = translate_sentences(list(mapping_dict.keys()), chrome_engine=args.chrome_engine, max_len=args.merge_maxlen, sep=args.merge_delimiter)
    translated_sentences = os.path.join(args.output_dir, 'translated_sentences.json')
    write_json(translated_sentences, map_src_tar)

    trans_idx_dict = {mapping_dict[k]: v for k, v in map_src_tar.items()}

    trans_dir = os.path.join(args.output_dir, 'translations')
    chk_dir_and_mkdir(trans_dir)
    for path in get_all_path(path_ids):
        path_output = os.path.join(trans_dir, os.path.basename(path))
        if os.path.isfile(path_output):
            continue
        df = pd.read_csv(path, sep='\t', header=None)
        df[0] = df[0].apply(lambda x: postprocessing(trans_idx_dict[x]))
        df[2] = df[2].apply(lambda x: postprocessing(trans_idx_dict[x]))
        df.to_csv(path_output, encoding='utf-8', header=None, index=False)
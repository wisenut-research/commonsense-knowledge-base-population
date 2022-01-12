import os
import csv

from allennlp_models import pretrained
from tqdm import tqdm

def read_data(file_path, head_set):

	with open(file_path, "r", encoding="utf8") as f:
		data = csv.reader(f)
		for i, row in enumerate(data):

			rows = row[0].split("\t")
			if len(rows) > 3:
				head, predicate = rows[:2]
				tail = " ".join(rows[2:])
			elif len(rows) == 3:
				head, predicate, tail = rows

			if "PersonX" in head:
				# if "___" in head:
				# 	head = head.replace("___", "something")
				head_set.add(head)
	print(file_path, len(head_set))

def head_process(sentence, start, end):
	if sentence[:end].strip() == 'PersonX':
		extract_phrase = " ".join(sentence.split()[:2])
	elif sentence[start:end].strip() == "PersonX'":
		extract_phrase = " ".join(sentence[:end].split()[:-1])
	elif "PersonX's" in sentence[:end].strip():
		extract_phrase = sentence[:end][:sentence[:end].index("PersonX's")].strip()
	elif 'PersonY' in sentence[:end].strip():
		extract_phrase = sentence[:end][:sentence[:end].index('PersonY')].strip()
	elif '__' in sentence[:end].strip():
		extract_phrase = sentence[:end][:sentence[:end].index('__')].strip()
	else:
		extract_phrase = sentence[:end].strip()

	return extract_phrase

def read_heads(head_data_path):
	input_sentences = []
	with open(head_data_path, "r") as head_reader:
		for head in head_reader:
			input_sentences.append({"sentence": head.strip()})
		print(f"Number of sentences: {len(input_sentences)}")

	return input_sentences

def parse_sentence(input_sentences):
	batch_size = 100
	num_batch = (len(input_sentences) // batch_size) + 1

	head_set = set()
	head_list = list()
	model = pretrained.load_predictor("structured-prediction-biaffine-parser")

	for i in tqdm(range(num_batch)):
		batch_sentences = input_sentences[i*batch_size:(i+1)*batch_size]
		srl_results = model.predict_batch_json(batch_sentences)
		for sentence, parsed_sent in zip(batch_sentences, srl_results):
			spans = parsed_sent['hierplane_tree']['root']['spans'][0]
			extract_phrase = head_process(sentence['sentence'], spans['start'], spans['end'])

			head_set.add(extract_phrase)
			head_list.append(extract_phrase + "\t" + sentence['sentence'])

	return head_set, head_list

def write_parsed_heads(parsed_head_path, head_list):
	with open(parsed_head_path, "w", encoding="utf-8") as writer:
		for i, head in enumerate(head_list):
			writer.write(head + "\n")

if __name__ == '__main__':

	dirname = "atomic-2020-head-extraction"
	head_set = set()

	# read_data
	read_data(os.path.join(dirname, "data/train.tsv"), head_set)
	read_data(os.path.join(dirname, "data/dev.tsv"), head_set)
	read_data(os.path.join(dirname, "data/test.tsv"), head_set)

	with open(os.path.join(dirname, "head_pool.txt"), "w") as head_writer:
		for head in list(head_set):
			head_writer.write(head + "\n")

	# dependenxy parsing
	input_sentences = read_heads(f"{dirname}/head_pool.txt")
	head_set, head_list = parse_sentence(input_sentences)

	print("전체 head 수: ", len(head_list))
	print("고유 head 수: ", len(head_set))

	write_parsed_heads(f"{dirname}/parsed_heads.txt", head_list)
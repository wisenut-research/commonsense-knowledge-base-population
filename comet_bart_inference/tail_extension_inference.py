import os
import sys
sys.path.append(os.getcwd())
import argparse
from tqdm import tqdm

import torch

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from utils.comet_utils import use_task_specific_params, trim_batch


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


class Comet:
    def __init__(self, model_path):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        task = "summarization"
        use_task_specific_params(self.model, task)
        # self.batch_size = 1
        self.decoder_start_token_id = None

    def generate(
            self,
            queries,
            decode_method="beam",
            num_generate=5,
            ):

        with torch.no_grad():
            examples = queries

            # for batch in list(chunks(examples, self.batch_size)):

            batch = self.tokenizer(examples, return_tensors="pt", truncation=True, padding="max_length").to(self.device)
            input_ids, attention_mask = trim_batch(**batch, pad_token_id=self.tokenizer.pad_token_id)

            summaries = self.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                decoder_start_token_id=self.decoder_start_token_id,
                num_beams=num_generate,
                num_return_sequences=num_generate,
                )

            dec = self.tokenizer.batch_decode(summaries, skip_special_tokens=True, clean_up_tokenization_spaces=False)

        return dec


def read_parsed_heads(file_path):
    all_heads = []
    with open(file_path, "r") as f:
        for example in f:

            row = example.replace("]", "")
            row = row.replace("[", "")
            heads = []
            for head in row.split(","):
                heads.append(head.strip()[1:-1])
            all_heads.append(heads)

    print("Head parsing done")
    print("Total number of heads: %d" % len(all_heads))

    return all_heads

event_centered = ["isAfter", "HasSubEvent", "isBefore", "HinderedBy", "Causes", "xReason", "isFilledBy"]
social_interaction = ["xNeed", "xAttr", "xEffect", "xReact", "xWant", "xIntent", "oEffect", "oReact", "oWant"]

def save_inference_result(file_path, result):
    with open(file_path, "w") as f:
        for sentence in result:
            f.write(sentence + "\n")

    # print(file_path, "save done")


def do_inference(all_heads, beam_size=10):
    # sample usage
    print("Model loading ...")
    comet = Comet("./comet-atomic_2020_BART")
    comet.model.zero_grad()
    print("Model loaded")

    #TODO: social_interaction
    for i, heads in tqdm(enumerate(all_heads)):
        # head_num (10) * relation_num (16) * num_generate (10)
        queries = []
        head_rel = []
        for head in heads:
            for rel in social_interaction:
                query = "{} {} [GEN]".format(head, rel)
                queries.append(query)
                head_rel.append(head + "\t" + rel)

            for rel in event_centered:
                query = "{} {} [GEN]".format(head, rel)
                queries.append(query)
                head_rel.append(head + "\t" + rel)

        generate_results = comet.generate(queries, decode_method="beam", num_generate=beam_size)

        result_set = set()
        result = []
        for q_i, q in enumerate(queries):
            tails = generate_results[q_i*beam_size:(q_i+1)*beam_size]
            for tail in tails:
                sentence = head_rel[q_i] + "\t" + tail.lower()

                if sentence not in result_set:
                    result.append(sentence)
                    result_set.add(sentence)

        file_path = os.path.join("tail-extension-results", "%s.txt" % str(i+1).zfill(5))
        # make files for each head
        save_inference_result(file_path, result)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description="Comet Tail Extension")
    arg_parser.add_argument("--head_file_path", dest="head_file_path", type=str, required=True,
                            help="head file path")
    arg_parser.add_argument("--beam_size", dest="beam_size", type=int, default=10, help="beam size")
    args = arg_parser.parse_args()

    # make directory for inference results
    os.makedirs("tail-extension-results", exist_ok=True)

    all_heads = read_parsed_heads(args.head_file_path)
    do_inference(all_heads, beam_size=args.beam_size)
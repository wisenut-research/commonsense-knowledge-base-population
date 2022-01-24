# Commonsense Knowledge-base Population

We populate commonsense knowledgebase(CSKB) dataset as known [ATOMIC 2020](https://allenai.org/data/atomic-2020). We're sharing it here, no proof for correctness. Use it with caution.

The Korean dataset is a translation of English data with Google Machine Translation API.

## Methods

### Target 

ATOMIC 2020 has three domains according to the defined relationship: social-interaction, physical-entity, and event-centered.

Among them, social-interaction data (consist of `{head, relation, tail}`) was selected as an extension target. 

Details of the dataset can be found in the paper of [ATOMIC 2020](https://allenai.org/data/atomic-2020). 

### Head Extension

1) For head extraction (subject and verb), simply run

```shell
$ python atomic-2020-head-extraction/head_extraction.py
```

### Tail Prediction 

1) Download pre-trained comet-bart model

2) Simply run `comet_bart_inference/tail_extension_inference.py` (arguments: `head_file_path`, `beam_size`)

```shell
$ sh comet_bart_inference/download_model.sh # download BART model
$ python comet_bart_inference/tail_extension_inference.py --head_file_path path/to/head_extension_file --beam_size 10
```

### Post-processing 

Using the following two files, the output data(triples) was cleansed and translated.

1) `data-translation/input_transform.py`: Since the relationship label determines whether there is a blank space, it is reflected and cleansed, and duplicate data is removed from each triple.
2) `data-translation/translation.py`: Translate to Korean using Google Translate API

## Results 

We extracted 186k (10 times) events (heads) of the existing data using the 'head extension'.
And using 'tail prediction', a triple of 28.9M was generated.
Finally, after performing 'post processing', it was expanded to 3.5M of data for each language.




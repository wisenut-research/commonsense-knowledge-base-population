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

2) Simply run `tail_extension_inference.py` (arguments: `head_file_path`, `beam_size`)

```shell
$ sh comet_bart_inference/download_model.sh # download BART model
$ python comet_bart_inference/tail_extension_inference.py --head_file_path path/to/head_extension_file --beam_size 10
```



### Post-processing 

TODO 

## Results 

TODO



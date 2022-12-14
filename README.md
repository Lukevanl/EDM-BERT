# EDM-BERT
EM-BERT currently uses static representations of wikipedia pages, we plan to use dynamic representations for these pages. We do this by finding the most relevant paragraph for an entity based on the query using a BM25 search model.

![EDM-Bert Promo](edm_bert.jpg)

## Setup
- Clone this repository
- Run `Code/make.sh`
- `cd Code/XML_parser/`
- Download the files with [entities](https://surfdrive.surf.nl/files/index.php/s/fT0R5czH4hmIlgw/download) and [wikipedia](http://downloads.dbpedia.org/2015-10/core-i18n/en/pages_articles_en.xml.bz2).
- Install `xml_split` using `sudo apt install xml-twig-tools`
- Remove the abstract from the tsv file ```awk -F"\t" '{print $1}' short_abstracts_en_full.tsv > entities.tsv```
- Run the script to split up the wikipedia dump and create JSON files for our Lucene index `./build_jsons.sh 5Gb wikipedia.xml entities.tsv`
- Create the Lucene index ```python -m pyserini.index -collection JsonCollection -input json -threads 20 -index "full_wiki_dump/" -storeDocvectors -storePositions -storeRaw```
- Run EDMBERT with this index ```python3 -m pygaggle.run.evaluate_document_ranker  --split dev --method seq_class_transformer --model "output/monobert-large-msmarco-finetuned_acc_batch_testmodel_acc_batch_600k_64_e6" --dataset "data/DBpedia-Entity/" --index-dir "full_wiki_dump" --task msmarco --output-file ../Runs/testrun_mostrel.tsv \
 --w2v "resources/wikipedia2vec/wikipedia-20190701/wikipedia2vec_500.pkl" --mapper "mappers/wikipedia2vec-500-cased.monobert-base-cased.linear.npy"```


# Orginal EMBERT Description

![Model architecture](ebert_diagram.png)

## About this repository

Github page with supplementary information to the paper `Entity-aware Transformers for Entity Search' by Emma Gerritse, Faegheh Hasibi and Arjen de Vries, which was accepted at SIGIR 2022, and can be accessed [here](https://arxiv.org/abs/2205.00820)

## Structure 
Structure of this github repository is as follows:
In the Runs Directory, you can find all runs in the paper, with the same name as in the paper table 2. 

In the Code directory, all code is available. All models and supplementary materials can be downloaded by running

```
cd Code/make.sh
```

Note that this will download around 40 gb of data.

We recommend running this code in an virtual environment using Python 3.7 (Using newer versions leads to conflicts with Pytorch), for example by using:

```
python3.7 -m venv venv
source venv/bin/activate
```

All Python packages can be downloaded with `pip install -r requirements.txt`, then do 
```
pip install tensorflow==2.5.0
pip install numpy==1.20.3
pip install click==7.1.1
```
to complete the install.

## Reranking

To rerank, call the following function in `Code`:

```
python -m pygaggle.run.evaluate_document_ranker  --split dev --method seq_class_transformer --model pathtomodel --dataset pathtodata --index-dir pathtoindex  --task msmarco --output-file pathtooutput --w2v pathtowikipedia2vec --mapper path2mapper
```

For example:

```
python -m pygaggle.run.evaluate_document_ranker  --split dev --method seq_class_transformer --model ../output/monobert-large-msmarco-finetuned_acc_batch_testmodel_acc_batch_600k_64_e6 --dataset ../data/DBpedia-Entity  --index-dir ../indexes/lucene-index-dbpedia_annotated_full  --task msmarco --output-file ../Runs/testrun.tsv --w2v ../resources/wikipedia2vec/wikipedia-20190701/wikipedia2vec_500.pkl --mapper ./mappers/wikipedia2vec-500-cased.monobert-base-cased.linear.npy
```


## More information 

Most of the code is based on either the [E-BERT](https://github.com/NPoe/ebert) or the [Pygaggle](https://github.com/castorini/pygaggle) repository.

To use on your own datasets, make sure to provide all documents and queries as in the pygaggle repository, but annotate the documents before the index and the queries. Annotations should come right after the mention, for example `Neil Gaiman ENTITY/Neil_Gaiman novels`. We used [REL](https://github.com/informagi/REL), but you can use entity linker as long as the part after the `ENTITY` preamble is a Wikipediapage.

An example of finetuning can be found in `Code/retraining_dbpedia_entity_folds.py`.


## Downloads

Everything needed to evaluate the model can be downloaded with the script in `Code/make.sh`
If you just want the seperate models or Lucene indexes, they can be downloaded here.

[TSV of DBpedia Entity](https://surfdrive.surf.nl/files/index.php/s/fT0R5czH4hmIlgw/download)

[TSV of DBpedia Entity Annotated](https://surfdrive.surf.nl/files/index.php/s/hjMd4zYYn3VXoRM/download)

[Lucene index for DBpedia Entity](https://surfdrive.surf.nl/files/index.php/s/K4TWcIWLHvDhrOK/download)

[Lucene index for DBpedia Entity annotated](https://surfdrive.surf.nl/files/index.php/s/ItjlwVhm8sApcZS/download)

[Wikipedia2vec embeddings](https://surfdrive.surf.nl/files/index.php/s/mOYK4gZfI3yjsZd/download)

[EMBERT finetuned on Annotated Dbpedia, all 5 folds](https://surfdrive.surf.nl/files/index.php/s/gfCY1dc5CdkbS5S/download)

[MonoBERT fintetuned on DBpedia, not annotated, all 5 folds](https://surfdrive.surf.nl/files/index.php/s/5KQIRtiKikObJDG/download)

[EMBERT fintetuned on MSMARCO (EMBERT (1st) in paper)](https://surfdrive.surf.nl/files/index.php/s/eJsvZLceqi6kPeY)



## Citation and contact

You can cite us using 

```
@inproceedings{Gerritse:2022:Entity,
author = {Gerritse, Emma and Hasibi, Faegheh and De Vries, Arjen},
booktitle = {Proc. of the 45th International ACM SIGIR Conference on Research and Development in Information Retrieval},
series = {SIGIR '22},
title = {{Entity-aware Transformers for Entity Search}},
year = {2022}
}
```

In case anything is missing, please either make an issue or send an emal to emma.gerritse@ru.nl



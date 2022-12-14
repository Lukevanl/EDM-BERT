# Extending EM-Bert with dynamic queries 
EM-Bert currently uses static representations of wikipedia pages, we plan to use dynamic representations for these pages.

## Setup
- Clone this repository
- Download the files with [entities](https://surfdrive.surf.nl/files/index.php/s/fT0R5czH4hmIlgw/download) and [wikipedia](http://downloads.dbpedia.org/2015-10/core-i18n/en/pages_articles_en.xml.bz2).
- Install `xml_split` using `sudo apt install xml-twig-tools`
- Remove the abstract from the tsv file ```awk -F"\t" '{print $1}' short_abstracts_en_full.tsv > entities.tsv```

- Run the script to split up the wikipedia dump and create JSON files for our Lucene index `./build_jsons.sh 1Gb wikipedia.xml entities.tsv`
<!-- - Run the ```XML_parser.py``` scriptto create JSON files for the Lucene index -->
- Create the Lucene index ```python -m pyserini.index -collection JsonCollection -input json -threads 20 -index "full_wiki_dump/" -storeDocvectors -storePositions -storeRaw```
- Run EMBERT with this index (and our addition to use BM25 on the new Lucene index)

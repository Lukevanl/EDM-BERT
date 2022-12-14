#!/bin/bash

if [ ! $# -eq 3 ]
then
	echo "Usage $0 <file_size> <source> <entities> "
	exit
fi 

# Split the Wikipedia File into chuncks
file_size=$1 #"1Gb"
source=$2 #"wikipedia.xml"
entities=$3 #"short_abstracts_en_full.tsv"
destination="json"

mkdir wiki-chunks
#xml_split -s $file_size -b "wiki-chunks/wiki" $source


# Run the Python Parser on these files
mkdir $destination
for file in wiki-chunks/*
do	
	echo "Running XML_Parser.py on $file"
	python3 XML_parser.py $file $entities $destination &
done
wait
echo "Finished"

#!/bin/bash

set -e

scripts_dir="$(dirname $0)"
base_dir=$scripts_dir/..
cd $base_dir 
base_dir=$(pwd)

# echo "base_dir: $base_dir"

echo "copying widoco output to static"
rm -rf $base_dir/static/sparql
mkdir $base_dir/static/sparql
cp -r $base_dir/../widoco/cello.html/doc $base_dir/static/sparql/

# clean useless files
cd $base_dir/static/sparql
rm doc/index-en.html.ori doc/index-en.htmlbak doc/webvowl/data/ontology.json.ori


# rm -rf $base_dir/sparql_pages/*
# mkdir -p $base_dir/sparql_pages/sparql

# cp -r $base_dir/../widoco/cello.html/doc $base_dir/sparql_pages/sparql
# cd $base_dir/sparql_pages/sparql

# clean widoco directories
# rm doc/index-en.html.ori doc/index-en.htmlbak doc/webvowl/data/ontology.json.ori

# # copy everything in api static directory
# echo "copying to static"
# cd $base_dir
# rm -rf ./static/sparql
# cp -r sparql_pages/sparql ./static/

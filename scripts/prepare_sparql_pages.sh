#!/bin/bash

scripts_dir="$(dirname $0)"
base_dir=$scripts_dir/..
cd $base_dir
base_dir=$(pwd)

# echo "base_dir: $base_dir"

rm -rf $base_dir/sparql_pages/*
mkdir -p $base_dir/sparql_pages/sparql

mv $base_dir/tmp-sparql-editor.html $base_dir/sparql_pages/sparql/sparql-editor.html
mv $base_dir/tmp-resolver-examples.html $base_dir/sparql_pages/sparql/resolver-examples.html

cp -r $base_dir/../widoco/cello.html/doc $base_dir/sparql_pages/sparql
cd $base_dir/sparql_pages/sparql

# clean widoco directories
rm doc/index-en.html.ori doc/index-en.htmlbak doc/webvowl/data/ontology.json.ori

# store result in a gz file
tar cvzf sparql_pages.tar.gz .
mv sparql_pages.tar.gz ../..

# copy everything in api static directory
echo "copying to static"
cd $base_dir
rm -rf ./static/sparql
cp -r sparql_pages/sparql ./static/

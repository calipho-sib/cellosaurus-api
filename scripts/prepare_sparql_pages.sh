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

echo "clean useless files"
cd $base_dir/static/sparql
rm doc/index-en.html.ori doc/webvowl/data/ontology.json.ori

echo "copying rdf_data to static"
cd $base_dir
tar cvzf cellosaurus_ttl.tar.gz rdf_data/data_*.ttl rdf_data/ontology.ttl rdf_data/void-cello.ttl rdf_data/queries.ttl
mkdir -p $base_dir/static/downloads
rm -f $base_dir/static/downloads/cellosaurus_ttl.tar.gz
mv cellosaurus_ttl.tar.gz static/downloads/

rm -f $base_dir/static/downloads/materialized*
cp rdf_data/materialized* static/downloads/


echo "done"



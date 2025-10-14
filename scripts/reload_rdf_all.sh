#!/bin/bash

set -e

scripts_dir="$(dirname $0)"
base_dir=$scripts_dir/..

# script to be run after task
#    $ python cellapi_builder.py RDF
# from cellapi base directory 

echo "clearing virtuoso triple store...."
$base_dir/sparql_service.sh clear

echo "reloading rdf data files"
$scripts_dir/load_ttl_files.sh data no_checkpoint

echo "reloading rdf ontology file"
$scripts_dir/load_ttl_files.sh onto no_checkpoint

echo "reloading rdf queries file"
$scripts_dir/load_ttl_files.sh queries no_checkpoint

echo "reloading rdf void file"
$scripts_dir/load_ttl_files.sh void no_checkpoint

echo "performing checkpoint and restarting virtuoso triple store...."
$base_dir/sparql_service.sh restart

echo "done"

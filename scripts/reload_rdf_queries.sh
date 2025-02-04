#!/bin/bash

scripts_dir="$(dirname $0)"
base_dir=$scripts_dir/..

# script to be run after task
#    $ python cellapi_builder.py ONTO
# from cellapi base directory 

echo "reloading rdf queries file"
$scripts_dir/load_ttl_files.sh queries no_checkout

#echo "preforming checkpoint and restarting virtuoso triple store...."
# $base_dir/sparql_service.sh restart

echo "done"

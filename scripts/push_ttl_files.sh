#!/bin/bash

set -e

scripts_dir="$(dirname $0)"
base_dir=$scripts_dir/..
cd $base_dir 
base_dir=$(pwd)
release_number=$1

if [ "$1" == "" ]; then
    echo "Error, usage is: push_ttl_files.sh <release_number>"
    exit 1
fi


ttl_dir=$base_dir/static/downloads
rel_dir=/share/sib/calipho/calipho/cellosaurus/release_${release_number}/

echo "base_dir........: $base_dir"
echo "release_number..: $release_number"
echo "ttl_dir.........: $ttl_dir"
echo "rel_dir.........: $rel_dir"

echo "copying downloadable ttl files to cellosaurus release directory"

cp $ttl_dir/* $rel_dir

echo "done"



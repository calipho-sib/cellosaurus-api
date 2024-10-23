#!/bin/bash

scripts_dir="$(dirname $0)"
base_dir=$scripts_dir/..

# echo "base_dir: $base_dir"

rm -rf $base_dir/sparql_pages/*
mkdir -p $base_dir/sparql_pages/sparql

mv $base_dir/tmp_index.html $base_dir/sparql_pages/sparql/index.html
mv $base_dir/tmp_resolver-examples.html $base_dir/sparql_pages/sparql/resolver-examples.html

cp -r $base_dir/../widoco/cello.html/doc $base_dir/sparql_pages/sparql
cd $base_dir/sparql_pages/sparql
tar cvzf sparql_pages.tar.gz .
mv sparql_pages.tar.gz ../..

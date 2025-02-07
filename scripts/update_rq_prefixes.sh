#!/bin/bash

set -e

scripts_dir="$(dirname $0)"
base_dir=$scripts_dir/..

cd $base_dir

python sparql_client.py prefixes > prefixes.tmp
queries=$(ls -1 sparql/*.rq)
for qfile in $queries; do
  echo "updating file sparql/$qfile"
  cp prefixes.tmp $qfile.new
  grep -v PREFIX $qfile >> $qfile.new
  rm $qfile
  mv $qfile.new $qfile
done
rm prefixes.tmp




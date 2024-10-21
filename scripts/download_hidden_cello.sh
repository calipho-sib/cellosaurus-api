#!/bin/bash

scripts_dir="$(dirname $0)"
base_dir=$scripts_dir/..

files="cellosaurus_species.csv celloparser.cv cellosaurus.txt cellosaurus_refs.txt cellosaurus_xrefs.txt cellosaurus.xml cellosaurus.xsd"
target_dir=$base_dir/data_in.downloaded
rm -rf $target_dir
mkdir $target_dir
for f in $files; do
  curl https://download.nextprot.org/pub/.pam/${f}.gz > ${target_dir}/${f}.gz
  gunzip ${target_dir}/${f}.gz
done



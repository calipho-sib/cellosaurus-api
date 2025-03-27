#!/bin/bash

scripts_dir="$(dirname $0)"
base_dir=$scripts_dir/..

trg_dir=$base_dir/data_in

files="cellosaurus.txt cellosaurus_refs.txt cellosaurus_xrefs.txt cellosaurus.xml cellosaurus.xsd \
cellosaurus_species.cv celloparser.cv cellosaurus_anatomy.cv cellosaurus_institutions.cv cellosaurus_journals.cv cellosaurus_omics.cv"

for f in $files; do
  echo "copying $trg_dir/$f to $trg_dir/$f.saved"
  cp $trg_dir/$f $trg_dir/$f.saved
done

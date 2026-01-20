#!/bin/bash

scripts_dir="$(dirname $0)"
base_dir=$scripts_dir/..

release_number=$1
no_xml=$2

echo "release_number: $release__number"

# directory with clone of https://gitlab.sib.swiss/calipho/cellodata
draft_dir="/home/pmichel/work/cellodata"

if [ "$release_number" == "draft" ]; then
  src_dir=${draft_dir}
else
  src_dir="${draft_dir}/release_${release_number}"
fi

echo "draft_dir: $draft_dir"
echo "src_dir  : $src_dir"

trg_dir=$base_dir/data_in
mkdir -p $trg_dir

# either in draft or release directory
# Note: we assume cellosaurus.xsd file is in $trg_dir (normally as a symlink) 
if [ "$no_xml" == "no-xml" ]; then
  files="cellosaurus.txt cellosaurus_refs.txt cellosaurus_xrefs.txt"
else
  files="cellosaurus.txt cellosaurus_refs.txt cellosaurus_xrefs.txt cellosaurus.xml"
fi

for f in $files; do
  echo "retrieving $src_dir/$f"
  scp $src_dir/$f $trg_dir/$f
done

# always in draft directory
files="cellosaurus_species.cv celloparser.cv cellosaurus_anatomy.cv cellosaurus_institutions.cv cellosaurus_journals.cv cellosaurus_omics.cv cellosaurus_countries.cv"
for f in $files; do
  echo "retrieving $draft_dir/$f"
  scp $draft_dir/$f $trg_dir/$f
done

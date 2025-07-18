#!/bin/bash

scripts_dir="$(dirname $0)"
base_dir=$scripts_dir/..

release_number=$1
no_xml=$2

echo "release_number: $release__number"

# kant is not available any more
# draft_dir="npteam@kant:/share/sib/calipho/calipho/cellosaurus"
draft_dir="/share/sib/calipho/calipho/cellosaurus"

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
if [ "$no_xml" == "no-xml" ]; then
  files="cellosaurus.txt cellosaurus_refs.txt cellosaurus_xrefs.txt cellosaurus.xsd"
else
  files="cellosaurus.txt cellosaurus_refs.txt cellosaurus_xrefs.txt cellosaurus.xml cellosaurus.xsd"
fi

for f in $files; do
  echo "retrieving $src_dir/$f"
  scp $src_dir/$f $trg_dir/$f
done

# only in draft directory
files="cellosaurus_species.cv celloparser.cv cellosaurus_anatomy.cv cellosaurus_institutions.cv cellosaurus_journals.cv cellosaurus_omics.cv cellosaurus_countries.cv"
for f in $files; do
  echo "retrieving $draft_dir/$f"
  scp $draft_dir/$f $trg_dir/$f
done

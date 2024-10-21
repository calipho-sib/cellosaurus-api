#!/bin/bash

scripts_dir="$(dirname $0)"
base_dir=$scripts_dir/..

if [ "$1" == "" ]; then
	echo ""
	echo "usage: $0 <src_dir> <trg_host>"
	echo ""
	exit 1
fi
if [ "$2" == "" ]; then
	echo ""
	echo "usage: $0 <src_dir> <trg_host>"
	echo ""
	exit 1
fi

src_dir=$1
trg_host=$2
trg_dir=${trg_host}:/work/cellapi/
archive_name=${src_dir}.tar.gz
files="$src_dir/*"

if [ "$src_dir" == "data_in" ]; then
  files="$src_dir/cellosaurus_species.cv $src_dir/celloparser.cv  $src_dir/site_mapping_to_cl_uberon $src_dir/institution_list"
  files="$files $src_dir/cellosaurus.txt $src_dir/cellosaurus_refs.txt $files $src_dir/cellosaurus_xrefs.txt"
  files="$files $src_dir/cellosaurus.xml $src_dir/cellosaurus.xsd"
fi

echo "building archive with content of $src_dir"
cd $base_dir
tar cvzf $archive_name $files
echo "pushing archive $archive_name to $trg_host:$trg_dir"
scp $archive_name $trg_dir/
echo "done"



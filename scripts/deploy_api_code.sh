#!/bin/bash

scripts_dir="$(dirname $0)"
base_dir=$scripts_dir/..

target_host=$1
target_dir=$2
if [ "$target_dir" == "" ]; then
  target_dir="/work/cellapi"
fi
echo "target_host : $target_host"
echo "target_dir  : $target_dir"

cd $base_dir
tar cvzf cellapi.tar.gz *.sh *.py *.html fields_def.txt ./html.templates/* ./static/* ./configs/*  ./etc/* ./scripts/* ./solr_config/*
ssh $target_host "mkdir -p $target_dir"
scp cellapi.tar.gz $target_host:$target_dir/


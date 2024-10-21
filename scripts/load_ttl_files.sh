#!/bin/bash

scripts_dir="$(dirname $0)"
base_dir=$scripts_dir/..

echo "base_dir: $base_dir"
conf_file="${base_dir}/$(hostname).config"
if [ ! -f "$conf_file" ]; then
  echo Cannot find config file: $conf_file
  echo Trying to read default.config file
  conf_file="default.config"
  if [ ! -f "$conf_file" ]; then
    echo Error: cannot find config file: $conf_file
    exit 1
  fi
fi
source $conf_file

virt_base=$CELLAPI_VIRT_ROOT_PATH
virt_ini=$CELLAPI_VIRT_INI_FILE
sparql_srv=$CELLAPI_SPARQL_URL

echo ""
echo "conf_file  : $conf_file"
echo "virt base  : $virt_base"
echo "virt ini   : $virt_ini"
echo "sparql srv : $sparql_srv"
echo ""

# input_dir must be set here as declared in the virtuoso ini file !!!
input_dir=../input

# absolute path to virtuoso isql utility
isql=$virt_base/bin/isql

# prefix of files to be loaded
prefix=$1

# setup of virtuoso: add predefined prefixes and allow query federation
if [ "$prefix" == "data" ]; then
  echo "$(date) - INFO setup of virtuoso prefixes and allow federated queries"
  $isql 1111 dba dba $scripts_dir/virtuoso_setup.sql
fi

# reset load list and display it
echo "$(date) - INFO Telling virtuoso which files need to be loaded"
$isql 1111 dba dba "EXEC=delete from DB.DBA.load_list;"
$isql 1111 dba dba "EXEC=ld_dir ('${input_dir}', '${prefix}*.ttl', 'https://www.cellosaurus.org/rdf/graphs/main') ;"
$isql 1111 dba dba "EXEC=select * from DB.DBA.load_list;"

# run N processes to load the ttl files
max_proc=2

echo "$(date) - INFO loading declared gz files with $max_proc process(es)"
for ((i=1; i<=max_proc; i++)); do
  $isql 1111 dba dba "EXEC=rdf_loader_run();" &
done
wait

error_cnt=$($isql 1111 dba dba exec="select 'errcnt:', count(*) from db.dba.load_list where ll_error is not null"  | grep errcnt| grep errcnt | tr -d ' ' | cut -d':' -f2)
if [ "$error_cnt" != "0" ]; then
    echo "$(date) - ERROR Problem while loading files"; 
    $isql 1111 dba dba "EXEC=select * from DB.DBA.load_list where ll_error is not null;"
    exit 7
fi


# run a checkout
if [ "$2" == "no_checkout" ]; then
  echo "$(date) - INFO Skipping checkpoint after load of chunk $chunk"
else
  echo "$(date) - INFO Starting checkpoint after load of chunk $chunk"
  $isql 1111 dba dba "EXEC=checkpoint;"
  if [ "$?" != "0" ]; then 
    echo "$(date) - ERROR Problem while running checkpoint"; 
    exit 8
  fi
fi

echo "$(date) - INFO done"




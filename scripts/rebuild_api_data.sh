#!/bin/bash

scripts_dir="$(dirname $0)"
base_dir=$scripts_dir/..

# read config file to get a location for python
conf_file="$(hostname).config"
if [ ! -f "$conf_file" ]; then
  echo Error: cannot find config file: $conf_file
  exit 1
fi
source $conf_file
mypython=$CELLAPI_PYTHON

cd $base_dir

# stop the api service
./api_service.sh stop

# rebuild static files ./fields_enum.py and ./static/api-fields-help.py 
$mypython fields_utils.py

# rebuild api indexes in ./serial directory 
$mypython cellapi_builder.py BUILD

# rebuild input files for solr indexing in ./solr_data
if [ "$1" == "--no-solr" ]; then
  echo "option --no-solr: will ignore the rebuilding of solr xml data input"
else
    $mypython cellapi_builder.py SOLR
fi

./solr_service.sh restart

# delete all solr indexes
sleep 30
./solr/bin/post -c pamcore1 -d "<delete><query>*:*</query></delete>"

# rebuild solr indexes
sleep 10
./solr/bin/post -c pamcore1 solr_data/data*.xml

# reload rdf data (doit-rdf.sh instead ?)
# ./scripts/reload_rdf_all.sh

# restart api service
./api_service.sh start

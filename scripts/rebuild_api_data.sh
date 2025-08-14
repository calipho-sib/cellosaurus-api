#!/bin/bash

#
# This script can be used to automate the deployment
# of the API code and data and must be run on
# a test or prod server.
# Before running it, make sure the new code and data
# archives are have been copied and decompressed
# on the target server

# See also deploy.README which contains a description
# of the full deployment process

set -e

if [[ "$1" != "local" && "$1" != "test" && "$1" != "prod" ]]; then
  echo "Error, invalid platorm name, expected local, test or prod"
  exit 3
fi

platform=$1

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
$mypython cellapi_builder.py --platform=$platform BUILD

# rebuild input files for solr indexing in ./solr_data
if [ "$2" == "no-solr" ]; then
  echo "no-solr: will ignore the rebuilding of solr xml data input"
else
    $mypython cellapi_builder.py --platform=$platform SOLR
fi

./solr_service.sh restart

# delete all solr indexes and rebuild indexes
sleep 30
./solr/bin/post -c pamcore1 -d "<delete><query>*:*</query></delete>"
sleep 10
./solr/bin/post -c pamcore1 solr_data/data*.xml

# reload rdf data
./scripts/reload_rdf_all.sh

# restart api service
./api_service.sh start

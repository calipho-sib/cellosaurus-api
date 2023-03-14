conf_file="$(hostname).config"
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

signal=$1
echo Sending $signal signal to solr on port $CELLAPI_SOLR_PORT
./solr/bin/solr $signal -p $CELLAPI_SOLR_PORT


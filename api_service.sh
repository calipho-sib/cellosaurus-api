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

action=$1
host=$(hostname)
server=$CELLAPI_SERVER
port=$CELLAPI_PORT
scope=$CELLAPI_ROOT_PATH
mypython=$CELLAPI_PYTHON
pattern="$mypython.main.py"

echo "conf_file : $conf_file"
echo "action    : $action"
echo "host      : $host"
echo "port      : $port"
echo "scope     : $scope"
echo "mypython  : $mypython"
echo "pattern   : $pattern"

if [ "$server" == "" ]; then
  server=$host
  echo "server    : CELLAPI_SERVER undefined, set to default hostname"
fi
echo "server    : $server"

if [ "$action" == "start" ]; then
  echo "starting API"
  nohup $mypython main.py -s $server -p $port -r $scope -l False > cellapi.log 2>&1 &
  echo done

elif [ "$action" == "status" ]; then    
  pid=$(pgrep -f $pattern)
  if [ "$pid" == "" ]; then  
    echo "Stopped, found no API process running"
    exit
  else
    echo "Started, found API process running, pid $pid"
    exit
  fi

elif [ "$action" == "stop" ]; then
  echo "stopping API"
  pid=$(pgrep -f $pattern)
  if [ "$pid" == "" ]; then
    echo "Oups, found no process to kill"
    exit 3
  else
    echo killing pid $pid
    kill $pid
    echo done
  fi

else
  echo "Error: Don't know what to do, usage: $0 start|stop|status"
  exit 2	
fi


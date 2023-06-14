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
  echo "Server    : CELLAPI_SERVER undefined, set to default hostname"
fi
echo "Server    : $server"

if [ "$action" == "start" ]; then
  echo "Starting API"
  nohup $mypython main.py -s $server -p $port -r $scope -l False > cellapi.log 2>&1 &
  pid=$(pgrep -f $pattern)
  echo "Started, API process has pid $pid"
  echo done

elif [ "$action" == "status" ]; then
  pid=$(pgrep -f $pattern)
  if [ "$pid" == "" ]; then
    echo "Stopped, no API process running"
    exit
  else
    echo "Running, API process has pid $pid"
    exit
  fi

elif [ "$action" == "stop" ]; then
  echo "Stopping API"
  pid=$(pgrep -f $pattern)
  if [ "$pid" == "" ]; then
    echo "Oups, found no process to kill"
    exit 3
  else
    echo Killing pid $pid
    kill $pid
    sleep 1
    pid=$(pgrep -f $pattern)
    if [ "$pid" != "" ]; then  
      echo "Could not stop process $pid smoothly"
      echo "Will use kill -9 in 5 seconds instead..."
      sleep 5
      children=$(pgrep -P $pid)
      echo "Killing main process $pid"
      kill -9 $pid
      for p in $children; do
        echo "Killing sub process $p"
        kill -9 $p
      done
    fi
    echo Done
  fi

else
  echo "Error: Don't know what to do, usage: $0 start|stop|status"
  exit 2
fi


#!/bin/bash

this_dir=$(dirname $0)

conf_file="${this_dir}/$(hostname).config"
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


if [ "$1" == "" ]; then
    echo "ERROR, usage is: $0 start|stop|restart|status|clear"
    exit 1
fi

# this_script="$(basename $0)"
# if ! [ -e "$this_script" ]; then
#     echo "ERROR, $0 must be run from its own directory"
#     exit 2
# fi

DBA_PW=dba
DAEMON=virtuoso-t

# ISQL=/home/pmichel/work/tools/virtuoso-opensource/bin/isql
# EXE_FILE=/home/pmichel/work/tools/virtuoso-opensource/bin/virtuoso-t
# DB_DIR=/home/pmichel/work/tools/virtuoso-opensource/database
# INI_FILE=/home/pmichel/work/cellosaurus-api/private/etc/virtuoso.ini

ISQL=$virt_base/bin/isql
EXE_FILE=$virt_base/bin/virtuoso-t
DB_DIR=$virt_base/database
INI_FILE=$virt_ini

status() {
    pid=$(pgrep $DAEMON)
    if [ "$pid" == "" ]; then
        echo "$(date) virtuoso daemon is NOT running"
    else
        echo "$(date) virtuoso is running, pid is $pid"
    fi
}

stop() {
    status
    if pgrep $DAEMON; then
        echo "$(date) stopping virtuoso..."
        echo "$(date) requesting checkpoint"
        $ISQL 1111 dba $DBA_PW exec="checkpoint;"
        echo "$(date) requesting shutdown"
        $ISQL 1111 dba $DBA_PW exec="shutdown;"
        sleep 5
        echo "$(date) virtuoso stopped"
    fi
}

clear() {
    stop
    mkdir -p $DB_DIR
    rm -rf $DB_DIR/*
    start
}

start() {
    status
    if pgrep $DAEMON; then exit; fi

    echo "$(date) starting virtuoso..."
    # since locations are relative in virtuoso INI_FILE we have to cd to bin dir first
    exe_path=$(dirname $EXE_FILE)
    cd $exe_path
    echo "$EXE_FILE +wait +configfile $INI_FILE"
    $EXE_FILE +wait +configfile $INI_FILE

    echo -n "$(date) checking virtuoso listening on 1111 "
    while true; do
        echo -n "."
        isqlok=$(netstat -plant 2> /dev/null | grep 1111 | grep virtuoso | grep LISTEN | wc -l)
        if [ "$isqlok" == "1" ]; then break; fi
        sleep 5
    done
    echo " OK"

    echo -n "$(date) checking virtuoso listening on 8890 "
    while true; do
    echo -n "."
    webok=$(netstat -plant 2> /dev/null | grep 8890 | grep virtuoso  | wc -l)
    if [ "$webok" == "1" ]; then break; fi
    sleep 5
    done
    echo " OK"
    echo "$(date) virtuoso restarted on $(hostname)"   
}


action=$1

if [ "$action" == "status" ]; then
    status
fi
if [ "$action" == "start" ]; then
    start
fi
if [ "$action" == "stop" ]; then
    stop
fi
if [ "$action" == "clear" ]; then
    clear
fi
if [ "$action" == "restart" ]; then
    stop
    start
fi




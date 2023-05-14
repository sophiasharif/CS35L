#!/bin/bash

# GET PARENTS
echo PARENTS:
set `ps -u classaif -o ppid,pid,comm | grep bash`
while
    [ $1 -ne 0 ]
do
    set `ps --no-headers -o ppid,pid,comm -p $1`
    echo $*
done

# GET CHILDREN (RECURSIVELY)
echo CHILDREN:
get_child()
{
    parent_pid=$1
    child_pids=$(pgrep -P $parent_pid)

    for child in $child_pids; do
	echo `ps -p  $child -o comm=` $child
	get_child $child
    done
}

get_child `ps -u classaif -o pid,comm | grep bash`


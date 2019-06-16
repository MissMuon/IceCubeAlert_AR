#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py2-v2/icetray-start
#METAPROJECT /home/lulu/IceRec/build_V05-01-00_cluster_Marcel/
set -e
cd `dirname "$0"`
(Xvfb :99 -screen 0 800x600x24 | true)&
export DISPLAY=:99

steamshovel --batch -s Bot_Steamshovel_session.py GCD_BigBird.i3 /tmp/$1_$2

pid=`pgrep -f "Xvfb :99 -screen 0 800x600x24"`
echo "Killing process $pid of Xvfb"
kill -9 $pid

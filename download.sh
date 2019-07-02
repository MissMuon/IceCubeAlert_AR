#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py2-v3/icetray-start
#METAPROJECT /home/lulu/Software/combo/build_realtime/

#eval `/cvmfs/icecube.opensciencegrid.org/py2-v2/setup.sh`
#~/Software/combo/build_realtime/env-shell.sh
set -e

cd `dirname "$0"`
sleep 60
python Bot_I3Live.py --start $1\ $2 --end $3\ $4 --runid $5 --evtid $6 --output /tmp/$5_$6

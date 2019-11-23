#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py2-v3/icetray-start
#METAPROJECT /home/lulu/Software/combo/build_realtime/

#eval `/cvmfs/icecube.opensciencegrid.org/py2-v2/setup.sh`
#~/Software/combo/build_realtime/env-shell.sh
set -e

cd `dirname "$0"`
python Bot_GenTrack.py --runid $1 --evtid $2
fsize=`stat --printf="%s" /tmp/$1_$2_track.csv`
if [ $fsize == 0 ]; then
    echo "Zero size found"
    exit 1;
else
    exit 0;
fi


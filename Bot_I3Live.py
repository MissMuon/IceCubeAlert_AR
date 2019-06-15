#!/usr/bin/env python2
"""
Extract GCDQP frames from I3Live.
Thanks to Claudio Kopper for the first version of this script!

Note that it currently does not take the baseline GCD into account.
"""
from optparse import OptionParser

from datetime import datetime, timedelta

from icecube import icetray, dataclasses, dataio

from icecube.realtime_tools import converter, live

from Bot_GrepEvents import find_event
from Bot_ConvertCSV import gen_hololens

import sys, os
from I3Tray import I3Tray

import pandas as pd


stop  = datetime.utcnow()
#start = stop - timedelta(days=1)
start = stop - timedelta(seconds=1800) #download -1 hour events                                                                              
parser = OptionParser()
parser.add_option("-t", "--topic", action="store",
                  type="string", default="neutrino", dest="topic",
                  help="which stream") #EHE/ESTRES/HESE/neutrino
parser.add_option("-s", "--start", action="store",
                  type="string", default=start, dest="start",
                  help="start time for downloading")
parser.add_option("-e", "--end", action="store",
                  type="string", default=stop, dest="stop",
                  help="stop time for downloading")
parser.add_option("-o", "--output", action="store",
                  type="string", default="GCDQP.i3", dest="output",
                  help="output file name")
parser.add_option("-r", "--runid", action="store",
                  type="int", default="132695", dest="runid",
                  help="runid")
parser.add_option("-i", "--evtid", action="store",
                  type="int", default="7617791", dest="evtid",
                  help="eventid")

options, args = parser.parse_args()

# get full event data from I3Live
events = live.get_events_data(options.topic, options.start, options.stop)
print 'I3Live returned {:d} events.'.format(len(events))

# write frames to .i3 file
i3file = dataio.I3File(options.output+".tmp.i3.zst", 'w')
for event in events:
	frames = event['value']['data']['frames']
	for key, frame in frames.iteritems():
		i3file.push(frame)
i3file.close()
print 'Wrote', options.output+".tmp.i3.zst"

#find event by run and id
ostream = dataio.I3File(options.output, 'w')
tray = I3Tray()
tray.Add('I3Reader', filename=options.output+".tmp.i3.zst")
tray.Add(find_event, runid=options.runid, eventid = options.evtid, ostream=ostream, outcsv = options.output+".csv", Streams = [icetray.I3Frame.DAQ,icetray.I3Frame.Physics])





#tray.AddModule('TrashCan', '')                                    
tray.Execute()
tray.Finish()

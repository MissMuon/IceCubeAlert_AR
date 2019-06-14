#!/usr/bin/env python2
"""
Extract GCDQP frames from I3Live.
Thanks to Claudio Kopper for the first version of this script!

Note that it currently does not take the baseline GCD into account.
"""
from optparse import OptionParser

from datetime import datetime, timedelta

from icecube import dataio
from icecube.realtime_tools import converter, live



stop  = datetime.now()
#start = stop - timedelta(days=1)
start = stop - timedelta(seconds=3600) #download -1 hour events                                                                                                                                                     

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

options, args = parser.parse_args()

# get full event data from I3Live
events = live.get_events_data(options.topic, options.start, options.stop)
print 'I3Live returned {:d} events.'.format(len(events))

# write frames to .i3 file
i3file = dataio.I3File(options.output, 'w')
for event in events:
	frames = event['value']['data']['frames']
	for key, frame in frames.iteritems():
		i3file.push(frame)
i3file.close()
print 'Wrote', options.output

import sys, os
from icecube import icetray, dataclasses, dataio
from I3Tray import I3Tray

runid = int(sys.argv[2])
eventid = int(sys.argv[3])

infiles = sys.argv[4:]


tray = I3Tray()
ostream = dataio.I3File(sys.argv[1], 'w')

tray.Add('I3Reader', filenamelist=infiles)

def FindEvent(frame):
    if frame.Has("I3EventHeader")==0:
        header = frame["QI3EventHeader"]
    else:        
        header = frame['I3EventHeader']

    if header.run_id!=runid:
        return 0

    if header.event_id == eventid:
        ostream.push(frame)
        print "found event ",runid,eventid

    elif header.event_id > eventid:
        ostream.close()
        tray.RequestSuspension()

tray.Add(FindEvent, Streams = [icetray.I3Frame.DAQ, icetray.I3Frame.Physics])

tray.AddModule('TrashCan', '')                                                                                                                                                                                     

tray.Execute()
tray.Finish()


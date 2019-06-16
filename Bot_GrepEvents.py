from Bot_ConvertCSV import gen_hololens


def find_event(frame,runid,eventid,ostream,outcsv):
    if frame.Has("I3EventHeader")==0:
        header = frame["QI3EventHeader"]
    else:        
        header = frame['I3EventHeader']

    if header.run_id!=runid:
        return 0

    if header.event_id == eventid:
        ostream.push(frame)
        print "found event ",runid,eventid
        
        if frame.Has("InIceDSTPulses"):
            gen_hololens(frame,outcsv)

    elif header.event_id > eventid:
        ostream.close()
        #tray.RequestSuspension()



from icecube import dataclasses
import pandas as pd

def gen_hololens(frame,outcsv,inputpulses = "InIceDSTPulses"):
    time = []
    stringID = []
    om = []
    charge = []
    fobj = dataclasses.I3RecoPulseSeriesMap.from_frame(frame, inputpulses)
    ommap = fobj
    for omkey, val in ommap:
        for pulse in val:
            time.append(pulse.time)
            stringID.append(omkey.string)
            om.append(omkey.om)
            charge.append(pulse.charge)
            
    df = pd.DataFrame(data={"time":time,"string":stringID,"om":om,"charge":charge})
    df.set_index("time",inplace=True)
    df.sort_index(inplace=True)
    df.to_csv(outcsv,header=False)
    

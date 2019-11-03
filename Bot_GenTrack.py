from icecube import dataclasses
import pandas as pd
import collections

def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def gen_appendix(frame,outcsv,inputparticle = "OnlineL2_SplineMPE", jasonfile="AlertShortFollowupMsg"):
    mpe = frame[inputparticle]
    info = frame[jasonfile]    
    message = info.value
    temp = flatten(eval(message.replace("null","None")))
    df = pd.DataFrame(temp, index=[temp["event_id"]])
    #send to VM               
    df_out = pd.DataFrame(data={"runid":df.run_id.values[0],"evtid":df.event_id.values[0],"eventtime":df.eventtime.values[0],"rec_x":mpe.pos.x,"rec_y":mpe.pos.y,"rec_z":mpe.pos.z,"rec_t0":mpe.time,"rec_zen":mpe.dir.zenith,"rec_azi":mpe.dir.azimuth},index=df.run_id)
    df_out.to_csv(outcsv,header=False)
    

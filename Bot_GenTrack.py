from icecube import dataclasses, dataio, astro
import pandas as pd
import collections
from optparse import OptionParser

def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def gen_appendix(frame, outcsv, inputparticle="OnlineL2_SplineMPE",
                 jsonfile="AlertShortFollowupMsg", eventheader="I3EventHeader"):
    mpe = frame[inputparticle]
    header = frame[eventheader]
    info = frame[jsonfile]
    message = info.value
    time_mjd = header.start_time.mod_julian_day_double
    zen_rad = mpe.dir.zenith
    azi_rad = mpe.dir.azimuth
    ra_rad, dec_rad = astro.dir_to_equa(zen_rad, azi_rad, time_mjd)
    temp = flatten(eval(message.replace("null","None")))
    df = pd.DataFrame(temp, index=[temp["event_id"]])

    df_out = pd.DataFrame(data={"evtid":df.event_id.values[0],
                                "mjd":time_mjd,
                                "rec_x":mpe.pos.x,
                                "rec_y":mpe.pos.y,
                                "rec_z":mpe.pos.z,
                                "rec_t0":mpe.time,
                                "zen_rad":zen_rad,
                                "azi_rad":azi_rad,
                                "ra_rad":ra_rad,
                                "dec_rad":dec_rad},
                          index=df.run_id)
    df_out.to_csv(outcsv, header=False)
    #return df_out

parser = OptionParser()
parser.add_option("-r", "--runid", action="store",
                  type="int", default="132695", dest="runid",
                  help="runid")
parser.add_option("-i", "--evtid", action="store",
                  type="int", default="7617791", dest="evtid",
                  help="eventid")

options, args = parser.parse_args()

f = dataio.I3File("/tmp/{}_{}".format(options.runid, options.evtid))
frame = f.pop_physics()
outFilename = "/tmp/{}_{}_track.csv".format(options.runid, options.evtid)
gen_appendix(frame, outFilename)

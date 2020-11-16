from icecube import icetray, dataclasses, dataio
import pandas as pd
from optparse import OptionParser

def gen_millipede(frame, outcsv="millipede_output.csv", bestfitparticle="MillipedeStarting2ndPassParams"):
    bestfits = frame[bestfitparticle]
    x = []
    y = []
    z = []
    time = []
    energy = []
    for particle in bestfits:
        x.append(particle.pos.x)
        y.append(particle.pos.y)
        z.append(particle.pos.z)
        time.append(particle.time)
        energy.append(particle.energy)

    df_out  = pd.DataFrame({'x':x, 'y':y, 'z':z, 'time':time, 'energy':energy})
    df_out.to_csv(outcsv, header=True)
    #return df_out

parser = OptionParser()
parser.add_option("-r", "--runid", action="store",
                  type="int", default="132695", dest="runid",
                  help="runid")
parser.add_option("-i", "--evtid", action="store",
                  type="int", default="7617791", dest="evtid",
                  help="eventid")

options, args = parser.parse_args()

f = dataio.I3File("/tmp/millipede_{}_{}".format(options.runid, options.evtid))
frame = f.pop_physics()
outFilename = "/tmp/millipede_{}_{}_track.csv".format(options.runid, options.evtid)
gen_millipede(frame, outcsv = outFilename)

#!/usr/bin/env python

from __future__ import print_function
import sys
import numpy as np

import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as pl
# Though the following appears unused, it is needed for figures to accept
# the projection='3d' argument
import mpl_toolkits.mplot3d.axes3d as a3d
import mpl_toolkits.mplot3d.proj3d as p3d
from matplotlib import cm
from matplotlib import mpl
import matplotlib.gridspec as gridspec

from icecube import dataio
from icecube import icetray
from icecube import dataclasses

def basic_scatter(num, coords, colors,cextents=None):

    fig = pl.figure(figsize=(13,9))
    gs = gridspec.GridSpec(2,3,width_ratios=[6,6,1])
    coords = list(zip(*coords))
    def mkax(idx):
        ax = fig.add_subplot(gs[idx], projection='3d', adjustable='box' )
        s = ax.scatter( *coords, color=colors, edgecolor=(0,0,0,.1))
        ax.auto_scale_xyz(*[[min(i), max(i)] for i in coords])
        ax.set_axis_bgcolor('white')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        return ax
    def mkscat(idx, xc,yc):
        ax = fig.add_subplot(gs[idx])
        s = ax.scatter( coords[xc], coords[yc], color=colors, edgecolor=(0,0,0,.1),s=100)
        ax.set_axis_bgcolor('white')
        ax.set_xlabel('xyz'[xc])
        ax.set_ylabel('xyz'[yc])
    ax = mkax((1,1))
    ax = mkscat(0, 0, 1)
    #ax.view_init(0,0)
    ax = mkscat(1, 0, 2)
    #ax.view_init(90,0)
    ax = mkscat((1,0), 1, 2)
    #ax.view_init(0,90)

    ax4 = fig.add_subplot(gs[:,2], title='time (ns)')
    cb = mpl.colorbar.ColorbarBase(ax4, cmap=cm.jet, norm=mpl.colors.Normalize(*cextents))
    fig.savefig('plot/{0}r.png'.format(num))
    #pl.show()


def draw_geometry(omgeo, coords, num, tmax, colormap=None):
    colors = []
    if colormap:
        mint = tmax-5000. #min(colormap.values())
        maxt = tmax+5000. #max(colormap.values())
        colormap = dict( (key,((colormap[key]-mint)/maxt)) for key in colormap.keys() )
    for omkey, omgeo in omgeo:
        if omgeo.position.z > 1200: continue
        if(colormap):
            if omkey in colormap:
                colors.append( cm.jet(colormap[omkey]) )
            else:
                colors.append( (0,0,0,0) )
    if( colormap ):
        basic_scatter(num,coords, colors, [mint,maxt])
    else:
        basic_scatter(num,coords, colors)

def gather_geom( i3frame , geometry_key='I3Geometry'):
    geo = i3frame.Get(geometry_key)
    omgeo = geo.omgeo
    coords = []
    for omkey, g in omgeo:
        # HACK: find icetop the correct way
        if g.position.z > 1200: continue
        coords.append((g.position.x, g.position.y, g.position.z))
    return omgeo, coords


def gather_colors(i3frame, key='InIceRawData'):
    dat = i3frame.Get(key)
    colors = dict( ((key,val[0].time) for key,val in dat.items()) )
    return colors

def gather_reco_colors(i3frame, key='InIceDSTPulses'): #SplitInIcePulses
    dat = i3frame[key].apply(i3frame)  #i3frame.Get(key)
    qmax = -1
    for key,val in dat.items():
        qtot = 0
        for pulses in val:
            qtot = qtot + pulses.charge
        if qtot>qmax:
            qmax = qtot
            tmax = val[0].time
    colors = dict( ((key,val[0].time) for key,val in dat.items() if len(val) >= 2 ))
    return colors,tmax
    

def main():

    i3file = dataio.I3File(sys.argv[1])
    gframe = i3file.pop_frame(icetray.I3Frame.Geometry)
    omgeo, coords = gather_geom(gframe)

    i3file2 = dataio.I3File(sys.argv[2])
    
    for i in range(1):
        print('Frame', i)
        pframe = i3file2.pop_physics()
        colors,tmax = gather_reco_colors(pframe)
        draw_geometry(omgeo, coords,i,tmax,colors)

if __name__ == '__main__':
    main()

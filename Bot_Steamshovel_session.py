def _dumpScenario():
    from icecube.shovelart import ActivePixmapOverlay, Arrow, ArtistHandle, ArtistHandleList, ArtistKeylist, BaseLineObject, ChoiceSetting, ColorMap, ColoredObject, ConstantColorMap, ConstantFloat, ConstantQColor, ConstantTime, ConstantVec3d, Cylinder, DynamicLines, FileSetting, I3TimeColorMap, KeySetting, LinterpFunctionFloat, LinterpFunctionQColor, LinterpFunctionVec3d, OMKeySet, OverlayLine, OverlaySizeHint, OverlaySizeHints, ParticlePath, ParticlePoint, Phantom, PixmapOverlay, PyArtist, PyQColor, PyQFont, PyVariantFloat, PyVariantQColor, PyVariantTime, PyVariantVec3d, RangeSetting, Scenario, SceneGroup, SceneObject, SceneOverlay, SolidObject, Sphere, StaticLines, StepFunctionFloat, StepFunctionQColor, StepFunctionTime, StepFunctionVec3d, Text, TextOverlay, TimePoint, TimeWindow, TimeWindowColor, VariantFloat, VariantQColor, VariantTime, VariantVec3d, VariantVec3dList, Vec3dList, ZPlane, vec3d
    from icecube.icetray import OMKey
    from icecube.icetray import logging
    scenario = window.gl.scenario
    scenario.clear()
    try:
        artist = scenario.add( 'Bubbles', ['I3Geometry', 'SplitUncleanedInIcePulses', ] )
        scenario.setIsActive( artist, False )
        scenario.changeSetting( artist, 'scale', 12 )
        scenario.changeSetting( artist, 'colormap', I3TimeColorMap() )
        scenario.changeSetting( artist, 'power', 0.2 )
        scenario.changeSetting( artist, 'custom color window', '' )
        scenario.changeSetting( artist, 'log10(delay/ns)', 5 )
        scenario.changeSetting( artist, 'static', PyQColor(255,0,255,255) )
        scenario.setIsActive( artist, True )
    except StandardError as e:
        logging.log_error( e.__class__.__name__ + " occured while loading saved state of Bubbles: " + str(e) )
    except:
        logging.log_error( "Unknown error occured while loading saved state of Bubbles: " + str(e) )
    try:
        artist = scenario.add( 'Detector', ['I3Geometry', ] )
        scenario.setIsActive( artist, False )
        scenario.changeSetting( artist, 'DOM color', PyQColor(115,115,115,255) )
        scenario.changeSetting( artist, 'DOM radius', 1 )
        scenario.changeSetting( artist, 'outline width', 0.1 )
        scenario.changeSetting( artist, 'high quality DOMs', False )
        scenario.changeSetting( artist, 'string cross', True )
        scenario.changeSetting( artist, 'string color', PyQColor(115,115,115,255) )
        scenario.changeSetting( artist, 'string width', 0.1 )
        scenario.changeSetting( artist, 'hide', 2 )
        scenario.changeSetting( artist, 'DOM labels', False )
        scenario.setIsActive( artist, True )
    except StandardError as e:
        logging.log_error( e.__class__.__name__ + " occured while loading saved state of Detector: " + str(e) )
    except:
        logging.log_error( "Unknown error occured while loading saved state of Detector: " + str(e) )
    try:
        artist = scenario.add( 'Ice', [] )
        scenario.setIsActive( artist, False )
        scenario.changeSetting( artist, '3D dust', False )
        scenario.changeSetting( artist, 'Dust density', 1.5 )
        scenario.changeSetting( artist, 'Dust scatter', 0.2 )
        scenario.changeSetting( artist, 'Show bedrock', True )
        scenario.changeSetting( artist, 'Color ice', PyQColor(25,25,255,255) )
        scenario.changeSetting( artist, 'Color bedrock', PyQColor(128,102,102,255) )
        scenario.changeSetting( artist, 'Plane width', '2200 m' )
        scenario.changeSetting( artist, 'Show ice', True )
        scenario.changeSetting( artist, 'Line width', 1 )
        scenario.changeSetting( artist, 'Show dust', False )
        scenario.changeSetting( artist, 'Color dust', PyQColor(100,100,100,50) )
    except StandardError as e:
        logging.log_error( e.__class__.__name__ + " occured while loading saved state of Ice: " + str(e) )
    except:
        logging.log_error( "Unknown error occured while loading saved state of Ice: " + str(e) )
    try:
        artist = scenario.add( 'Particles', ['OnlineL2_SplineMPE', ] )
        scenario.setIsActive( artist, False )
        scenario.changeSetting( artist, 'min. energy [track]', '' )
        scenario.changeSetting( artist, 'scale', 10 )
        scenario.changeSetting( artist, 'show light fronts', False )
        scenario.changeSetting( artist, 'colormap', I3TimeColorMap() )
        scenario.changeSetting( artist, 'power', 0.15 )
        scenario.changeSetting( artist, 'color', PyQColor(243,51,51,153) )
        scenario.changeSetting( artist, 'vertex size', 0 )
        scenario.changeSetting( artist, 'labels', True )
        scenario.changeSetting( artist, 'Cherenkov cone size', 0 )
        scenario.changeSetting( artist, 'blue light fronts', True )
        scenario.changeSetting( artist, 'incoming/outgoing', True )
        scenario.changeSetting( artist, 'color by type', True )
        scenario.changeSetting( artist, 'arrow head size', 120 )
        scenario.changeSetting( artist, 'linewidth', 3 )
        scenario.changeSetting( artist, 'min. energy [cascade]', '' )
        scenario.setIsActive( artist, True )
    except StandardError as e:
        logging.log_error( e.__class__.__name__ + " occured while loading saved state of Particles: " + str(e) )
    except:
        logging.log_error( "Unknown error occured while loading saved state of Particles: " + str(e) )
    try:
        artist = scenario.add( 'TextSummary', ['I3EventHeader', ] )
        scenario.setIsActive( artist, False )
        scenario.changeSetting( artist, 'font', PyQFont.fromString('Sans Serif,9,-1,5,50,0,0,0,0,0') )
        scenario.changeSetting( artist, 'short', True )
        scenario.changeSetting( artist, 'fontsize', 9 )
        scenario.setOverlaySizeHints( artist, [OverlaySizeHint(10,10,175,49), ] )
        scenario.setIsActive( artist, True )
    except StandardError as e:
        logging.log_error( e.__class__.__name__ + " occured while loading saved state of TextSummary: " + str(e) )
    except:
        logging.log_error( "Unknown error occured while loading saved state of TextSummary: " + str(e) )
 
    window.gl.backgroundColor = PyQColor(255,255,255,255)
    window.gl.cameraLock = False
    window.gl.perspectiveView = True

#app.files.openLocalFile("./GCD_BigBird.i3")
app.files.advanceFrame(5)
#app.files.openLocalFile(options.input)
#app.files.advanceFrame(2)
_dumpScenario()
#window.gl.setCameraPivot(7.17023658752, 36.1024436951, -63.2644119263)
#window.gl.setCameraLoc(172.551498413, -1770.15148926, 500.825744629)
#window.gl.setCameraOrientation(0.995834589005, 0.0911788865924, -4.71844785466e-16)

from icecube import phys_services
from icecube import dataclasses
from icecube.icetray import I3Units
import numpy as np

cylinder = phys_services.Cylinder(1000, 625)
bestfit = frame["OnlineL2_SplineMPE"].dir
zenith = bestfit.zenith*180./3.14
azimuth = bestfit.azimuth*180./3.14
x = frame["OnlineL2_SplineMPE"].pos.x
y = frame["OnlineL2_SplineMPE"].pos.y
z = frame["OnlineL2_SplineMPE"].pos.z
adir = dataclasses.I3Direction(zenith*I3Units.deg, azimuth*I3Units.deg)
vtx =  dataclasses.I3Position(x*I3Units.m, y*I3Units.m, z*I3Units.m)
intercept = cylinder.intersection(vtx, adir)

centre = dataclasses.I3Position(((intercept.second*adir + vtx).x+(intercept.first*adir + vtx).x)/2.,((intercept.second*adir + vtx).y+(intercept.first*adir + vtx).y)/2.,((intercept.second*adir + vtx).z+(intercept.first*adir + vtx).z)/2.)
temp = centre.cross(bestfit)+centre*4.5
temp.z = 500
#window.gl.setCameraPivot(7.17023658752, 36.1024436951, -63.2644119263)
window.gl.setCameraOrientation(1, 0, 0)
window.gl.setCameraLoc(temp)
window.gl.setCameraPivot(0,0,0)

window.timeline.rangeFinder = "SplitUncleanedInIcePulses"
window.frame_filter.code = ""
window.activeView = 0
pulses = frame["SplitUncleanedInIcePulses"]
pulses = pulses.apply(frame)
qmax = -1
for key,val in pulses.items():
    qtot = 0
    for pulse in val:
        qtot = qtot + pulse.charge
    if qtot>qmax:
        qmax = qtot
        tmax = val[0].time
window.timeline.maxTime = int(tmax+5000.)
window.timeline.minTime = int(tmax-1000.)

reset = window.gl.cameraLoc
if np.absolute(reset.x)>np.absolute(reset.y):    
    scaling = 1770./np.absolute(reset.x)
else:
    scaling = 1770./np.absolute(reset.y)
window.gl.setCameraLoc(reset.x*scaling,reset.y*scaling,reset.z)

#print reset
#print temp

if frame.Has("I3EventHeader")==0:
    header = frame["QI3EventHeader"]
else:   
    header = frame['I3EventHeader']
run, event = header.run_id,header.event_id
from os.path import join
#outdir = "/home/lulu/Software/combo/build_realtime/realtime_tools/resources/scripts/IceCubeAlert_AR/Bot_Steamshovel_Screenshots/"
outdir = "/tmp/"
filename = join(outdir,"%i_%i.png" %(run,event))

window.gl.screenshotDpi(300,filename)


#del _dumpScenario
#app.quit
#import os
#os._exit(0)
#exit()

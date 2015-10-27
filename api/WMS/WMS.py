import threading
import pyinotify
import Queue
import mapscript
import fileinput, os, sys
#from logger import *

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        super(StoppableThread, self).__init__()
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class WMS(StoppableThread):

    def __init__(self):
        super(WMS,self).__init__()
        self.renderQueue = Queue.Queue()
        self.outputPath = "/var/www/map/imgs/"
        self.path = "/media/ramfs/runs/"

    def __del__(self):
        pass

    def getStatus(self):
        return "OK"

    def run(self):
        #setup renderer
        while (not self.stopped()):
            try:
                #wait for new file
                args = self.renderQueue.get(block=True,timeout=1)

                #do WMS-y things


            except Queue.Empty:
                pass

            except:
                print "Unexpected error:", sys.exc_info()[0]
                raise

    def fillCache(self):
        pass

    def emptyCache(self):
        #delete everything
        pass

    #public method to add a file to the render queue
    def getMap(self, speciesID, timelineID, time, params=[]):
        self.renderQueue.put([speciesID,timelineID,time, params])
        return self.generateMap(params)
        # print "Queued: " + inputFile

    def generateMap(self,params):
        i=int(params['time'])

        mapfile = 'WMS/static.map'
        m = mapscript.mapObj(mapfile)

        width = int(float(params['width']))
        height = int(float(params['height']))

        m.setSize(width,height)
        #large 16094657.112754999,-2030855.404508848,16366008.563167373,-1857343.3503014978
        #small 16258461.66437013, -1983693.758056894, 16260907.649275256, -1981247.7731517684
        #16229014.299223267, -2036989.4760287334, 16274226.801453948, -2006452.8832288054

        ext = params['bbox'].split(',')
        m.setExtent(float(ext[0]),float(ext[1]),float(ext[2]),float(ext[3]))

        layer = m.getLayerByName("dispersal")
        layer.data = "/media/ramfs/runs/siam-1/aggs/agg"+str(i)+".asc"

        savepath = "/var/www/map/imgs/siam-1/agg"+str(i)+".png"
        print "Rendered: " + str(i)
        return m.draw()

import threading
import pyinotify
import Queue
import mapscript
import fileinput, os, sys
import bencode, hashlib
import StringIO
import math
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
        self.cachePath = "data/cache/"
        self.path = "/media/ramfs/runs/"
        self.cacheID = 0

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

    def __getIdentifier(self,params,filename=True):
        pString = params['timeline']+params['species']+params['height']+params['width']
        pString+= str(params['bbox'])[1:-1]

        if filename:
            pString+=params['time']

        idHash = hashlib.md5(pString).hexdigest()
        return idHash

    def __checkCache(self,params):
        ID = self.__getIdentifier(params,False)

        if (self.cacheID == ID):
            return True
        else:
            self.cacheID = ID
            return False

    def __getFilename(self,params):
        return self.cachePath + str(self.__getIdentifier(params)) +".png"

    def __processParams(self,params):

        bbox = params['bbox'].split(",")
        for i in xrange(len(bbox)):
            bbox[i] = int(float(bbox[i]))

        params['bbox'] = bbox

        return params

    #public method to add a file to the render queue
    def getMap(self,wmsParams=[]):

        output = StringIO.StringIO()

        params = self.__processParams(wmsParams)

        #check cache
        noCache = False
        if self.__checkCache(params):
            ##load it from cache
            try:
                with open(self.__getFilename(params),'r') as file:
                    print "from cache"
                    output.write(file.read())
            except IOError:
                noCache=True

            mapImg = False
        else:
            noCache = True

        if noCache:
            time = int(params['time'])
            times = range(0,30)
            if time in times:
                times.remove(time)
            else:
                return false

            self.renderQueue.put({"params":params,"range":times})
            mapImg = self.__generateMap(params)
            mapImg.write(output)
            del mapImg

        imgOutput = output.getvalue()
        del output

        return imgOutput
        # print "Queued: " + inputFile

    def __generateMap(self,params):
        i=int(params['time'])

        mapfile = 'WMS/static.map'
        m = mapscript.mapObj(mapfile)

        width = int(float(params['width']))
        height = int(float(params['height']))
        species = params['species']
        timeline = params['timeline']
        identifier = species+"-"+timeline

        m.setSize(width,height)

        m.setExtent(params['bbox'][0],params['bbox'][1],params['bbox'][2],params['bbox'][3])

        layerParams = self._findLayerParams(identifier,i)
        if not layerParams:
            print "WMS: no layer data found"
            return False

        layer = m.getLayerByName("dispersal")
        layer.data = layerParams[0]
        layer.setProjection(layerParams[1])

        savepath = self.__getFilename(params)
        mapImg = m.draw()
        mapImg.save(savepath)

        del m

        print "Rendered: " + str(i)
        return mapImg

    def _findLayerParams(self,identifier,i):
        ascPath = "/media/ramfs/runs/"+identifier+"/aggs/agg"+str(i)+".asc"
        tifPath = "/media/scratch/imgs/"+identifier+"/agg"+str(i)+".tif"

        if os.path.isfile(ascPath):
            return [ascPath,"init=epsg:4326"]

        if os.path.isfile(tifPath):
            return [tifPath,"init=epsg:3857"]

        return false

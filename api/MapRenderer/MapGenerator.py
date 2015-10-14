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


class MapGenerator(StoppableThread):

    def __init__(self):
        super(MapGenerator,self).__init__()
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
                paths = self.renderQueue.get(block=True,timeout=1)

                inputFile = paths[0]
                outputFile = paths[1]

                #determine output path
                pathSeg = outputFile.split("/")
                del pathSeg[-1]
                outputPath = "/".join(pathSeg)
                #print "Output path: " + outputPath

                #check folder exists
                if not os.path.exists(outputPath):
                    #check parent folder exists
                    if os.path.exists(self.outputPath):
                        os.makedirs(outputPath)
                    else:
                        print "Output Path Doesn't Exist: Aborting"
                        self.stop()

                #render
                outputFile = self._render(inputFile,outputFile)

            except Queue.Empty:
                pass

            except:
                print "Unexpected error:", sys.exc_info()[0]
                raise

    #public method to add a file to the render queue
    def renderFile(self, inputFile, outputFile):
        self.renderQueue.put([inputFile,outputFile])
        # print "Queued: " + inputFile

    def _render(self, inputFile, outputFile):
        mapfile = 'MapRenderer/static.map'
        # print "Input From: " + inputFile
        # print "Output to: " + outputFile

        #check output directory exists
        if not os.path.exists(self.outputPath):
            os.makedirs(self.outputPath)

        try:
            m = mapscript.mapObj(mapfile)
            m.setSize(1542,2523)

            #set layer data file
            layer = m.getLayerByName("dispersal")
            layer.data = inputFile

            m.draw().save(outputFile)
        except mapscript.MapServerError as e:
            print e
            pass
            #log.critical(e)
        except IOError as e:
            print e
            pass
            #log.critical(e)


    def cleanup(self,fileName):
        os.remove(fileName)

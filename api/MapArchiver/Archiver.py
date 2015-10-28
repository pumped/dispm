import threading
import pyinotify
import Queue
import mapscript
import fileinput, os, sys
import time
import subprocess
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


class MapArchiver(StoppableThread):

    def __init__(self):
        super(MapArchiver,self).__init__()
        self.renderQueue = Queue.Queue()
        self.outputPath = "/var/www/map/imgs/"

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

                #determine output path to check the directory exists
                pathSeg = outputFile.split("/")
                del pathSeg[-1]
                outputPath = "/".join(pathSeg)

                #check folder exists
                if not os.path.exists(outputPath):
                    #check parent folder exists
                    if os.path.exists(self.outputPath):
                        os.makedirs(outputPath)
                    else:
                        print "Output Path Doesn't Exist: Aborting"
                        self.stop()

                #render
                outputFile = self._convert(inputFile,outputFile)

            except Queue.Empty:
                pass

            except:
                print "Unexpected error:", sys.exc_info()[0]
                raise

    #public method to add a file to the render queue
    def convertFile(self, inputFile, outputFile):
        print inputFile
        print outputFile
        self.renderQueue.put([inputFile,outputFile])
        # print "Queued: " + inputFile

    def _convert(self, inputFile, outputFile):
        #run warp
        t0 = time.time()

        with open(os.devnull, 'w') as FNULL:
            cmd = 'gdalwarp -s_srs "EPSG:4326" -t_srs "EPSG:3857" -overwrite -co COMPRESS=DEFLATE ' + inputFile + " " + outputFile
            status = subprocess.call(cmd, shell=True, stdout=FNULL)

        t1 = time.time()
        #print t1-t0

        #cleanup
        self.cleanup(inputFile)


    def cleanup(self,fileName):
        os.remove(fileName)

##
# logger
#  - manages all application logging
#
##

import logging
import threading
from operator import itemgetter

#log levels
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

class Singleton(object):
    def __new__(type):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance

class Logger(Singleton):
    
    mdLog = None
    liveLog = []
    liveLogSize = 12
    liveLogIndex = 0
    
    def __init__(self):
        LOG_FILENAME = 'log.txt'
        logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
        self.mdLog = logging.getLogger("default")
        
        #create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s::%(levelname)s::%(message)s")
        ch.setFormatter(formatter)
        self.mdLog.addHandler(ch)
    
    def insertLive(self, logLevel, message):
        i = self.liveLogIndex%self.liveLogSize
        self.liveLog.insert(0,{"ID":self.liveLogIndex,"logLevel":logLevel,"message":message})
        if (len(self.liveLog)>self.liveLogSize):
            self.liveLog.pop()

        self.liveLogIndex = self.liveLogIndex+1;
        #print self.liveLogIndex;

    def getLiveLog(self, idx=-1):
        logs = self.liveLog
        #print logs
        output = []
        for log in logs:
            if (log['ID'] > idx):
                output.append(log)

        return output

    def log(self, logLevel, message):
        tName = threading.currentThread().getName()
        output = tName + ': ' + str(message)
        self.insertLive(logLevel, output)
        if logLevel == DEBUG:
            self.mdLog.debug(output)
        elif logLevel == INFO:
           self.mdLog.info(output)
        elif logLevel == WARNING:
           self.mdLog.warning(output)
        elif logLevel == ERROR:
          self.mdLog.error(output)
        elif logLevel == CRITICAL:
          self.mdLog.error(output)
    
    def debug(self, str):
        self.log(DEBUG, str)
    
    def info(self, str):
        self.log(INFO, str)
        
    def warning(self, str):
        self.log(WARNING, str)
    
    def error(self, str):
        self.log(ERROR, str)
        
    def critical(self, str):
        self.log(CRITICAL, str)


log = Logger()

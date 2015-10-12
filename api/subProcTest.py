import subprocess
import json

def main():
    cmd = "stdbuf -oL /media/src/model/migclim/mig /media/ramfs/runs/a-b/params.txt /media/ramfs/runs/a-b/ /media/ramfs/runs/a-b/aggs"

    #run process
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=0, shell=True)

    #capture output
    while True:
        output = proc.stdout.readline()
        if output == '' and proc.poll() is not None:
            break
        if output:
            processOutput(output.strip())

    print "Process Finished"

def processOutput(output):
    line = output.lower()

    #process file write completion
    if line.startswith("write"):
        if (":" in line):
            parts = line.split(":",1)

            if len(parts) == 2:

                #determine year number
                fileNumber = parts[0].replace("write","").strip(" ")

                #process output
                statsJson = parts[1].strip()

                print fileNumber + " " + statsJson
                stats = json.loads(statsJson)

                sm.updateTime("asdf",1,fileNumber,stats)

                return [fileNumber, stats]


class StatStore:

    def __init__(self,fileName=None):
        self.fileName = fileName
        self.defaultTimeline = {\
            "startTime":0,\
            "endTime":30,\
            "ID":0,\
            "occupied":[],\
            "cost":0,\
            "children":[]\
        }

        if fileName is not None:
            self._loadStore()

    def _loadStore(self):
        try:
            with open(self.fileName,'r') as f:
                self.stats = json.load(f)
                print "loaded"
        except IOError:
            self.stats = self.defaultTimeline

    def _saveStore(self):
        print 'saving'
        with open(self.fileName,'w') as f:
            f.write(json.dumps(self.stats))
            print "saved"

    def getDefaultNode(self,id):
        self.stats["ID"] = id
        return self.stats

    def setTime(self,timelineID,time,stats):
        time = int(time)
        
        #check if timeline exists
        node = self.fetchTimeline(timelineID)

        if not node:
            #find parent
            node = self.getDefaultNode(timelineID)

        print "found node"
        for key in stats:
            print key

            #add key if necessary
            if key not in node:
                node[key] = []

            if len(node[key]) <= time:
                while len(node[key]) < time:
                    node[key].append(None)
                node[key].append(stats[key])
            else:
                node[key][time] = stats[key]


        #add stats
        print "time set"

    def setStats(self,timelineID,stats):
        self.stats = stats
        print "time set"

    def fetchTimeline(self,id):
        return self._recursiveSearch(id, self.stats)

    def _recursiveSearch(self, id, elem):
        if elem["ID"] == id:
            return elem;

        for i in elem["children"]:
            print i
            child = self._recursiveSearch(id,elem["children"][i])
            if child:
                return child

        return False

class StatManager:

    def __init__(self):
        self.stats = {}
        pass

    def loadStats(self,id):
        fileName = "data/stats/"+id+".json"

        #open stats file
        self.stats[id] = StatStore(fileName)

    def saveStats(self,id=None):
        if id is None:
            for timeline in self.stats:
                print timeline
        else:
            if id in self.stats:
                self.stats[id]._saveStore()

    def updateStats(self, id, timelineID, stats):
        if id not in self.stats:
            self.loadStats(id)

        self.stats[id].setStats(timelineID,stats)
        self.saveStats(id)

    #                 species timeline   time  stats
    #                    ^^      ^^       ^^    ^^^
    def updateTime(self, id, timelineID, time, stats):
        if id not in self.stats:
            self.loadStats(id)

        self.stats[id].setTime(timelineID,time,stats)
        self.saveStats(id)

sm = StatManager()
#sm.updateTime("asdf",1,1,json.loads('{"occupied":1,"total":1}'))
#sm.updateTime("asdf",1,2,json.loads('{"occupied":1,"total":1}'))
#sm.updateTime("asdf",1,3,json.loads('{"occupied":1,"total":1}'))
#sm.updateStats("asdf",1,json.loads('{"a":2}'))

main()

import json
import copy

class StatStore:

    def __init__(self,fileName=None):
        self.fileName = fileName
        self.defaultTimeline = {\
            "startTime":0,\
            "endTime":30,\
            "ID":None,\
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
                #print "loaded"
        except (IOError, ValueError) as e:
            self.stats = copy.deepcopy(self.defaultTimeline)

    def _saveStore(self):
        #print 'saving'
        with open(self.fileName,'w') as f:
            f.write(json.dumps(self.stats, sort_keys=True, indent=4))
            #print "saved"

    def getDefaultNode(self,id):
        self.stats["ID"] = id
        return self.stats

    def getNode(self,id):
        #check if timeline exists
        node = self.fetchTimeline(id)

        #create new node under parent
        if not node:
            if self.stats["ID"] is not None and "children" in self.stats:
                node = copy.deepcopy(self.defaultTimeline)
                #print 'creating node'
                #print node
                node["ID"] = id
                self.stats["children"].append(node)
            else:
                #print 'node create failed'
                pass

        #create a default node
        if not node:
            #find parent
            node = self.getDefaultNode(id)

        return node

    def setTime(self,timelineID,time,stats):
        time = int(time)

        node = self.getNode(timelineID)

        #set paramaters of node
        for key in stats:
            #print key
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
        #print "time set: " + str(timelineID)

    def setStats(self,timelineID,stats):
        self.stats = stats
        #print "time set"


    def getTimeline(self,id):
        node = self.fetchTimeline(id)
        if node:
            return node
        else:
            return False

    def getData(self):
        pass

    def fetchTimeline(self,id):
        return self._recursiveSearch(id, self.stats)

    def _recursiveSearch(self, id, elem):
        if elem["ID"] == id:
            return elem;

        for c in elem["children"]:
            #print c
            child = self._recursiveSearch(id,c)
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
            pass
            #for timeline in self.stats:
                #print timeline
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

    def getTimeline(self,id,timelineID):
        if id not in self.stats:
            self.loadStats(id)

        node = self.stats[id].getTimeline(timelineID)
        if node:
            return json.dumps(node)
        else:
            return False


    def getSpecies(self,id):
        if id not in self.stats:
            self.loadStats(id)

        node = json.dumps[self.stats[id].getData()]
        if node:
            return json.dumps(node)
        else:
            return False

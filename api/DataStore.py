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
                    node[key].append(0)
                node[key].append(stats[key])
            else:
                node[key][time] = stats[key]


        #add cost stats
        stats = {
            "delimitation":{"id":"d_range","cost":300,"costID":"d_cost","costSumID":"d_costSum","haSum":"d_haSum"},
            "prevention":{"id":"p_range","cost":0,"costID":"p_cost","costSumID":"p_costSum","haSum":"p_haSum"},
            "removal":{"id":"r_range","cost":1800,"costID":"r_cost","costSumID":"r_costSum","haSum":"r_haSum"},
            "containment":{"id":"c_range","cost":1200,"costID":"c_cost","costSumID":"c_costSum","haSum":"c_haSum"},
            "intensiveControl":{"id":"ic_range","cost":1200,"costID":"ic_cost","costSumID":"ic_costSum","haSum":"ic_haSum"},
            "assetProtection":{"id":"ap_range","cost":600,"costID":"ap_cost","costSumID":"ap_costSum","haSum":"ap_haSum"}
          }

        totalCost = 0

        for key in stats:
            #if the range is in the node
            if stats[key]["id"] in node:

                #get the array names
                id = stats[key]["id"]
                costID = stats[key]["costID"]
                costSumID = stats[key]["costSumID"]
                haSumID = stats[key]["haSum"]


                #setup cost arrays in node if it doesn't exist
                if costID not in node:
                    node[costID] = []
                    node[costSumID] = []
                    node[haSumID] = []

                #for each step in particular range add to cost
                cost = 0
                costSum = 0
                haSum = 0
                for i,val in enumerate(node[id]):
                    #calculate cost and cost summary
                    if val is not None:
                        cost = val * stats[key]["cost"]
                        haSum += val
                    else:
                        cost = 0
                        
                    costSum += cost
                    totalCost += cost


                    # if the node array isn't long enough, make it longer
                    if len(node[costID]) <= i:
                        while len(node[costID]) <= i:
                            node[costID].append(0)
                            node[costSumID].append(0)
                            node[haSumID].append(0)



                    #add it to the node
                    node[costID][i] = cost
                    node[costSumID][i] = costSum
                    node[haSumID][i] = haSum

        #for all of the prevention nodes
        if (stats["prevention"]["costID"] in node):
            preventionNode = node[stats["prevention"]["costID"]]
            preventionSumNode = node[stats["prevention"]["costSumID"]]
            amt = 0
            costSum = 0
            if "prevention" in node:
                amt = int(node["prevention"][0])

            for i,val in enumerate(preventionNode):
                cost = ((totalCost / 100)*amt) / len(preventionNode)
                costSum += cost

                preventionNode[i] = cost
                preventionSumNode[i] = costSum




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
        return self.stats

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

    def getStore(self,id):
        if id not in self.stats:
            self.loadStats(id)

        return self.stats[id]

    #                 species timeline   time  stats
    #                    ^^      ^^       ^^    ^^^
    def updateTime(self, id, timelineID, time, stats):
        self.getStore(id).setTime(timelineID,time,stats)
        self.saveStats(id)

    def getTimeline(self,id,timelineID):
        node = self.getStore(id).getTimeline(timelineID)
        if node:
            return json.dumps(node)
        else:
            return False


    def getSpecies(self,id):
        node = self.getStore(id).getData()
        if node:
            if "ID" in node:
                if node["ID"] != None:
                    return json.dumps(node)

        return False

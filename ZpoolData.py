'''
Created on Apr 12, 2017

@author: dquigley
'''
import os
from ToolData import ToolData
from __builtin__ import True
from PerfUtil import PerfUtil
        
class ZpoolRecord(object):
    def __init__(self):
        self.name = ""
        self.capacityAlloc = 0
        self.capacityFree = 0
        self.operationsRead = 0
        self.operationsWrite = 0
        self.bandwidthRead = 0
        self.bandwidthWrite = 0
        self.totalwaitRead = 0
        self.totalwaitWrite = 0
        self.diskwaitRead = 0
        self.diskwaitWrite = 0
        self.syncqwaitRead = 0
        self.syncqwaitWrite = 0
        self.asyncqwaitRead = 0
        self.asyncqwaitWrite = 0
        self.scrubwait = 0
        
            
    @classmethod
    def recordFromArgs(cls, args):
        record = cls()
        if len(args) == 16:
            record.name = args[0]
            record.capacityAlloc = int(args[1])
            record.capacityFree = int(args[2])
            record.operationsRead = int(args[3])
            record.operationsWrite = int(args[4])
            record.bandwidthRead = int(args[5])
            record.bandwidthWrite = int(args[6])
            record.totalwaitRead = int(args[7])
            record.totalwaitWrite = int(args[8])
            record.diskwaitRead = int(args[9])
            record.diskwaitWrite = int(args[10])
            record.syncqwaitRead = int(args[11])
            record.syncqwaitWrite = int(args[12])
            record.asyncqwaitRead = int(args[13])
            record.asyncqwaitWrite = int(args[14])
            record.scrubwait = int(args[15])
        return record
        
class ZpoolIOStat(object):
    def __init__(self):
        self.pool = None
        self.children = []
        pass
    @classmethod
    def statsFromLines(cls, lines):
        stats = cls()
        stats.pool = ZpoolRecord.recordFromArgs(lines[0].split())
        if len(lines) > 1:
            for line in lines[1:]:
                stats.children.append(ZpoolRecord.recordFromArgs(line.split()))
        return stats
        
class ZpoolIOSummary(object):
    def __init__(self):
        self.finalized = False
        self.name = ""
        self.count = 0
        self.capacityAlloc = 0
        self.capacityFree = 0
        self.operationsRead = 0
        self.operationsWrite = 0
        self.bandwidthRead = 0
        self.bandwidthWrite = 0
        self.totalwaitRead = 0
        self.totalwaitWrite = 0
        self.diskwaitRead = 0
        self.diskwaitWrite = 0
        self.syncqwaitRead = 0
        self.syncqwaitWrite = 0
        self.asyncqwaitRead = 0
        self.asyncqwaitWrite = 0
        self.scrubwait = 0
        
    def addRecord(self, record):
        self.count = self.count+1
        self.capacityAlloc += record.capacityAlloc
        self.capacityFree += record.capacityFree
        self.operationsRead += record.operationsRead
        self.operationsWrite += record.operationsWrite
        self.bandwidthRead += record.bandwidthRead
        self.bandwidthWrite += record.bandwidthWrite
        self.totalwaitRead += record.totalwaitRead
        self.totalwaitWrite += record.totalwaitWrite
        self.diskwaitRead += record.diskwaitRead
        self.diskwaitWrite += record.diskwaitWrite
        self.syncqwaitRead += record.syncqwaitRead
        self.syncqwaitWrite += record.syncqwaitWrite
        self.asyncqwaitRead += record.asyncqwaitRead
        self.asyncqwaitWrite += record.asyncqwaitWrite
        self.scrubwait += record.scrubwait
    
    def returnFinalized(self):
        from copy import deepcopy
        
        final = deepcopy(self)
        final.finalize()
        return final
        
    def finalize(self):
        self.capacityAlloc /= self.count
        self.capacityFree /= self.count
        self.operationsRead /= self.count
        self.operationsWrite /= self.count
        self.bandwidthRead /= self.count
        self.bandwidthWrite /= self.count
        self.totalwaitRead /= self.count
        self.totalwaitWrite /= self.count
        self.diskwaitRead /= self.count
        self.diskwaitWrite /= self.count
        self.syncqwaitRead /= self.count
        self.syncqwaitWrite /= self.count
        self.asyncqwaitRead /= self.count
        self.asyncqwaitWrite /= self.count
        self.scrubwait /= self.count
        self.finalized = True
    
    def compare(self, other):
        score = 0
        score += PerfUtil.compare(self.capacityAlloc, other.capacityAlloc)
        score += PerfUtil.compare(self.capacityFree, other.capacityFree)
        score += PerfUtil.compare(self.operationsRead, other.operationsRead)
        score += PerfUtil.compare(self.operationsWrite, other.operationsWrite)
        score += PerfUtil.compare(self.bandwidthRead, other.bandwidthRead)
        score += PerfUtil.compare(self.bandwidthWrite, other.bandwidthWrite)
        score += PerfUtil.compare(self.totalwaitRead, other.totalwaitRead)
        score += PerfUtil.compare(self.totalwaitWrite, other.totalwaitWrite)
        score += PerfUtil.compare(self.diskwaitRead, other.diskwaitRead)
        score += PerfUtil.compare(self.diskwaitWrite, other.diskwaitWrite)
        score += PerfUtil.compare(self.syncqwaitRead, other.syncqwaitRead)
        score += PerfUtil.compare(self.syncqwaitWrite, other.syncqwaitWrite)
        score += PerfUtil.compare(self.asyncqwaitRead, other.asyncqwaitRead)
        score += PerfUtil.compare(self.asyncqwaitWrite, other.asyncqwaitWrite)
        score += PerfUtil.compare(self.scrubwait, other.scrubwait)
        return PerfUtil.normalize(score)
        
        
        
class ZpoolDataSummary(object):
    def __init__(self, data = None):
        self.pool = ZpoolIOSummary()
        self.children = []
        if data is not None:
            for child in data.stats[0].children:
                newChild = ZpoolIOSummary()
                newChild.name = child.name
                self.children.append(newChild)
            self.summarizeData(data)
    def summarizeData(self, data):
        for row in data.stats:
            self.pool.addRecord(row.pool)
            for i in range(len(row.children)):
                self.children[i].addRecord(row.children[i])
        
        self.pool.finalize()
        for child in self.children:
            child.finalize()
    
    def compare(self, other):
        """
            TODO: This should be modified to check if self and other have been finalized
            and if not have them return finalized copies with return finalized also for
            now assume both runs have the same number of children
        """
        score = 0
        
        score += self.pool.compare(other.pool)
        for i in range(len(self.children)):
            score+= self.children[i].compare(other.children[i])      
        
        return PerfUtil.normalize(score)
        
        
class ZpoolData(ToolData):
    '''
    classdocs
    '''

    def __init__(self, filename=None):
        ToolData.__init__(self, "zpool.iostat")
        self.stats = []
        if filename:
            self.parseResults(filename)
        else:
            self.filename = ""
        pass
        
    def parseResults(self, resultFile):
        """
            TODO: This function is the way it is because we don't collect the 
            zpool.iostat data with -H. Convert to use -H in the future 
            since we don't need it to be human readable
        """
        self.filename = os.path.abspath(resultFile)
        
        f = open(self.filename)
        save = False
        lines = []
        for line in f:
            if line[0] == '-' and save is False:
                save = True
            elif line[0] == '-' and save is True:
                save = False
                self.stats.append(ZpoolIOStat.statsFromLines(lines))
                lines = []
            elif save:
                lines.append(line)
        f.close()                   
        pass
    def summarize(self):
        return ZpoolDataSummary(self) 
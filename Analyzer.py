'''
Created on Apr 13, 2017

@author: dquigley
'''
import jsonpickle
from os import listdir
from os.path import isfile, join, abspath, basename
from FioData import FioData
from DstatData import DstatData
from ZpoolData import ZpoolData
from PerfUtil import PerfUtil

class TestConfigSummary():
    def __init__(self, testConfig = None):
        if testConfig is None:
            self.testScript = ""
            self.sync = ""
            self.iosize = ""
            self.threads = "" 
            self.toolSummaries = {}
        else:
            self.loadFromTestConfig(testConfig)
           
    def loadFromTestConfig(self, testConfig):
        self.testScript = testConfig.testScript
        self.sync = testConfig.sync
        self.iosize = testConfig.iosize
        self.threads = testConfig.threads
        self.toolSummaries = {}

        toolSummary = {}
        for key, value in testConfig.toolData.items():
            toolSummary[key] = value.summarize()
        self.toolSummaries = toolSummary
        
    def compare(self, other):
        """
        TODO: This assumes that all configs have the same tools
        that were summarizes or at least that every key present
        in self.toolSummaries is also in other.toolSummaries
        """
        
        score = 0
        for key in self.toolSummaries.keys():
            score += self.toolSummaries[key].compare(other.toolSummaries[key]) 
        return PerfUtil.normalize(score)
        
class TestConfig(object):
    def __init__(self):
        self.testScript = ""
        self.sync = ""
        self.iosize = ""
        self.threads = "" 
        self.toolData = {}
    def summarize(self):
        summary = TestConfigSummary(self)
        return summary
        
class Analyzer(object):
    '''
    classdocs
    '''
    def __init__(self, dirname=None):
        self.testRuns = {}
        if dirname:
            self.loadResults(dirname)
        else:
            self.dirname = ""
        pass
    
    def findTestRun(self, scriptName, sync, iosize, threads):
        if scriptName not in self.testRuns.keys():
            return None
        for config in self.testRuns[scriptName]:
            if config.sync == sync and config.iosize == iosize and config.threads == threads:
                    return config
        return None
    
    def loadToolData(self, fileName, toolName):
        '''This is a klugy hack just for now.'''
        if toolName == "fio":
            return FioData(fileName)
        elif toolName == "dstat":
            return DstatData(fileName)
        elif toolName == "zpool.iostat":
            return ZpoolData(fileName)
        return None
    
    def loadResults(self, dirname):
        self.dirname = abspath(dirname)
        self.files = []
        
        for f in listdir(self.dirname):
            if isfile(join(self.dirname, f)):
                self.files.append(join(self.dirname, f))
        
        for f in self.files:
            filename = basename(f)
            tokens = filename.split('-')
            if len(tokens) < 5:
                continue
            scriptName = tokens[0]
            toolName = tokens[1]
            syncType = tokens[2]
            iosize = tokens[3].split('.')[0]
            extension = ""
            
            threadTokens = tokens[4].split('.')
            threads = threadTokens[0]
                
            if len(threadTokens) is 3:
                extension = threadTokens[2]
            
            #Check to see if we have an easy out by not having the right file
            if toolName == "dstat" and extension != "csv":
                continue
            if toolName == "fio" and extension != "json":
                continue
            
            testRun = self.findTestRun(scriptName, syncType, iosize, threads)
            if testRun:
                testRun.toolData[toolName] = self.loadToolData(f, toolName) 
            else:
                newRun = TestConfig()
                newRun.testScript = scriptName
                newRun.sync = syncType
                newRun.iosize = iosize
                newRun.threads = threads
                newRun.toolData[toolName] = self.loadToolData(f, toolName)
                if scriptName not in self.testRuns.keys():
                    self.testRuns[scriptName] = []
                self.testRuns[scriptName].append(newRun)
        pass
    
    def writeAnalysis(self, filename):
        
        output = {}
        
        for key, value in self.testRuns.items():
            
            configs = []
            output[key] = configs
            for config in value:
                configs.append(config.summarize()) 
        
        
        with open(filename, 'w') as f:
            data = jsonpickle.encode(output)
            f.write(data)
        pass
    
        
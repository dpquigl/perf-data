'''
Created on Apr 12, 2017

@author: dquigley
'''
import os
import csv
import itertools 
from ToolData import ToolData
from PerfUtil import PerfUtil

class DstatCpuData(object):
    def __init__(self,usr,sys,idl,wai,hiq,siq):
        self.usr = float(usr)
        self.sys = float(sys)
        self.idl = float(idl)
        self.wai = float(wai)
        self.hiq = float(hiq)
        self.siq = float(siq)
        pass
    @classmethod
    def dataFromRow(cls,row):
        return cls(row['usr'],row['sys'],row['idl'],row['wai'],row['hiq'],row['siq'])

class DstatDiskData(object):
    def __init__(self,read,writ):
        self.read = int(read.split('.')[0])
        self.writ = int(writ.split('.')[0])   
        pass
    @classmethod
    def dataFromRow(cls,row):
        return cls(row['read'],row['writ'])
    
class DstatNetData(object):
    def __init__(self,recv,send):
        self.recv = int(recv.split('.')[0])
        self.send = int(send.split('.')[0])
        pass
    @classmethod
    def dataFromRow(cls,row):
        return cls(row['recv'],row['send'])

class DstatPageData(object):
    def __init__(self,pagein,pageout):
        self.pagein = int(pagein.split('.')[0])
        self.pageout = int(pageout.split('.')[0])
        pass
    @classmethod
    def dataFromRow(cls,row):
        return cls(row['in'],row['out'])

class DstatSystemData(object):
    def __init__(self, interrupt, csw):
        self.interupt = int(interrupt.split('.')[0])
        self.csw = int(csw.split('.')[0])
        pass
    @classmethod
    def dataFromRow(cls,row):
        return cls(row['int'],row['csw'])
    
class DstatDataRow(object):
    def __init__(self, row):
        self.cpu = DstatCpuData.dataFromRow(row)
        self.disk = DstatDiskData.dataFromRow(row)
        self.net = DstatNetData.dataFromRow(row)
        self.page = DstatPageData.dataFromRow(row)
        self.system = DstatSystemData.dataFromRow(row)
       
class DstatDataSummary(object): #Will probably extend SummaryData later 
    def __init__(self):
        self.count = 0
        self.read = 0
        self.writ = 0
        self.usr = 0
        self.sys = 0
        self.idl = 0
        self.wai = 0
        self.hiq = 0
        self.siq = 0
        self.pagein = 0
        self.pageout = 0
        
    def addRecord(self, record):
        self.count = self.count+1
        self.read += record.disk.read
        self.writ += record.disk.writ
        self.usr += record.cpu.usr
        self.sys += record.cpu.sys
        self.idl += record.cpu.idl
        self.wai += record.cpu.wai
        self.hiq += record.cpu.hiq
        self.siq += record.cpu.siq
        self.pagein += record.page.pagein
        self.pageout += record.page.pageout
    
    def returnFinalized(self):
        from copy import deepcopy
        
        final = deepcopy(self)
        final.finalize()
        return final
               
    def finalize(self):
        self.read /= self.count
        self.writ /= self.count
        self.usr /= self.count
        self.sys /= self.count
        self.idl /= self.count
        self.wai /= self.count
        self.hiq /= self.count
        self.siq /= self.count
        self.pagein /= self.count
        self.pageout /= self.count
        self.finalized = True
        
    def compare(self, other):
        score = 0
        score += PerfUtil.compare(self.read, other.read)
        score += PerfUtil.compare(self.writ, other.writ)
        score += PerfUtil.compare(self.usr, other.usr)
        score += PerfUtil.compare(self.sys, other.sys)
        score += PerfUtil.compare(self.idl, other.idl)
        score += PerfUtil.compare(self.wai, other.wai)
        score += PerfUtil.compare(self.hiq, other.hiq)
        score += PerfUtil.compare(self.siq, other.siq)
        score += PerfUtil.compare(self.pagein, other.pagein)
        score += PerfUtil.compare(self.pageout, other.pageout)
    
        return PerfUtil.normalize(score)
        

class DstatData(ToolData):
    '''
    classdocs
    '''

    def __init__(self, filename=None):
        ToolData.__init__(self, "dstat")
        self.data = []
        if filename:
            self.parseResults(filename)
        else:
            self.filename = ""
        pass
        
    def parseResults(self, resultFile):
        self.filename = os.path.abspath(resultFile)
        
        CSVFile = open(self.filename)
        '''Dstat csv files have an annoying header so we need to remove it'''
        reader = csv.DictReader(itertools.islice(CSVFile, 6, None))
        for row in reader:
            self.data.append(DstatDataRow(row))
        CSVFile.close()
        pass
    
    def summarize(self):
        summary = DstatDataSummary()
        for record in self.data:
            summary.addRecord(record)
        summary.finalize()
        return summary
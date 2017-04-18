'''
Created on Apr 11, 2017

@author: dquigley
'''
import os
import json
from ToolData import ToolData
from PerfUtil import PerfUtil






class FioLatData(object):
    def __init__(self):
        self.min = 0
        self.max = 0
        self.mean = 0.0
        self.stddev = 0.0
        self.percentile = {}
    @classmethod
    def loadFromJson(cls, jObject):
        lat = cls()
        lat.min = jObject['min']
        lat.max = jObject['max']
        lat.mean = jObject['mean']
        lat.stddev = jObject['stddev']
        if 'percentile' in jObject:
            for key, value in jObject['percentile'].items():
                lat.percentile[key] = value
        return lat
    def compare(self, other):
        score = 0;
        score += PerfUtil.compare(self.min, other.min)
        score += PerfUtil.compare(self.max,other.max)
        score += PerfUtil.compare(self.mean,other.mean)
        score += PerfUtil.compare(self.stddev,other.stddev)
        
        keys = set(self.percentile).intersection(set(other.percentile))
        for key in keys:
            score += PerfUtil.compare(self.percentile[key], other.percentile[key])
        return PerfUtil.normalize(score)
   
class FioIoDataSummary(object):
    def __init__(self, ioData = None):
        if ioData is None:
            self.iops = 0
            self.bw = 0
            self.runtime = 0
            self.lat = None
            self.clat = None
        else:
            self.loadFromIoData(ioData) 
        pass   
    def loadFromIoData(self, ioData):
        self.iops = ioData.iops
        self.bw = ioData.bw
        self.runtime = ioData.runtime
        self.lat = ioData.lat
        self.clat = ioData.clat
        pass
    def compare(self,other):
        score = 0
        score += PerfUtil.compare(self.iops, other.iops)
        score += PerfUtil.compare(self.bw, other.bw)
        score += PerfUtil.compare(self.runtime, other.runtime)
        score += self.lat.compare(other.lat)
        score += self.clat.compare(other.clat)
        return PerfUtil.normalize(score)
        
class FioIoData(object):
    def __init__(self):
        self.io_bytes = 0
        self.bw = 0
        self.iops = 0
        self.runtime = 0
        self.total_ios = 0
        self.short_ios = 0
        self.drop_ios = 0
        self.slat = None
        self.clat = None
        self.lat = None
        self.bw_min = 0
        self.bw_max = 0
        self.bw_agg = 0.0
        self.bw_mean = 0.0
        self.bw_dev = 0.0
        pass
    @classmethod
    def loadFromJson(cls, jObject):
        io = cls()
        io.io_bytes = jObject['io_bytes']
        io.bw = jObject['bw']
        io.iops = jObject['iops']
        io.runtime = jObject['runtime']
        io.total_ios = jObject['total_ios']
        io.short_ios = jObject['short_ios']
        io.drop_ios = jObject['drop_ios']
        io.slat = FioLatData.loadFromJson(jObject['slat'])
        io.clat = FioLatData.loadFromJson(jObject['clat'])
        io.lat = FioLatData.loadFromJson(jObject['lat'])
        io.bw_min = jObject['bw_min']
        io.bw_max = jObject['bw_max']
        io.bw_agg = jObject['bw_agg']
        io.bw_mean = jObject['bw_mean']
        io.bw_dev = jObject['bw_dev']
        return io
    def summarize(self):
        return FioIoDataSummary(self)
    
class FioJobSummary(object):
    def __init__ (self, job = None):
        if job is None:
            self.ioSummaries = {}
        else:
            self.loadFromJobData(job)
        pass
    def loadFromJobData(self, job):
        self.ioSummaries = {}
        self.ioSummaries['read'] = job.read.summarize()
        self.ioSummaries['write'] = job.write.summarize()
        self.ioSummaries['trim']  = job.trim.summarize() 
    
    def compare(self, other):
        score = 0
        score += self.ioSummaries['read'].compare(other.ioSummaries['read'])
        score += self.ioSummaries['write'].compare(other.ioSummaries['write'])
        score += self.ioSummaries['trim'].compare(other.ioSummaries['trim'])
        return PerfUtil.normalize(score)

class FioJob(ToolData):
    def __init__(self):
        self.jobname = ""
        self.groupid = 0
        self.error = 0
        self.read = None
        self.write = None
        self.trim = None
        self.usr_cpu = 0.00
        self.sys_cpu = 0.00
        self.ctx = 0
        self.majf = 0
        self.minf = 0
        self.iodepth_level = {}
        self.latency_us = {}
        self.latency_ms = {}
        self.latency_depth = 0
        self.latency_target = 0
        self.latency_percentile = 0.0
        self.latency_window = 0
    
    @classmethod
    def loadFromJson(cls,jObject):
        job = cls()
        job.jobname = jObject['jobname']
        job.groupid = jObject['groupid']
        job.error = jObject['error']
        if 'read' in jObject:
            job.read = FioIoData.loadFromJson(jObject['read'])
        if 'write' in jObject:
            job.write = FioIoData.loadFromJson(jObject['write'])
        if 'trim' in jObject:
            job.trim = FioIoData.loadFromJson(jObject['trim'])
        job.usr_cpu = jObject['usr_cpu']
        job.sys_cpu = jObject['sys_cpu']
        job.ctx = jObject['ctx']
        job.majf = jObject['majf']
        job.minf = jObject['minf']
        for key, value in jObject['iodepth_level'].items():
            job.iodepth_level[key] = value
        for key, value in jObject['latency_us'].items():
            job.latency_us[key] = value
        for key, value in jObject['latency_ms'].items():
            job.latency_ms[key] = value
        job.latency_depth = jObject['latency_depth']
        job.latency_target = jObject['latency_target']
        job.latency_percentile = jObject['latency_percentile']
        job.latency_window = jObject['latency_window']
        return job

class FioSummary(object):
    def __init__(self, data = None):
        """
            TODO: Fix this so we have a way of adding jobs after construction
        """
        if data is None:
            self.jobs = []
        else:
            for job in data.jobs:
                self.jobs = []
                self.jobs.append(FioJobSummary(job))
        pass
    def compare(self, other):
        """
            For now assume both sides have the same number of jobs
            otherwise its not an apples to apples comparison.
        """
        score = 0;
        for i in range(len(self.jobs)):
            score += self.jobs[i].compare(other.jobs[i])
        return PerfUtil.normalize(score)
        


class FioData(ToolData):
    '''
    classdocs
    '''

    def __init__(self, filename=None):
        ToolData.__init__(self, "fio")
        if filename:
            self.parseResults(filename)
        else:
            self.filename = ""
            self.fio_version = ""
            self.timestamp = 0
            self.time = ""
            self.jobs = []
        pass
        
    def parseResults(self, resultFile):
        self.filename = os.path.abspath(resultFile)
        
        file_data = open(self.filename)
        self.rawdata = json.load(file_data)
        jObject = self.rawdata
        self.fio_version = jObject['fio version']
        self.timestamp = jObject['timestamp']
        self.time = jObject['time']
        self.jobs = []
        for job in jObject['jobs']:
            self.jobs.append(FioJob.loadFromJson(job))
        file_data.close()
        pass
    def summarize(self):
        return FioSummary(self)
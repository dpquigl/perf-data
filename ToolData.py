'''
Created on Apr 11, 2017

@author: dquigley
'''

class ToolData(object):
    '''
    classdocs
    '''
    def __init__(self, toolName):
        self.toolName = toolName
        
    def parseResults(self, resultFile):
        '''
        Not sure if there is any superclass behavior here yet but sub classes will implement.
        '''
        pass
    def compare(self, obj1, obj2):
        pass
    def summarize(self):
        pass
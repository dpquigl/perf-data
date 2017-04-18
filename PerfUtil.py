'''
Created on Apr 18, 2017

@author: dquigley
'''

class PerfUtil(object):
    
    @staticmethod
    def normalize(score, weight = 1):
        """
            normalizes the score to {-weight0,weight}
            This is so a comparison on something like clat with 
            15 fields doesn't get additional weight. By default weight is 1
        """
        if score == 0:
            return 0
        elif score > 0:
            return weight
        else:
            return -weight
        
    @staticmethod
    def compare(first = None, second = None, margin=.20):
        """
            First: Base value to compare
            Second: object being compared to
            margin: decimal percentage to use for variance
            
            will return a value in the set {-1,0,1} for 
            which item is greater {first, equal, second}
        """
        if first is None and second is not None:
            return 1
        elif second is None and first is not None:
            return -1
        elif first is None and second is None:
            return 0
        
        variance = int(first * margin)
        distance = (first - second)
        
        if abs(distance) <= variance:
            return 0
        elif distance < 0:
            return 1
        else:
            return -1
        
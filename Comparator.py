'''
Created on Apr 18, 2017

@author: dquigley
'''
import jsonpickle
from PerfUtil import PerfUtil

class Comparator(object):
    '''
    classdocs
    '''


    def __init__(self, first, second):
        """
            TODO: for now assume that the summaries share
            some keys but are not necessarily equal. Also
            for each script key we will only compare configs
            that are present in both
        """
        first_data = first.read()
        second_data = second.read()
        self.first_summary = jsonpickle.decode(first_data)
        self.second_summary = jsonpickle.decode(second_data)
    
    def compare(self):
        score = 0
        joint_keys = set(self.first_summary.keys()).intersection(set(self.second_summary.keys()))
        
        for key in joint_keys:
            pairs = []
            
            """
            TODO: This is stupid. I really need to make the configs hashable so 
            they can be hashed and that hash used as a key in a dictionary. 
            Even if this is just concatenating the important values. This 
            n^2 search of the lists for matching pairs is just stupid when
            the dictionary class can do it on its own if I just implement
            rich equality comparison.
            """
            for first_config in self.first_summary[key]:
                for second_config in self.second_summary[key]:
                    if (
                        first_config.sync == second_config.sync and 
                        first_config.iosize == second_config.iosize and 
                        first_config.threads == second_config.threads
                        ):
                            pairs.append((first_config, second_config))
                            break
        
            
            for pair in pairs:
                score += pair[0].compare(pair[1])
        return PerfUtil.normalize(score)       
        
""" Patched to load EEA mail configuration
"""
import os                                                                                                                                                              
from Globals import package_home 
from Acquisition import aq_base                                                                                                                                      
                                                                                                                                                                       
EEA_CONFIG_PATH = os.path.join(package_home(globals()), 'eea_mailhost_config')                                                                                         
                                                                                                                                                                       
def patched_getConfigPath(self):                                                                                                                                           
    """ Get the path to the currently active configuration file                                                                                                    
    """                                                                                                                                                            
    return getattr(aq_base(self), 'config_path', EEA_CONFIG_PATH)                                                                                                                 
                                                                                                                                                                       
                                                                                                                                                                       
                                                                                                                                                                       

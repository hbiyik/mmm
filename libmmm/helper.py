'''
Created on Nov 4, 2022

@author: boogie
'''
import logging

LOGLEVEL = logging.INFO
# LOGLEVEL = logging.DEBUG
logging.basicConfig(level=LOGLEVEL, format='%(message)s')
logger = logging.getLogger("mmm")

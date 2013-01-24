__author__ = 'juliewe'

from stsdata import STSData

datadirname="/Users/juliewe/Documents/workspace/STS/data/trial/STS2012-train/STSinput-tagged"

mydata = STSData()
mydata.readdata(datadirname)
__author__ = 'juliewe'

from stsdata import STSData

datadirname="/Users/juliewe/Documents/workspace/STS/data/trial/STS2012-train/STSinput-tagged"
gsdirname="/Users/juliewe/Documents/workspace/STS/data/trial/STS2012-train/gs"
cv_param=5


mydata = STSData()
mydata.readdata(datadirname)
mydata.split(cv_param)
mydata.readgs(gsdirname)
#mydata.testread()
param=1
while(param<=cv_param):
    print mydata.fitpoly("MSRpar",param,"lemma")
    param+=1
__author__ = 'juliewe'

from stsdata import STSData

datadirname="/Users/juliewe/Documents/workspace/STS/data/trial/STS2012-train/STSinput-tagged"
gsdirname="/Users/juliewe/Documents/workspace/STS/data/trial/STS2012-train/gs"
cv_param=10
files=["MSRpar","MSRvid","SMTeuroparl"]
#sims=["lemma_content","token","lemma"]
sims=["lemma_content"]

mydata = STSData()
mydata.readdata(datadirname)
mydata.split(cv_param)
mydata.readgs(gsdirname)
mydata.testread()
for type in sims:
    for f in files:
        param=1
        total=0
        while(param<=cv_param):
            r= mydata.testpoly(f,param,type)
            total +=r[0]
            #print f, param, r
            param+=1

        av=total/cv_param
        print "Average cross-validation correlation for "+f+" with "+type+" similarity is "+str(av)

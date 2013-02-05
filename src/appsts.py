__author__ = 'juliewe'

from stsdata import STSData

datadirname="/Users/juliewe/Documents/workspace/STS/data/trial/STS2012-train/STSinput-tagged"
gsdirname="/Users/juliewe/Documents/workspace/STS/data/trial/STS2012-train/gs"
cv_param=10
cv_repeat=10
k=1.96 #for 95% confidence intervals
files=["MSRpar","MSRvid","SMTeuroparl"]
sims=["token_content","lemma_content","token","lemma"]
#sims=["lemma_content"]
graphson=False


mydata = STSData(graphson)
mydata.readdata(datadirname)
mydata.readgs(gsdirname)
#mydata.testread()
for type in sims:
    for f in files:
        param=1
        repeat_param=1
        total=0
        totalsquare=0
        n=0
        while(repeat_param<=cv_repeat):
            mydata.split(cv_param)
            while(param<=cv_param):
                r= mydata.testpoly(f,param,type)
                total +=r[0]
                totalsquare +=r[0]*r[0]
                #print f, param, r
                param+=1
                n+=1
            repeat_param+=1
            param=1

        av=total/n
        sd=pow(totalsquare/n - av*av,0.5)

        int = k*sd/pow(n,0.5)
        print "Average cross-validation correlation for "+f+" with "+type+" similarity is "+str(av)+", sd="+str(sd)+", n="+str(n)
        print "95% confidence interval is "+str(av)+" +- "+str(int)

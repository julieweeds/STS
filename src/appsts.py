__author__ = 'juliewe'

import sys
from stsdata import STSData

#set up configuration. Import configuration function
import conf
#pass commandline arguments
(testing,at_home,on_apollo,windows,filtered,comptype,metric,setsim,threshold,threshtype,toyrun,use_cache,adja,adjb)=conf.configure(sys.argv)

#uni filenames
parent="/Volumes/LocalScratchHD/juliewe/Documents/workspace/STS/data/"

if at_home:
    parent="C:/Users/Julie/Documents/GitHub/STS/data/"

if on_apollo:
    parent="/mnt/lustre/scratch/inf/juliewe/STS/data/"

datadirname=parent+"trial/STS2012-train/STSinput-tagged"
gsdirname=parent+"trial/STS2012-train/gs"


if filtered:
    vectorfilename=parent+"vectors_gw_filt/vectors_mi"
else:
    vectorfilename=parent+"allvectors/vectors_mi"


cv_param=10
cv_repeat=10
k=1.96 #for 95% confidence intervals
files=["MSRpar","MSRvid","SMTeuroparl"]
#files=["MSRvid"]
#sims=["lemma_content","sent_set","sent_comp"]
#sims=["dinu_overlap"]
sims=["sent_set"]
baseline="lemma_content"
graphson=False
verbose=False

if testing:
    sims=["sent_set"]
    files=["MSRpar"]
    cv_param=10
    cv_repeat=1
    graphson=False
    #vectorfilename=vectorfilename+"_test"

#comptype="additive"
#metric="cosine"

if toyrun:
    datadirname=parent+"toy/toyinput-tagged"
    gsdirname=parent+"toy/gs"
    files=["toy1"]
    sims=["sent_set"]
    cv_param=2
    cv_repeat=1
    baseline="none"
    verbose=True

if windows:
    cachename=datadirname+"/../win_vectors.cached"
else:
    cachename=datadirname+"/../dep_vectors.cached"

if use_cache:
    vectorfilename=cachename


def do_correlation(mydata):

    for type in sims:
        for f in files:
            param=1
            repeat_param=1
            total=0
            totalsquare=0
            n=0
            mydata.setseed()
            while(repeat_param<=cv_repeat):
                mydata.split(cv_param)
                while(param<=cv_param):
                    if baseline=="none":
                        r=mydata.testpoly(f,param,type)
                    else:
                        r= mydata.testpoly2(f,param,baseline,type)
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
            if baseline=="none":
                print "Starting next run"
            else:
                outfile=parent+"logs/ranking_"+f+"_"+type+"_"+setsim+"_"+str(windows)
                outstream=open(outfile,'w')
                mydata.ranksent(f,type,cv_repeat,outstream)
                outstream.close()
                print "Starting next run"


mydata = STSData(graphson,testing,windows,threshold,threshtype,verbose,adja,adjb)
print "Configuration set to windows = ", windows
print "Composition type = ", comptype
print "Similarity metric = ", metric
print "Set similarity method = ", setsim
print "Similarity threshold = ", str(threshold)
print "Threshold type = ", threshtype
mydata.readdata(datadirname)
mydata.readgs(gsdirname)
sys.stdout.flush()
if "sent_set" in sims:
    mydata.readvectors(vectorfilename,cachename)
elif "sent_comp" in sims:
    mydata.readvectors(vectorfilename,cachename)

sys.stdout.flush()
if "sent_set" in sims:
    mydata.set_simall(setsim,metric)
if "sent_comp" in sims:
    mydata.composeall_faster(comptype,metric)
#for dataset in files:
#    mydata.testread("gs",dataset)
for sim in sims:
    for dataset in files:
        mydata.testread(sim,dataset)
#mydata.inspect()
if toyrun:
    mydata.inspect()
else:
    do_correlation(mydata)


__author__ = 'juliewe'

import sys
import conf
from thesaurus import Thesaurus
#pass commandline arguments
(testing,at_home,on_apollo,windows,filtered,comptype,metric,setsim,threshold,threshtype,toyrun,use_cache,adja,adjb)=conf.configure(sys.argv)

#uni filenames
parent="/Volumes/LocalScratchHD/juliewe/Documents/workspace/STS/data/"

if at_home:
    parent="C:/Users/Julie/Documents/GitHub/STS/data/"

if on_apollo:
    parent="/mnt/lustre/scratch/inf/juliewe/STS/data/"

datadirname=parent+"trial/STS2012-train/STSinput-tagged"



if windows:
    cachename=datadirname+"/../win_vectors.cached"
    simcachefile=datadirname+"/../win_sims.cached"
else:
    cachename=datadirname+"/../dep_vectors.cached"
    simcachefile=datadirname+"/../dep_sims.cached"


if use_cache:
    vectorfilename=cachename


words=[("man","N"),("woman","N"),("lady","N"),("gentleman","N"),("light","N")]

simcache=False #whether file currently contains valid sims
k=100

mythes=Thesaurus(vectorfilename,simcachefile,simcache,windows,k,adja,adjb)
mythes.readvectors()
for wordA in words:
    for wordB in words:
        mythes.outputsim(wordA,wordB,metric)
mythes.allpairssims(metric)

mythes.analyse()
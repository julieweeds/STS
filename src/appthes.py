__author__ = 'juliewe'

import sys
import conf
from thesaurus import Thesaurus
#pass commandline arguments
(testing,at_home,on_apollo,windows,filtered,comptype,metric,setsim,threshold,threshtype,toyrun,use_cache)=conf.configure(sys.argv)

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


simcache=True #whether file currently contains valid sims
k=100

mythes=Thesaurus(vectorfilename,simcachefile,simcache,windows,k)
mythes.readvectors()
mythes.allpairssims()
mythes.analyse()
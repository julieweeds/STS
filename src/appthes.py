__author__ = 'juliewe'

import sys
import conf
from thesaurus import Thesaurus
#pass commandline arguments
(testing,at_home,on_apollo,windows,filtered,comptype,metric,setsim,threshold,threshtype,toyrun,use_cache,adja,adjb,simcache,byblo)=conf.configure(sys.argv)

#uni filenames
#parent="/Volumes/LocalScratchHD/juliewe/Documents/workspace/STS/data/"
parent="/Volumes/LocalScratchHD/juliewe/Documents/workspace/ThesEval/"

if at_home:
    parent="C:/Users/Julie/Documents/GitHub/STS/data/"

if on_apollo:
    parent="/mnt/lustre/scratch/inf/juliewe/STS/data/"

#datadirname=parent+"trial/STS2012-train/STSinput-tagged"
datadirname=parent+"data/giga_t10/"


if windows:
#    cachename=datadirname+"/../win_vectors.cached"
#    simcachefile=datadirname+"/../"+metric+"test_win_sims.cached"
    cachename=datadirname+"nouns_win.mi"
    if byblo:
        simcachefile=datadirname+"nouns_win.byblo"
    else:
        simcachefile=datadirname+"nouns_win_sims.cached"
else:
#    cachename=datadirname+"/../dep_vectors.test"
#    simcachefile=datadirname+"/../"+metric+"test_dep_sims.cached"
    cachename=datadirname+"nouns-deps.mi"
    if byblo:
        simcachefile=datadirname+"nouns-deps.byblo"
    else:
        simcachefile=datadirname+"nouns-win-deps.cached"

if use_cache:
    vectorfilename=cachename


words=[("man","N"),("woman","N"),("lady","N"),("gentleman","N"),("person","N"),("light","N")]
testpair=(("lady","N"),("stir","V"))

#simcache=False #whether file currently contains valid sims
k=100
kdisplay=10

print(sys.argv)
Thesaurus.byblo = byblo
mythes=Thesaurus(vectorfilename,simcachefile,simcache,windows,k,adja,adjb)
mythes.readvectors()
#if simcache:
#    check=True
#else:
#    for wordA in words:
#        for wordB in words:
#            mythes.outputsim(wordA,wordB,metric)

#(word1,word2)=testpair
#mythes.outputsim(word1,word2,metric)

mythes.allpairssims(metric)

for word in words:
    mythes.displayneighs(word,kdisplay)
mythes.analyse()
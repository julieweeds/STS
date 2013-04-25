import re

thresholdPATT = re.compile('threshold=(.*)')
linadjaPATT = re.compile('linadja=(.*)')
linadjbPATT = re.compile('linadjb=(.*)')

def configure(arguments):

#set defaults
#mode
    testing=False
#location
    at_home=False
    on_apollo=True
#feature_type

    windows=False
#filtered vectors
    filtered=False
#composition type
    comptype="additive"
#similarity metric
    metric="cosine"
#set similarity method
    setsim="avg_max"
#set similarity threshold
    threshold =0
#set threshold type
    threshtype="nonbin"
#data
    toyrun=False
#use vector cache?
    use_cache=False
#linadj parameters
    adja=2
    adjb=1
#valid sims in simcache file for thesaurus
    simcache=False



#override with command line arguments
    for argument in arguments:
        if argument == "testing":
            testing = True
        elif argument == "windows":
            windows =True
        elif argument == "deps":
            windows = False
        elif argument == "apollo":
            on_apollo=True
        elif argument == "local":
            on_apollo=False
            at_home=False
        elif argument == "home":
            on_apollo=False
            at_home=True
        elif argument == "multiplicative":
            comptype="multiplicative"
        elif argument == "additive":
            comptype ="additive"
        elif argument == "geo_max":
            setsim="geo_max"
        elif argument == "avg_max":
            setsim="avg_max"
        elif argument == "nonbin":
            threshtype="nonbin"
        elif argument == "binary":
            threshtype="binary"
        elif argument == "weighted":
            threshtype="weighted"
        elif argument == "toyrun":
            toyrun = True
        elif argument == "use_cache":
            use_cache=True
        elif argument == "simcache":
            simcache=True
        elif argument == "filtered":
            filtered=True
        elif argument == "unfiltered":
            filtered=False
        elif argument == "lin":
            metric="lin"
        elif argument == "cosine":
            metric="cosine"
        elif argument == "binprob":
            metric="binprob"
        elif argument == "linadj":
            metric="linadj"
        else:
            matchobj = linadjaPATT.match(argument)
            if matchobj:
                adja=int(matchobj.group(1))
            else:
                matchobj = linadjbPATT.match(argument)
                if matchobj:
                    adjb=int(matchobj.group(1))
                else:
                    matchobj = thresholdPATT.match(argument)
                    if matchobj:
                        threshold = float(matchobj.group(1))

    return(testing,at_home,on_apollo,windows,filtered,comptype,metric,setsim,threshold,threshtype,toyrun,use_cache,adja,adjb,simcache)


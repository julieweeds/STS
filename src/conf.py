import re

thresholdPATT = re.compile('threshold=(.*)')

def configure(arguments):

#set defaults
#mode
    testing=False
#location
    at_home=False
    on_apollo=True
#feature_type

    windows=True
#filtered vectors
    filtered=True
#composition type
    comptype="additive"
#similarity metric
    metric="cosine"
#set similarity method
    setsim="avg_max"
#set similarity threshold
    threshold =1

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
        else:
            matchobj = thresholdPATT.match(argument)
            if matchobj:
                threshold = float(matchobj.group(1))

    return(testing,at_home,on_apollo,windows,filtered,comptype,metric,setsim,threshold)


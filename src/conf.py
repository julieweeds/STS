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

#override with command line arguments
    for argument in arguments:
        if argument == "windows":
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

    return(testing,at_home,on_apollo,windows,filtered,comptype,metric)


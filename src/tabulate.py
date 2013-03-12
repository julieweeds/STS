__author__ = 'Julie'

#read in results files and tabulate them
import sys
import glob
import re

###settings
at_home=True
on_apollo=False

#uni filenames
parent="/Users/juliewe/Documents/workspace/STS/data/results/"

if at_home:
    parent="C:/Users/Julie/Documents/GitHub/STS/results/"

if on_apollo:
    parent="/mnt/lustre/scratch/inf/juliewe/STS/data/results/"

if len(sys.argv)>1:
    resdir=sys.argv[1]+"/"
else:
    resdir=""

inputdir=parent+resdir+"*"

###regular expressions
feattypePATT = re.compile('Configuration set to windows = *(.*)')
comptypePATT = re.compile('Composition type = *(.*)')
simPATT = re.compile('Similarity metric = *(.*)')
setsimPATT = re.compile('Set similarity method = *(.*)')
simthresPATT = re.compile('Similarity threshold = *(.*)')
threshtypePATT = re.compile('Threshold type = *(.*)')
correlationPATT = re.compile('Average cross-validation correlation for (.*) with (.*) similarity is (.*), sd=(.*),')
confidencePATT=re.compile('.*confidence interval is (.*) +- (.*)')
averagePATT=re.compile('Average (.*) for (.*) data is (.*)')
###variables
feattype=""
comptype=""
simPATT=""
threshtype=""
setsim=""
threshold=0.0
correlation=0.0
average=0.0
sd=0.0
dataset=""
bound=0.0

###functions

def processfile(file):
    print "Processing "+file
    input = open(file,'r')
    for line in input:
        processline(line.rstrip())
    input.close()

def processline(line):
    #print line
    matchobj=feattypePATT.match(line)
    if matchobj:
        value = matchobj.group(1)
        if value=="True":
            feattype="windows"
        else:
            feattype="dependencies"
    matchobj=comptype.match(line)
    if matchobj:
        comptype=matchobj.group(1)
###main
print "Reading "+inputdir
filelist = glob.glob(inputdir)
for f in filelist:
    processfile(f)
__author__ = 'Julie'

#read in results files and tabulate them
import sys
import glob
import re


class Tabulate:
    ###settings

    def __init__(self,args):
        self.at_home=False
        self.on_apollo=False

    #uni filenames
        self.parent="/Users/juliewe/Documents/workspace/STS/data/results/"

        if self.at_home:
            self.parent="C:/Users/Julie/Documents/GitHub/STS/results/"

        if self.on_apollo:
            self.parent="/mnt/lustre/scratch/inf/juliewe/STS/data/results/"

        if len(args)>1:
            self.resdir=args[1]+"/"
        else:
            self.resdir=""

        self.inputdir=self.parent+self.resdir+"*"
        self.outname=self.parent+"tab_"+args[1]+".csv"
        self.outstream=open(self.outname,'w')

###regular expressions
        self.feattypePATT = re.compile('Configuration set to windows = *(.*)')
        self.comptypePATT = re.compile('Composition type = *(.*)')
        self.simPATT = re.compile('Similarity metric = *(.*)')
        self.setsimPATT = re.compile('Set similarity method = *(.*)')
        self.simthresPATT = re.compile('Similarity threshold = *(.*)')
        self.threshtypePATT = re.compile('Threshold type = *(.*)')
        self.correlationPATT = re.compile('Average cross-validation correlation for (.*) with (.*) similarity is (.*), sd=(.*),')
        self.confidencePATT=re.compile('(.*) confidence interval is (.*) \+\- (.*)')
        self.averagePATT=re.compile('Average (.*) for (.*) data is (.*)')
        ###variables
        self.feattype=""
        self.comptype=""
        self.simmetric=""
        self.threshtype=""
        self.setsim=""
        self.threshold=0.0
        self.correlation=0.0
        self.average=0.0
        self.sd=0.0
        self.dataset=""
        self.bound=0.0
        self.simtype=""

###functions

    def processdir(self):
        print "Reading "+self.inputdir
        filelist = glob.glob(self.inputdir)
        for f in filelist:
            self.processfile(f)
        self.outstream.close()

    def processfile(self,file):
        print "Processing "+file
        input = open(file,'r')
        for line in input:
            self.processline(line.rstrip())
        input.close()

    def processline(self,line):
        #print line
        matchobj=self.feattypePATT.match(line)
        if matchobj:
            value = matchobj.group(1)
            if value=="True":
                self.feattype="windows"
            else:
                self.feattype="dependencies"
        matchobj=self.comptypePATT.match(line)
        if matchobj:
            self.comptype=matchobj.group(1)
        matchobj=self.simPATT.match(line)
        if matchobj:
            self.simmetric=matchobj.group(1)
        matchobj=self.setsimPATT.match(line)
        if matchobj:
            self.setsim=matchobj.group(1)
        matchobj=self.simthresPATT.match(line)
        if matchobj:
            self.threshold=matchobj.group(1)
        matchobj=self.threshtypePATT.match(line)
        if matchobj:
            self.threshtype=matchobj.group(1)
        matchobj=self.averagePATT.match(line)
        if matchobj:
            self.simtype=matchobj.group(1)
            self.dataset=matchobj.group(2)
            self.average=matchobj.group(3)
            self.outstream.write("Average similarity, "+self.simtype+", "+self.dataset+", "+self.feattype+", "+self.comptype+", "+self.setsim+", "+self.simmetric+", "+self.threshtype+", "+self.threshold+", "+self.average+"\n")
        matchobj=self.correlationPATT.match(line)
        if matchobj:
            self.dataset=matchobj.group(1)
            self.simtype=matchobj.group(2)
            self.correlation=matchobj.group(3)
            self.sd=matchobj.group(4)
            self.outstream.write("Cross-validated correlation, "+self.simtype+", "+self.dataset+", "+self.feattype+", "+self.comptype+", "+self.setsim+", "+self.simmetric+", "+self.threshtype+", "+self.threshold+", "+self.correlation+", "+self.sd+", ")

        matchobj=self.confidencePATT.match(line)
        if matchobj:
            check=matchobj.group(2)
            self.bound=matchobj.group(3)
            if check==self.correlation:
                self.outstream.write(self.bound+"\n")
            else:
                print "Warning "+check+" is not equal to "+self.correlation




###main
if __name__ =="__main__":
    mytable=Tabulate(sys.argv)
    mytable.processdir()

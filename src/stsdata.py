__author__ = 'juliewe'

from sentpair import SentencePair
import re
import glob
import random
import numpy

class STSData:
    sidPATT = re.compile('.*<document>')
    sidendPATT = re.compile('.*</document>')
    wordPATT = re.compile('.*<word>(.*)</word>')
    lemmaPATT = re.compile('.*<lemma>(.*)</lemma>')
    fileidPATT= re.compile('.*STSinput(.*)/pair(.*)(.).tagged')
    gssetPATT = re.compile('.*STS.gs.(.*).txt')


    def __init__(self):
        self.pairset={} #label is setid_fileid
        self.vectordict={}
        self.sid=0
        self.filesread=0
        self.setid=""
        self.sentid=""
        self.label=""
        self.fileid=0
        self.simaverage={} #average similarities for different functions and subsets
        self.nosplits=-1 #number of cross-validation splits


    def readdata(self,parentname):
        dirlist = glob.glob(parentname+'/*')
        for d in dirlist:
            print "Reading "+d
            filelist = glob.glob(d+'/*')
            for f in filelist:
                #print "Reading "+f
                matchobj = STSData.fileidPATT.match(f)
                if matchobj:
                    self.setid=matchobj.group(1)
                    self.fileid=matchobj.group(2)
                    self.sentid=matchobj.group(3)
                    self.label=self.setid+"_"+self.fileid
                    #print "Setid: "+self.setid+" fileid: "+self.fileid
                else:
                    print "Error with filename, should contain id number "+f

                self.readdatafile(f)


    def readdatafile(self,filename):
        #print "Opening "+filename
        dstream = open(filename,'r')
        self.validfile=True
        for line in dstream:
            self.processline(line.rstrip())
        dstream.close()
        self.filesread+=1


    def processline(self,line):

 #       if self.validfile:
            #print "Processing "+line
            matchobj=STSData.sidPATT.match(line)
            if matchobj:
                if self.label in self.pairset:
                    self.currentpair=self.pairset[self.label]
                else:
                    self.currentpair=SentencePair(self.fileid,self.setid)

            else:
                matchobj=STSData.sidendPATT.match(line)
                if matchobj:
                        self.pairset[self.label]=self.currentpair
                        #print "Finished reading sentence - stored pair ..."
                else:
                    matchobj = STSData.wordPATT.match(line)
                    if matchobj:
                        word = matchobj.group(1)
                        self.currentpair.addword(word,self.sentid)
                    else:
                        matchobj = STSData.lemmaPATT.match(line)
                        if matchobj:
                            lemma = matchobj.group(1)
                            self.currentpair.addlemma(lemma,self.sentid)



    def averagesim(self,type,subset):
        label=type+"_"+subset
        print label
        if label in self.simaverage:
            average = self.simaverage[label]
        else:
            total =0
            count =0
            if subset=='all':
                for p in self.pairset.values():
                    total+=p.sim(type)
                    count+=1
            else :
                for p in self.pairset.values():
                    if (p.fid == subset):
                            total+=p.sim(type)
                            count+=1
            average = total/count
            self.simaverage[label]=average
            self.freq[label]=count
        return average

    def readgs(self,dirname):
        #read in gs scores and associate with sentence pairs
        filelist = glob.glob(dirname+'/*')
        for f in filelist:
            print "Reading "+f
            self.readgsfile(f)

    def readgsfile(self,filename):
        matchobj=STSData.gssetPATT.match(filename)
        if matchobj:
            gsid=matchobj.group(1)
        else:
            print "Error with gs file "+filename
            exit(1)
        pid =0
        instream=open(filename,'r')
        for line in instream:
            pid +=1
            self.processgsline(line.rstrip(),gsid,pid)
        instream.close()

    def processgsline(self,line,gsid,pid):
        label = gsid+"_"+str(pid)
        if label in self.pairset.keys():
            self.pairset[label].gs=float(line)
        else:
            print "Error "+label+" not found in pairset"
            exit(1)

    def split(self,num):
        print "Splitting data into subsets for cross-validation ..."
        self.nosplits=num
        for pair in self.pairset.values():
            rsplit = random.randint(1,num)
            pair.cvsplit = rsplit

    def fitpoly(self,subset,excl,type):
        #subset is a setid and excl is cv_split to exclude and type is similarity to correlate
        carryon=True
        fileid = 1
        correlationx=[]
        correlationy=[]
        while carryon==True:
            label = subset+"_"+str(fileid)
            if label in self.pairset.keys():
                #print "Checking for "+label
                if self.pairset[label].cvsplit==excl:
                    #ignore
                    #print "Ignoring"
                    fileid+=1
                else:
                    correlationy.append(self.pairset[label].gs)
                    correlationx.append(self.pairset[label].sim(type))
                    fileid+=1
            else:
                carryon=False #assumes pairs are consecutively numbered
        print len(correlationx),len(correlationy)

        return numpy.polyfit(numpy.array(correlationx),numpy.array(correlationy),2)



    def testread(self):
        print "Testing"
        print "Files read = "+str(self.filesread)
        print "Pairs stored = "+str(len(self.pairset))
        for p in self.pairset.values():
            p.display()

        print "Average lemma overlap is "+str(self.averagesim("lemma","all"))
        print "Average lemma overlap for europarl data is "+str(self.averagesim("lemma","SMTeuroparl"))
        print "Average lemma overlap for MSRpar data is "+str(self.averagesim("lemma","MSRpar"))
        print "Average lemma overlap for MSRvid data is "+str(self.averagesim("lemma","MSRvid"))

        print "Average gs overlap is "+str(self.averagesim("gs","all"))
        print "Average gs overlap for europarl data is "+str(self.averagesim("gs","SMTeuroparl"))
        print "Average gs overlap for MSRpar data is "+str(self.averagesim("gs","MSRpar"))
        print "Average gs overlap for MSRvid data is "+str(self.averagesim("gs","MSRvid"))
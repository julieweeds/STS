__author__ = 'juliewe'

from sentpair import SentencePair
import re
import glob

class STSData:
    sidPATT = re.compile('.*<document>')
    sidendPATT = re.compile('.*</document>')
    wordPATT = re.compile('.*<word>(.*)</word>')
    lemmaPATT = re.compile('.*<lemma>(.*)</lemma>')
    fileidPATT= re.compile('.*STSinput(.*)/pair(.*)(.).tagged')


    def __init__(self):
        self.pairset={}
        self.vectordict={}
        self.sid=0
        self.filesread=0
        self.setid=""
        self.sentid=""
        self.label=""
        self.fileid=0
        self.simaverage={}


    def readdata(self,parentname):
        dirlist = glob.glob(parentname+'/*')
        for d in dirlist:
            filelist = glob.glob(d+'/*')
            for f in filelist:
                #print f
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
        self.testread()


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
                    total+=p.lemmasim()
                    count+=1
            else :
                for p in self.pairset.values():
                    if (p.fid == subset):
                            total+=p.lemmasim()
                            count+=1
            average = total/count
            self.simaverage[label]=average
        return average

    def testread(self):
        print "Testing"
        print "Files read = "+str(self.filesread)
        print "Pairs stored = "+str(len(self.pairset))
        for p in self.pairset.values():
            p.display()

        print "Average lemma overlap is "+str(self.averagesim("lemma","all"))
        print "Average lemma overlap for europarl data is "+str(self.averagesim("lemma","europarl"))
        print "Average lemma overlap for MSRpar data is "+str(self.averagesim("lemma","MSRpar"))
        print "Average lemma overlap for MSRvid data is "+str(self.averagesim("lemma","MSRvid"))

__author__ = 'juliewe'

from sentpair import SentencePair
from wordvector import WordVector
import re
import glob
import random
import numpy
import scipy.stats as stats
import sys
import scipy.sparse as sparse

#import matplotlib.pyplot as plt

class STSData:
    sidPATT = re.compile('.*<document>')
    sidendPATT = re.compile('.*</document>')
    wordPATT = re.compile('.*<word>(.*)</word>')
    lemmaPATT = re.compile('.*<lemma>(.*)</lemma>')
    posPATT = re.compile('.*<POS>(.).*</POS>')
    fileidPATT= re.compile('.*STSinput(.*).pair(.*)(.).tagged')
    gssetPATT = re.compile('.*STS.gs.(.*).txt')
    wordposPATT = re.compile('(.*)/(.*)')
    methods = ["additive","multiplicative"]

    def __init__(self,graphson,testing,windows):
        self.pairset={} #label is setid_fileid
        self.vectordict={} #mapping from (word,POS) tuples to wordvectors
        self.sid=0
        self.filesread=0
        self.setid=""
        self.sentid=""
        self.label=""
        self.fileid=0
        self.simaverage={} #average similarities for different functions and subsets
        self.nosplits=-1 #number of cross-validation splits
        self.show=graphson
        self.updated=0
        self.testing=testing
        self.comp=""
        self.metric=""
        self.allfeatures={} #dictionary of all feature dimenesions
        self.fkeys=[] #list (to be sorted) of all features to
        self.fk_idx={} #feature --> dimension
        self.dim=0
        WordVector.windows=windows

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
            if self.testing == True: break
        self.vectordict_init()


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
                    self.currentpair=SentencePair(self.fileid,self.setid,self.testing)

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
                        else:
                            matchobj=STSData.posPATT.match(line)
                            if matchobj:
                                pos = matchobj.group(1)
                                self.currentpair.addpos(pos,self.sentid)



    def averagesim(self,type,subset):
        label=type+"_"+subset
        #print label
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
                            #print "average sim "+str(p.sim(type))
                            count+=1
                            #print count

            average = total/count
            self.simaverage[label]=average
        return average

    def readgs(self,dirname):
        #read in gs scores and associate with sentence pairs
        filelist = glob.glob(dirname+'/*')
        for f in filelist:
            print "Reading "+f
            self.readgsfile(f)
            if self.testing == True: break

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
        #print "Splitting data into subsets for cross-validation ..."
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
        #print len(correlationx),len(correlationy)
        x=numpy.array(correlationx)
        y=numpy.array(correlationy)
        thispoly= numpy.poly1d(numpy.polyfit(x,y,1))

        if excl==1 and self.show == True:
            pr=stats.spearmanr(x,y)
            mytitle="Regression line for: "+subset+":"+str(excl)+":"+type
            self.showpoly(x,y,thispoly,mytitle,pr,1,5)

        return thispoly

    def showpoly(self,x,y,poly,title,pr,xl,yl):
        xp=numpy.linspace(0,xl,100)
        plt.plot(x,y,'.',xp,poly(xp),'-')
        plt.ylim(0,yl)
        plt.title(title)
        mytext1="srcc = "+str(pr[0])
        mytext2="p = "+str(pr[1])
        plt.text(0.05,yl*0.9,mytext1)
        plt.text(0.05,yl*0.8,mytext2)
        plt.show()

    def testpoly(self,subset,excl,type):

        thispoly = self.fitpoly(subset,excl,type)
        #print thispoly

        fileid =1
        predictions=[]
        gs=[]
        carryon=True
        #noones=0
        #nozeroes=0

        while carryon == True:
            label = subset+"_"+str(fileid)
            if label in self.pairset.keys():
                if self.pairset[label].cvsplit== excl:
                    #if self.pairset[label].sim(type)==1:
                      #  noones+=1
                    #if self.pairset[label].sim(type)==0:
                      #  nozeroes+=1
                    predictions.append(thispoly(self.pairset[label].sim(type)))
                    gs.append(self.pairset[label].gs)
                    fileid+=1
                else:
                    #ignore
                    fileid+=1
            else:
                carryon = False
        #now to compute spearman correlation coefficient between gs and predictions

        x=numpy.array(predictions)
        y=numpy.array(gs)
        #print len(x),len(y)
        #sumzeroone=nozeroes+noones
        #print nozeroes, noones, sumzeroone
        #print x,y
        pr = stats.spearmanr(x,y)
        if excl==1 and self.show==True:
            mytitle="Correlation for: "+subset+": "+str(excl)+": "+type
            self.showpoly(x,y,numpy.poly1d(numpy.polyfit(x,y,1)),mytitle,pr,5,5)
        #print pr
        return pr


    def testread(self):
        print "Testing"
        print "Files read = "+str(self.filesread)
        #print "Pairs stored = "+str(len(self.pairset))
        #for p in self.pairset.values():
        #    p.display()



        #print "Average lemma overlap of content words is "+str(self.averagesim("lemma_content","all"))
        print "Average lemma overlap of content words for europarl data is "+str(self.averagesim("lemma_content","SMTeuroparl"))
        print "Average lemma overlap of content words for MSRpar data is "+str(self.averagesim("lemma_content","MSRpar"))
        print "Average lemma overlap of content words for MSRvid data is "+str(self.averagesim("lemma_content","MSRvid"))

        #print "Average gs overlap is "+str(self.averagesim("gs","all"))
        #print "Average gs overlap for europarl data is "+str(self.averagesim("gs","SMTeuroparl"))
        print "Average gs overlap for MSRpar data is "+str(self.averagesim("gs","MSRpar"))
        #print "Average gs overlap for MSRvid data is "+str(self.averagesim("gs","MSRvid"))

        print "Average composed sentence similarity for europarl data is "+str(self.averagesim("sent_comp","SMTeuroparl"))
        print "Average composed sentence similarity for MSRpar data is "+str(self.averagesim("sent_comp","MSRpar"))
        print "Average composed sentence similarity for MSRvid data is "+str(self.averagesim("sent_comp","MSRvid"))

    def vectordict_init(self):
        for pair in self.pairset.values():
            for sent in ['A','B']:
               for item in pair.returncontentlemmas(sent):
                    if item in self.vectordict:
                        self.check=True
                    else:
                        self.vectordict[item]=WordVector(item)
        print "Vector dictionary initialised with "+str(len(self.vectordict.keys()))+" words"

    def readvectors(self,vectorfilename):
        print"Reading vector file"
        linesread=0
        instream=open(vectorfilename,'r')
        for line in instream:
            self.processvectorline(line.rstrip())
            linesread+=1
            #if (self.testing==True and linesread>1000):
             #   break
            if (linesread%1000 == 0):
                print "Read "+str(linesread)+" lines and updated "+str(self.updated)+" vectors"
                sys.stdout.flush()

        print "Read "+str(linesread)+" lines and updated "+str(self.updated)+" vectors"
        coverage=self.updated*100.0/len(self.vectordict.keys())
        print "Vector dictionary coverage is "+str(coverage)+"%"
        instream.close()
        print "Compressing vector dictionary representation"
        self.makematrix()
        print "Finished sparse array generation"

    def processvectorline(self,line):
        featurelist=line.split('\t')
        matchobj = STSData.wordposPATT.match(featurelist[0])
        if matchobj:
            wordpos=(matchobj.group(1),matchobj.group(2))
        else:
            print "Error with vector file matching "+featurelist[0]
            #this could be "__FILTERED" so ignore line and carry on
            return

        #if len(featurelist)>WordVector.dim:
         #   WordVector.dim=len(featurelist)
        if wordpos in self.vectordict.keys():
            featurelist.reverse()
            featurelist.pop()
            self.updatevector(wordpos,featurelist)
            self.updated+=1

    def updatevector(self,wordpos,featurelist):
        while(len(featurelist)>0):
            f=featurelist.pop()
            sc=featurelist.pop()
            added=self.vectordict[wordpos].addfeature(f,sc)
            if added:
                self.allfeatures[f]=1
        self.vectordict[wordpos].length=pow(self.vectordict[wordpos].length2,0.5)

    def makematrix(self):
        self.fkeys =self.allfeatures.keys()
        self.fkeys.sort()
        for i in range(len(self.fkeys)):
            self.fk_idx[self.fkeys[i]] = i
        del self.fkeys
        del self.allfeatures
        self.dim=len(self.fk_idx)
        print "Dimensionality is "+ str(self.dim)
        self.makearrays()

    def makearrays(self):
        #need to convert a word vector which stores a dictionary of features into a sparse array based on fk_idx
        for wordvector in self.vectordict.values():

            temparray = numpy.zeros(self.dim)
            for feature in wordvector.vector.keys():

                col=self.fk_idx[feature]
                score=wordvector.vector[feature]
#
                temparray[col]=score
           # print temparray
            wordvector.array = sparse.csr_matrix(temparray)
            #print wordvector.array.data
           # print "Converted "+wordvector.word+"/"+wordvector.pos


#    def composeall(self,method,metric):
#        for pair in self.pairset.values():
#            pair.compose(self.vectordict,method,metric) # compose and sentence sim each pair of sentences
#            sys.stdout.flush()


    def composeall_faster(self,method,metric):
        self.comp=method
        self.metric=metric
        if method in STSData.methods:
            donepairs=0
            for pair in self.pairset.values():
                self.compose_faster(pair)
                sys.stdout.flush()
                pair.getsentsim()
                donepairs+=1
                #if donepairs%10 ==0:
                 #   print "Completed composition and similarity calculations for "+str(donepairs)+" pairs"
                 #   break


        else:
            print "Unknown method of composition "+method


    def compose_faster(self,pair):
        pair.comp=self.comp
        pair.metric=self.metric
        for sent in ['A','B']:
            lemmalist=pair.returncontentlemmas(sent) #get all lemmas in sentence
            pair.sentvector[sent]=WordVector((sent,'S'))
            if pair.comp == "multiplicative":
                pair.sentvector[sent].array=sparse.csr_matrix(numpy.ones(self.dim)) #initialise sentence array as ones
            else:  #assume additive
                pair.sentvector[sent].array=sparse.csr_matrix(numpy.zeros(self.dim)) #initialise sentence array as zeroes

            #print lemmalist
            for tuple in lemmalist:
                if tuple in self.vectordict:
                    if len(self.vectordict[tuple].vector)>0:  #only compose non-zero vectors
                    #     print tuple, "yes"
                        if pair.comp == "multiplicative":
                            #pair.sentvector[sent].mult_array(self.vectordict[tuple])
                            pair.sentvector[sent].array=pair.sentvector[sent].array.multiply(self.vectordict[tuple].array)
                        else: #assume additive
                            #pair.sentvector[sent].add_array(self.vectordict[tuple])
                            pair.sentvector[sent].array=pair.sentvector[sent].array + self.vectordict[tuple].array
            #pair.sentvector[sent].display()
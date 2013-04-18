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
import operator
from wordvector import update_params

#import matplotlib.pyplot as plt

class STSData:
    sidPATT = re.compile('.*<document>')
    sidendPATT = re.compile('.*</document>')
    wordPATT = re.compile('.*<word>(.*)</word>')
    lemmaPATT = re.compile('.*<lemma>(.*)</lemma>')
    posPATT = re.compile('.*<POS>(.).*</POS>') #only first char of POS
    fileidPATT= re.compile('.*input(.*).pair(.*)(.).tagged')
    gssetPATT = re.compile('.*.gs.(.*).txt')
    wordposPATT = re.compile('(.*)/(.)') #only first char of POS
    methods = ["additive","multiplicative"]
    setmethods = ["avg_max","geo_max"]
    simthreshold = 1.0
    minsim = 0.001
    threshtype="nonbin"
    seed = 666


    def __init__(self,graphson,testing,windows,threshold,threshtype,verbose,adja,adjb):
        self.pairset={} #label is setid_fileid
        self.vectordict={} #mapping from (word,POS) tuples to wordvectors
        self.wordcounts={} #count the number of times each (word,POS) tuple occurs in data for analysis
        self.uncovered={} #store words and counts not in thesaurus
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
        self.setsim=""
        self.allfeatures={} #dictionary of all feature dimenesions
        self.fkeys=[] #list (to be sorted) of all features to
        self.fk_idx={} #feature --> dimension
        self.dim=0
        WordVector.windows=windows
        STSData.simthreshold=threshold
        STSData.threshtype=threshtype
        self.verbose = verbose
        self.adja=adja
        self.adjb=adjb

    def setseed(self):
        random.seed(STSData.seed)#for reproducible results

    def readdata(self,parentname):
        dirlist = glob.glob(parentname+'/*')
        if len(dirlist)==0:
            print "Aborting due to empty data directory "+parentname
            exit(1)
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
                    #print "Self.label = "+self.label
                    #print "Setid: "+self.setid+" fileid: "+self.fileid
                else:
                    print "Error with filename, should contain id number "+f

                self.readdatafile(f)
            if self.testing == True: break
#        self.removeduplicates()
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


    def removeduplicates(self):
        #remove pairs from pairset where the two sentences are identical
        #however, this needs work as the system assumes consecutive numbering of pairs
        total={}
        dups={}
        for key in self.pairset.keys():
            pair=self.pairset[key]
            fileid=pair.fid
            if fileid in total.keys():
                total[fileid]=total[fileid]+1
            else:
                total[fileid]=1
            if pair.isidentical():
                if fileid in dups.keys():
                    dups[fileid]=dups[fileid]+1
                else:
                    dups[fileid]=1
                print "Removing duplicate:"
                pair.display()
                del self.pairset[key]
        for fileid in total.keys():
            if fileid in dups.keys():
                top=dups[fileid]
            else:
                top=0.0
            percent = top*100.0/total[fileid]
            print "For "+fileid+" removed "+str(top)+" duplicates out of "+str(total[fileid])+" pairs: "+str(percent)+"%"


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
            print "WARNING "+label+" not found in pairset"


    def split(self,num):
        #print "Splitting data into subsets for cross-validation ..."
        self.nosplits=num
        for pair in self.pairset.values():
            pair.cvsplit = random.randint(1,num)

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

        #to generate and test regression line

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

        #pr = stats.spearmanr(x,y)
        pr=stats.spearmanr(x,y)
        if excl==1 and self.show==True:
            mytitle="Correlation for: "+subset+": "+str(excl)+": "+type
            self.showpoly(x,y,numpy.poly1d(numpy.polyfit(x,y,1)),mytitle,pr,5,5)
            #print pr
        return pr

    def testpoly2(self,subset,excl,type1, type2):

        #to generate and compare 2 regression lines

        thispoly1 = self.fitpoly(subset,excl,type1)
        thispoly2 = self.fitpoly(subset,excl,type2)
        #print thispoly

        fileid =1
#        predictions1=[]
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
 #                   predictions1.append(thispoly1(self.pairset[label].sim(type1)))
                    predictions.append(thispoly2(self.pairset[label].sim(type2)))
                    gs.append(self.pairset[label].gs)
                    error1 = thispoly1(self.pairset[label].sim(type1))-self.pairset[label].gs
                    error2 = thispoly2(self.pairset[label].sim(type2))-self.pairset[label].gs
                    diff=pow(error2,2)-pow(error1,2)
                    self.pairset[label].totaldiff+=diff
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



    def testread(self,sim,dataset):

        #print "Testing"
        #print "Files read = "+str(self.filesread)
        if self.testing:
            print "Pairs stored = "+str(len(self.pairset))
            for p in self.pairset.values():
                p.display()
        #else:
        #    for p in self.pairset.values():
        #        p.display()


        #print "Average lemma overlap of content words is "+str(self.averagesim("lemma_content","all"))
        print "Average "+sim+" for "+dataset+" data is "+str(self.averagesim(sim,dataset))


    def vectordict_init(self):
        for pair in self.pairset.values():
            for sent in ['A','B']:
               for item in pair.returncontentlemmas(sent):
                    if item in self.vectordict:
                        #self.check=True
                        self.wordcounts[item]+=1 #count how many times each item occurs for analysis
                    else:
                        self.vectordict[item]=WordVector(item)
                        self.wordcounts[item]=1
        print "Vector dictionary initialised with "+str(len(self.vectordict.keys()))+" words"

    def compute_token_coverage(self):
        total=0
        covered=0
        for word in self.wordcounts.keys():
            freq=self.wordcounts[word]
            total+=freq
            if len(self.vectordict[word].vector)>0:
                covered+=freq
            else:
                self.uncovered[word]=freq
        coverage=covered*100.0/total
        self.analyse_uncovered()
        return coverage

    def analyse_uncovered(self):
        #outlog=open('logfile','w')
        poscounts={} #count how many uncovered in each POS
        for tuple in self.uncovered.keys():
            (word,pos)=tuple
            #outlog.write(word+"/"+pos+"\t"+str(self.uncovered[tuple])+"\n")
            if pos in poscounts.keys():
                poscounts[pos]+=1
            else:
                poscounts[pos]=1

        #outlog.close()
        total=0
        for pos in poscounts.keys():

            print "Uncovered by POS:-"
            print pos+" : " + str(poscounts[pos])
            total+=poscounts[pos]
        print "Total "+str(total
)

    def readvectors(self,vectorfilename,cachename):
        print"Reading vector file "+vectorfilename
        linesread=0
        instream=open(vectorfilename,'r')
        for line in instream:
            self.processvectorline(line.rstrip())
            linesread+=1
            #if (self.testing==True and linesread>1000):
             #   break
            if (linesread%10000 == 0):
                print "Read "+str(linesread)+" lines and updated "+str(self.updated)+" vectors"
                sys.stdout.flush()

        print "Read "+str(linesread)+" lines and updated "+str(self.updated)+" vectors"
        coverage=self.updated*100.0/len(self.vectordict.keys())
        print "Vector dictionary type coverage is "+str(coverage)+"%"
        print "Token coverage is "+str(self.compute_token_coverage())+"%"
        instream.close()
        if cachename==vectorfilename:
            print "Vector cache up to date"
        else:
            print "Writing vector cache"
            self.makecache(cachename)
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
        update_params(self.dim,self.adja,self.adjb)
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


    def composeall_faster(self,method,metric): #compose each sentence in each pair and compute similarity of pair
        self.comp=method
        self.metric=metric
        if method in STSData.methods:
            donepairs=0
            for pair in self.pairset.values():
                self.compose_faster(pair)
                sys.stdout.flush()
                pair.getsentsim()
                donepairs+=1
                if donepairs%500 ==0:
                    print "Completed composition and similarity calculations for "+str(donepairs)+" pairs"
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

    def set_simall(self,method,metric):
        self.metric=metric
        self.setsim=method
        if self.setsim in STSData.setmethods:
            donepairs=0
            for pair in self.pairset.values():
                self.set_sim(pair)
                sys.stdout.flush()
                donepairs+=1
                #if self.testing:
                if donepairs%500 ==0:
                    print "Completed set similarity calculations for "+str(donepairs)+" pairs"
                       #break


        else:
            print "Unknown method of set similarity "+self.setsim

    def set_sim(self,pair):
        pair.metric=self.metric
        pair.setsim=self.setsim
        label="set_"+pair.metric+"_"+pair.setsim
        if label in pair.sentsim.keys():
            sim = pair.sentsim[label]
        else:
            lemmalistA=pair.returncontentlemmas('A') #get all content lemmas in sentence A
            lemmalistB=pair.returncontentlemmas('B') #get all content lemmas in sentence B

            #compute set sim A->B
            (total1,count1)= self.set_sim1(lemmalistA,lemmalistB)
            #sim1=self.set_sim1(lemmalistA,lemmalistB)
            #compute set sim B->A
            (total2,count2)= self.set_sim1(lemmalistB,lemmalistA)
            #sim2=self.set_sim1(lemmalistB,lemmalistA)
            #compute arithmetic mean
            if self.setsim=="geo_max":
                sim=pow(total1*total2,1.0/(count1+count2))
            else:
                sim =(total1+total2)/(count1+count2)
            #sim =(sim1+sim2)/2
            pair.sentsim[label]=sim
        if self.verbose:
            print (pair.toString("sent_set"))
        return sim

    def set_sim1(self,lemmalistA,lemmalistB): #asymmetric set sim from A to B

        if self.setsim=="geo_max":
            total =1.0
        else:
            total=0.0
        count=0.0
        for lemmaA in lemmalistA:
            maxsim=STSData.minsim #smoothing - if no lemmas in B have entry or any similarity to this lemma
            maxlemma=("$!","$!")
            if lemmaA in self.vectordict:
                if lemmaA in lemmalistB: #check if word is actually in the other sentence
                    maxsim=1.0
                    maxlemma=lemmaA
                else:
                    if len(self.vectordict[lemmaA].vector)>0: #only consider non-zero vectors

                        for lemmaB in lemmalistB: #find maximally similar lemma in B
                            if lemmaB in self.vectordict:
                                if len(self.vectordict[lemmaB].vector)>0:
                                    thissim=self.vectordict[lemmaA].findsim(self.vectordict[lemmaB],self.metric)
                                    if thissim>1:
                                        print lemmaA, lemmaA, thissim
                                    if(thissim>maxsim):
                                        maxsim=thissim
                                        maxlemma=lemmaB


            else:
                print "Vector dictionary error for ", lemmaA
            if maxsim < STSData.simthreshold: #similarity threshold
                if STSData.threshtype=="weighted":
                     maxsim = maxsim/STSData.simthreshold #weighted thresholding
                else:
                    maxsim = STSData.minsim # minimum similarity i.e., ignore in binary or non-binary case
                    maxlemma=("$!",maxlemma)
            else:
                if STSData.threshtype=="nonbin":
                    maxsim = maxsim * 1.0 # leave similarity as it is for non-binary threshold
                else:
                    maxsim = 1.0 #in - weighted thresholding or binary threshold

            if self.setsim=="geo_max":
                total = total * maxsim
            else :
                total = total + maxsim
            count +=1
            if self.verbose:
                (wordA,posA)=lemmaA
                (wordB,posB)=maxlemma
                print wordA+"/"+posA+ " : "+wordB+"/"+posB+" : "+str(maxsim)

#        if self.setsim=="geo_max":
#            sim = pow(total,(1.0/count))
#        else:
#            sim = total/count
        return (total,count)

    def ranksent(self,f,type,repeats,outstream):
        ranking=[]
        for key in self.pairset.keys():#create unordered list of (key,score) pairs
            if self.pairset[key].fid == f:
                score = self.pairset[key].totaldiff/repeats
                ranking.append((key,score))
        #sort list based on score
        ranking.sort(key=operator.itemgetter(1))
        rank=1
        for (key,score) in ranking:
            outstream.write(str(rank)+" : "+str(score)+"\n")
            outstream.write(self.pairset[key].toString(type))
            rank+=1

    def makecache(self,filename):
        outstream = open(filename,'w')
        for vector in self.vectordict.values():
            if len(vector.vector)>0:
                vector.makecache(outstream)
        outstream.close()

    def inspect(self):
        print "Pairs stored = "+str(len(self.pairset))
        #for p in self.pairset.values():
         #   print(p.toString("sent_set"))
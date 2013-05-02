__author__ = 'juliewe'


from wordvector import WordVector
from wordvector import update_params
import re
import sys
import numpy
import scipy.sparse as sparse
#import matplotlib.pyplot as plt
import scipy.stats as stats

class Thesaurus:

    wordposPATT = re.compile('(.*)/(.)') #only first char of POS
    byblo = False # byblo neighbours file or appthes generated from vector file

    def __init__(self,vectorfilename,simcachefile,simcache,windows,k,adja,adjb,compress):
        self.vectorfilename=vectorfilename
        self.simcachefile=simcachefile
        self.simcache=simcache
        self.thisvector=""
        self.vectordict={} #dictionary of vectors
        self.allfeatures={} #dictionary of all feature dimensions
        self.updated=0
        self.fkeys=[] #list (to be sorted) of all features to
        self.fk_idx={} #feature --> dimension
        self.dim=0
        WordVector.windows=windows
        self.k=k
        self.adja=adja
        self.adjb=adjb
        self.filter=False
        self.filterwords=[]
        self.compress=compress #whether to generate sparse vector representation for efficient sim calcs

    def readvectors(self):
        if self.simcache:
            #don't bother reading in vectors - just need simcache
            same=True
        else:
            print"Reading vector file "+self.vectorfilename
            linesread=0
            instream=open(self.vectorfilename,'r')
            for line in instream:
                self.processvectorline(line.rstrip())
                linesread+=1
                if (linesread%10000 == 0):
                    print "Read "+str(linesread)+" lines and updated "+str(self.updated)+" vectors"
                    sys.stdout.flush()

            print "Read "+str(linesread)+" lines and updated "+str(self.updated)+" vectors"
            instream.close()
            if self.compress:
                print "Compressing vector dictionary representation"
                self.makematrix()
                print "Finished sparse array generation"

    def processvectorline(self,line):
        featurelist=line.split('\t')
        matchobj = Thesaurus.wordposPATT.match(featurelist[0])
        if matchobj:
            wordpos=(matchobj.group(1),matchobj.group(2))
        else:
            print "Error with vector file matching "+featurelist[0]
            #this could be "__FILTERED" so ignore line and carry on
            return

            #if len(featurelist)>WordVector.dim:
            #   WordVector.dim=len(featurelist)

        self.vectordict[wordpos]=WordVector(wordpos) #initialise WordVector in vector dictionary

        featurelist.reverse() #reverse list so can pop features and scores off
        featurelist.pop() #take off last item which is word itself
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

    def readsims(self):

        print"Reading sim file "+self.simcachefile
        linesread=0
        instream=open(self.simcachefile,'r')
        for line in instream:
            self.processsimline(line.rstrip())
            linesread+=1
            if (linesread%100 == 0):
                print "Read "+str(linesread)+" lines and updated "+str(self.updated)+" similarity vectors"
                sys.stdout.flush()
                #return

        print "Read "+str(linesread)+" lines and updated "+str(self.updated)+" vectors"
        instream.close()


    def processsimline(self,line):
        featurelist=line.split('\t')
        matchobj = Thesaurus.wordposPATT.match(featurelist[0])
        if matchobj:
            wordpos=(matchobj.group(1),matchobj.group(2))
        else:
            print "Error with vector file matching "+featurelist[0]
            return


        #self.vectordict[wordpos]=WordVector(wordpos) #initialise WordVector in vector dictionary
        (word,pos)=wordpos
        add=True
        if self.filter:
            if word+"/"+pos in self.filterwords:
                add=True
            else:
                add=False

        if add:
            self.thisvector=WordVector(wordpos)

            featurelist.reverse() #reverse list so can pop features and scores off
            featurelist.pop() #take off last item which is word itself
            if Thesaurus.byblo:
                #no extra fields
                check=True
            else:
                self.thisvector.width=float(featurelist.pop())
                self.thisvector.length=float(featurelist.pop())
            self.updatesimvector(wordpos,featurelist)
            self.thisvector.topk(self.k)
            self.vectordict[wordpos]=self.thisvector
            #self.vectordict[wordpos].displaysims()
            self.updated+=1

    def updatesimvector(self,wordpos,featurelist):
        while(len(featurelist)>0):
            f=featurelist.pop()
            sc=featurelist.pop()
            self.thisvector.allsims[f]=float(sc)


    def makematrix(self):
        self.fkeys =self.allfeatures.keys()
        self.fkeys.sort()
        for i in range(len(self.fkeys)):
            self.fk_idx[self.fkeys[i]] = i
        del self.fkeys
        del self.allfeatures
        self.dim=len(self.fk_idx)
        print "Dimensionality is "+ str(self.dim)
        update_params(self.dim,self.adja,self.adjb)
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

    def allpairssims(self,metric):
        if self.simcache:
            #read in from sim cache
            self.readsims()
            #outstream=open(self.simcachefile,'w')
            #for wordvectorA in self.vectordict.values():
            #    wordvectorA.outputsims(outstream)
            #outstream.close()
        else:
            outstream=open(self.simcachefile,'w')
            #compute all pairs sims and write sim cache
            done =0
            for wordvectorA in self.vectordict.values():
                wordvectorA.allsims={}
                for wordvectorB in self.vectordict.values():
                    if wordvectorA.equals(wordvectorB):
                        #ignore
                        same =True
                    else:
                        label = wordvectorB.word+"/"+wordvectorB.pos

                        sim=wordvectorA.findsim(wordvectorB,metric)
                        if sim<0:
                            wordvectorA.debug=True
                            wordvectorA.findsim(wordvectorB,metric)
                        if sim>1:
                            wordvectorA.debug=True
                            wordvectorA.findsim(wordvectorB,metric)
                        wordvectorA.allsims[label]=sim
                wordvectorA.outputtopk(outstream,self.k)

                done+=1
                if done%100==0: print "Completed similarity calculations for "+str(done)+" words"


        for wordvectorA in self.vectordict.values():
            wordvectorA.analyse()

    def outputsim(self,wordA,wordB,metric):
        sim =-1
        if wordA in self.vectordict.keys():
            vectorA = self.vectordict[wordA]

            if wordB in self.vectordict.keys():
                vectorB = self.vectordict[wordB]
                sim = vectorA.findsim(vectorB,metric)
                print "Similarity between "+vectorA.word+"/"+vectorA.pos+" and "+vectorB.word +"/"+vectorB.pos+" is "+str(sim)
                print "("+str(vectorA.width) + ", "+str(vectorB.width)+")"

            else:
                (word,pos)=wordB
                print word+"/"+pos +" not in dictionary"

        else:
            (word,pos)=wordA
            print word+"/"+pos +" not in dictionary"


    def topk(self,k):
        #retain top k neighbours for each word
        for thisvector in self.vectordict.values():
            thisvector.topk(k)

    def topsim(self,sim):
        #retain similarities over sim threshold
        for thisvector in self.vectordict.values():
            #print thisvector,sim
            thisvector.keeptopsim(sim)

    def displayneighs(self,word,k):
        if word in self.vectordict.keys():

            vector=self.vectordict[word]
            vector.topk(k)
            vector.displaysims()
        else:
            (word,pos)=word
            print word+"/"+pos + " not in dictionary"

    def analyse(self):
        totaltop=0.0
        totalavg=0.0
        squaretop=0.0
        squareavg=0.0
        count=0
        correlationx=[]
        correlationy1=[]
        correlationy2=[]
        totalsd = 0.0
        squaresd=0.0

        for wordvectorA in self.vectordict.values():
            count+=1
            totaltop+=wordvectorA.topsim
            squaretop+=wordvectorA.topsim*wordvectorA.topsim
            totalavg+=wordvectorA.avgsim
            squareavg+=wordvectorA.avgsim*wordvectorA.avgsim
            totalsd+=wordvectorA.sd
            squaresd+=wordvectorA.sd * wordvectorA.sd
            correlationx.append(float(wordvectorA.width))
            correlationy1.append(float(wordvectorA.topsim))
            correlationy2.append(float(wordvectorA.avgsim))

        avgtop=totaltop/count
        sdtop=pow(squaretop/count - avgtop*avgtop,0.5)
        avgavg=totalavg/count
        sdavg=pow(squareavg/count-avgavg*avgavg,0.5)
        avgsd=totalsd/count
        sdsd=pow(squaresd/count-avgsd*avgsd,0.5)

        print "Top similarity: average = "+str(avgtop)+" sd = "+str(sdtop)
        print "average similarity: average = "+str(avgavg)+" sd = "+str(sdavg)
        print "SD similarity: average = "+str(avgsd)+" sd = "+str(sdsd)


        #print correlationx
        #print correlationy1
        x=numpy.array(correlationx)
        y=numpy.array(correlationy1)

        #print x
        #print y

        thispoly= numpy.poly1d(numpy.polyfit(x,y,1))


        pr=stats.spearmanr(x,y)
        mytitle="Regression line for width and top similarity"
      #  self.showpoly(x,y,thispoly,mytitle,pr,1,1)
        print "SRCC for width and top similarity is "+str(pr[0])+" ("+str(pr[1])+")"
        print thispoly

        x=numpy.array(correlationx)
        y=numpy.array(correlationy2)
        thispoly= numpy.poly1d(numpy.polyfit(x,y,1))


        pr=stats.spearmanr(x,y)
        mytitle="Regression line for width and average similarity"
     #   self.showpoly(x,y,thispoly,mytitle,pr,1,1)
        print "SRCC for width and average similarity is "+str(pr[0])+" ("+str(pr[1])+")"
        print thispoly

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

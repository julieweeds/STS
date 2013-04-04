__author__ = 'juliewe'


from wordvector import WordVector
import re
import sys
import numpy
import scipy.sparse as sparse
#import matplotlib.pyplot as plt
import scipy.stats as stats

class Thesaurus:

    wordposPATT = re.compile('(.*)/(.)') #only first char of POS

    def __init__(self,vectorfilename,simcachefile,simcache):
        self.vectorfilename=vectorfilename
        self.simcachefile=simcachefile
        self.simcache=simcache
        self.vectordict={} #dictionary of vectors
        self.allfeatures={} #dictionary of all feature dimensions
        self.updated=0
        self.fkeys=[] #list (to be sorted) of all features to
        self.fk_idx={} #feature --> dimension
        self.dim=0

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
            if (linesread%10000 == 0):
                print "Read "+str(linesread)+" lines and updated "+str(self.updated)+" vectors"
                sys.stdout.flush()

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


        self.vectordict[wordpos]=WordVector(wordpos) #initialise WordVector in vector dictionary

        featurelist.reverse() #reverse list so can pop features and scores off
        featurelist.pop() #take off last item which is word itself
        self.vectordict[wordpos].width=featurelist.pop()
        self.vectordict[wordpos].length=featurelist.pop()
        self.updatesimvector(wordpos,featurelist)
        self.updated+=1

    def updatesimvector(self,wordpos,featurelist):
        while(len(featurelist)>0):
            f=featurelist.pop()
            sc=featurelist.pop()
            self.vectordict[wordpos].allsims[f]=sc


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

    def allpairssims(self):
        if self.simcache:
            #read in from sim cache
            self.readsims(self.simcachefile)
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
                        label = wordvectorB.word+"_"+wordvectorB.pos
                        wordvectorA.allsims[label]=wordvectorA.cossim_array(wordvectorB)

                wordvectorA.outputsims(outstream)

                done+=1
                if done%100==0: print "Completed similarity calculations for "+str(done)+" words"


        for wordvectorA in self.vectordict.values():
            wordvectorA.analyse()


    def analyse(self):
        totaltop=0.0
        totalavg=0.0
        squaretop=0.0
        squareavg=0.0
        count=0
        correlationx=[]
        correlationy1=[]
        correlationy2=[]

        for wordvectorA in self.vectordict.values():
            count+=1
            totaltop+=wordvectorA.topsim
            squaretop+=wordvectorA.topsim*wordvectorA.topsim
            totalavg+=wordvectorA.avgsim
            squareavg+=wordvectorA.avgsim*wordvectorA.avgsim
            correlationx.append(wordvectorA.width)
            correlationy1.append(wordvectorA.topsim)
            correlationy2.append(wordvectorA.avgsim)

        avgtop=totaltop/count
        sdtop=pow(squaretop/count - avgtop*avgtop,0.5)
        avgavg=totalavg/count
        sdavg=pow(squareavg/count-avgavg*avgavg,0.5)

        print "Top similarity: average = "+str(avgtop)+" sd = "+str(sdtop)
        print "average similarity: average = "+str(avgavg)+" sd = "+str(sdavg)

        x=numpy.array(correlationx)
        y=numpy.array(correlationy1)
        thispoly= numpy.poly1d(numpy.polyfit(x,y,1))


        pr=stats.spearmanr(x,y)
        mytitle="Regression line for width and top similarity"
        #self.showpoly(x,y,thispoly,mytitle,pr,1,5)
        print "SRCC for width and top similarity is "+str(pr[0])+" ("+str(pr[1])+")"
        print thispoly

        x=numpy.array(correlationx)
        y=numpy.array(correlationy2)
        thispoly= numpy.poly1d(numpy.polyfit(x,y,1))


        pr=stats.spearmanr(x,y)
        mytitle="Regression line for width and average similarity"
        #self.showpoly(x,y,thispoly,mytitle,pr,1,5)
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

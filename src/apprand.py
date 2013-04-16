__author__ = 'Julie'

#generate random vectors of dimensionality 1 .. n to examine width correlation properties

from wordvector import WordVector
import random
import numpy
import scipy.sparse as sparse
import scipy.stats as stats
import matplotlib.pyplot as plt
import sys




class AppRand:

    def __init__(self,a,b,metric):
        self.n=1000
        self.runs=100
        self.vectordict={}
        random.seed(666)
        self.allfeatures=[]
        self.fk_idx={}
        dim=0
        while dim<1*self.n:
            label="feature_"+str(dim)
            self.allfeatures.append(label)
            dim+=1

        self.llim=a
        self.ulim=b
        self.mu=a
        self.sigma=b
        self.metric = metric
        self.width=0
        self.widths=[]
        self.ex=[]
        self.sd=[]

    def makematrix(self):
        fkeys = list(self.allfeatures)
        fkeys.sort()
        for i in range(len(fkeys)):
            self.fk_idx[fkeys[i]] = i
        del fkeys
        self.dim=len(self.fk_idx)
        #print self.fk_idx
        print "Dimensionality is "+ str(self.dim)
        WordVector.dim=self.dim
        self.makearrays()

    def makearrays(self):
        #need to convert a word vector which stores a dictionary of features into a sparse array based on fk_idx
        for wordvector in self.vectordict.values():

            temparray = numpy.zeros(self.dim)
            for feature in wordvector.vector.keys():

                col=self.fk_idx[feature]
                #print feature, col
                score=wordvector.vector[feature]
                #
                temparray[col]=score
                #print temparray
            wordvector.array = sparse.csr_matrix(temparray)
            #print wordvector.array.data
            #print "Converted "+wordvector.word+"/"+wordvector.pos




    def run(self):
        #set up dimension labels

        #set up vectors
        done =0
        while done<self.n:
            self.width=done+1
            self.vectordict={}

            tests=0
            while tests<self.runs:

                label="Word_"+str(tests)
                self.vectordict[label]=WordVector((label,"N"))
                dim=0
                features=list(self.allfeatures)
                random.shuffle(features)
                #print len(features)
                while dim<=done:
                    #self.vectordict[label].addfeature(features.pop(),random.uniform(self.llim,self.ulim))
                    self.vectordict[label].addfeature(features.pop(),abs(random.gauss(self.mu,self.sigma)))
                    dim+=1

                tests+=1
            done+=1

            #convert to arrays
            self.makematrix()
            self.allpairsims()
            for wordvector in self.vectordict.values():
                wordvector.analyse()

            (avg,sd)=self.analyse2()
            self.widths.append(self.width)
            self.ex.append(avg)
            self.sd.append(sd)
        x=numpy.array(self.widths)
        y=numpy.array(self.ex)

        thispoly= numpy.poly1d(numpy.polyfit(x,y,1))


        pr=stats.spearmanr(x,y)
        mytitle="Regression line for width and Expected Similarity using "+self.metric
        self.showpoly(x,y,thispoly,mytitle,pr,1,1)
        print "SRCC for width and top similarity is "+str(pr[0])+" ("+str(pr[1])+")"
        print thispoly

        y=numpy.array(self.sd)

        thispoly= numpy.poly1d(numpy.polyfit(x,y,1))


        pr=stats.spearmanr(x,y)
        mytitle="Regression line for width and Standard Deviation of Similarity Scores using "+self.metric
        self.showpoly(x,y,thispoly,mytitle,pr,1,1)
        print "SRCC for width and SD is "+str(pr[0])+" ("+str(pr[1])+")"
        print thispoly



    def allpairsims(self):

        done =0
        for wordvectorA in self.vectordict.values():
            wordvectorA.allsims={}
            for wordvectorB in self.vectordict.values():
                if wordvectorA.equals(wordvectorB):
                    #ignore
                    same =True
                else:
                    label = wordvectorB.word+"_"+wordvectorB.pos
                    wordvectorA.allsims[label]=wordvectorA.findsim(wordvectorB,self.metric)

                    #print "Similarity between "+str(wordvectorA.word)+" and "+str(wordvectorB.word)+" is "+str(wordvectorA.allsims[label])

            done+=1
            if done%10==0: print "Completed similarity calculations for "+str(done)+" words"


#    def analyse(self):
#        totaltop=0.0
#        totalavg=0.0
#        squaretop=0.0
#        squareavg=0.0
#        count=0
#        correlationx=[]
#        correlationy1=[]
#        correlationy2=[]
#
#        for wordvectorA in self.vectordict.values():
#            count+=1
#            totaltop+=wordvectorA.topsim
#            squaretop+=wordvectorA.topsim*wordvectorA.topsim
#            totalavg+=wordvectorA.avgsim
#            squareavg+=wordvectorA.avgsim*wordvectorA.avgsim
#            correlationx.append(float(wordvectorA.width))
#            correlationy1.append(float(wordvectorA.topsim))
#            correlationy2.append(float(wordvectorA.avgsim))
#
#        avgtop=totaltop/count
#        sdtop=pow(squaretop/count - avgtop*avgtop,0.5)
#        avgavg=totalavg/count
#        sdavg=pow(squareavg/count-avgavg*avgavg,0.5)
#
#        print "Top similarity: average = "+str(avgtop)+" sd = "+str(sdtop)
#        print "average similarity: average = "+str(avgavg)+" sd = "+str(sdavg)
#
#
#        #print correlationx
#        #print correlationy1
#        x=numpy.array(correlationx)
#        y=numpy.array(correlationy1)
#
#        #print x
#        #print y
#
#        thispoly= numpy.poly1d(numpy.polyfit(x,y,1))
#
#
#        pr=stats.spearmanr(x,y)
#        mytitle="Regression line for width and top similarity"
#        self.showpoly(x,y,thispoly,mytitle,pr,1,1)
#        print "SRCC for width and top similarity is "+str(pr[0])+" ("+str(pr[1])+")"
#        print thispoly
#
#        x=numpy.array(correlationx)
#        y=numpy.array(correlationy2)
#        thispoly= numpy.poly1d(numpy.polyfit(x,y,1))
#
#
#        pr=stats.spearmanr(x,y)
#        mytitle="Regression line for width and average similarity"
#        self.showpoly(x,y,thispoly,mytitle,pr,1,1)
#        print "SRCC for width and average similarity is "+str(pr[0])+" ("+str(pr[1])+")"
#        print thispoly

    def analyse2(self):
        total=0.0
        square=0.0
        count=0

        for wordvectorA in self.vectordict.values():
            count+=wordvectorA.nosims
            total+=wordvectorA.totalsim
            square+=wordvectorA.squaretotal

        avg=total/count
        sd=pow(square/count - avg*avg,0.5)


        print "Width "+str(self.width)+" expected similarity = "+str(avg)+" sd = "+str(sd)
        return (avg,sd)





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


if __name__ == "__main__":
    lower_limit=-5
    upper_limit=5
    metric="cosine"
    print(sys.argv)
    if len(sys.argv)>=3:
        lower_limit=sys.argv[1]
        upper_limit=sys.argv[2]

    if len(sys.argv)==4:
        metric = sys.argv[3]
    print "Lower limit for feature value is: "+str(lower_limit)
    print "Upper limit for feature value is: "+str(upper_limit)
    print "Similarity metric is: "+metric
    myapprand=AppRand(int(lower_limit),int(upper_limit),metric)
    myapprand.run()
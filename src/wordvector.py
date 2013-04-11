__author__ = 'juliewe'

import re
import numpy
import scipy
import scipy.sparse as sparse

class WordVector:

    windows=False
    windowPATT=re.compile('T:.*')
    filteredPATT=re.compile('___FILTERED___')
    beta=0
    gamma=0

    def __init__(self, wordpos):

        self.word=wordpos[0]
        self.pos=wordpos[1]
        self.vector={}
        self.length2=0
        self.width=0
        self.length=0
        self.array=""
        self.allsims={}
        self.topsim=-1.0
        self.avgsim=-1.0
        self.sd=-1.0
        self.nosims=0
        self.totalsim=0
        self.square=0



    def addfeature(self,feature,score):
        if float(score) <=-5:
            return False
        else:
            if feature in self.vector:
                print "Error "+self.word+" already has feature "+feature
                exit(1)
            else:
                matchobj=WordVector.windowPATT.match(feature)
                if matchobj:
                    if WordVector.windows:
                        self.vector[feature]=float(score)
                        self.width+=1
                        self.length2+=float(score)*float(score)
                        return True
                    else:
                        return False
                else:
                    matchobj=WordVector.filteredPATT.match(feature)
                    if matchobj:
                        #ignore
                        return False
                    else:
                        if WordVector.windows==False:
                            self.vector[feature]=float(score)
                            self.width+=1
                            self.length2+=float(score)*float(score)
                            return True
                        else:
                            return False


#    def update(self,featurelist):
#        #print "Updating "+self.word+"/"+self.pos
#        while(len(featurelist)>0):
#
#            self.addfeature(featurelist.pop(),featurelist.pop())
#        self.length=pow(self.length2,0.5)
#        #self.display()

    def add(self,avector):
        #replaced by add_array
        print "Warning - using deprecated method WordVector.add()"
        if len(avector.vector)>0:
            #print"adding features"
            #avector.display()
            for feature in avector.vector:
                score=avector.vector[feature]
                if feature in self.vector:
                    oldscore=self.vector[feature]
                    self.length2-=oldscore
                    newscore=oldscore+score
                    self.vector[feature]=newscore
                    self.length2+=newscore*newscore
                else:
                    self.vector[feature]=score
                    self.width+=1
                    self.length2+=score*score
            self.length=pow(self.length2,0.5)

    def add_array(self,avector): #unnecessary wrapper method for add if initialised properly
        #replacement for add working with sparse arrays rather than dictionaries
        if self.array=="":
            self.array=avector.array
        else:
            self.array = self.array + avector.array

    def mult_array(self,avector):  #unnecessary wrapper method for multiply if initialised properly
        if self.array=="":
            self.array=avector.array
        else:
            self.array = self.array.multiply(avector.array)


    def getfeature(self,feature):
        if feature in self.vector.keys():
            return self.vector[feature]
        else:
            return 0

    def display(self):
        print self.word+"/"+self.pos
        if self.pos =="S":
            print self.array
            print self.length
        else:
            print self.vector
            print self.width,self.length2,self.length

    def findsim(self,avector,metric):
        if metric =="cosine":
            return self.cossim_array(avector)
        elif metric =="lin":
            return self.linsim(avector)
        elif metric =="cr":
            return self.cr(avector,WordVector.beta,WordVector.gamma)
        else:
            print "Unknown similarity metric "+metric

    def cossim(self,avector):
        #replaced by cossim
        print "Warning - using deprecated method WordVector.cossim"
        if self.length*avector.length == 0:
            sim = 0
            print"Warning: 0 length vectors"
        else:
            dotprod=0
            print self.width,avector.width
            if self.width<avector.width:
                for feature in self.vector.keys():
                    dotprod+=avector.getfeature(feature)*self.getfeature(feature)
            else:
                for feature in avector.vector.keys():
                    dotprod+=self.getfeature(feature)*avector.getfeature(feature)

            sim = dotprod/(self.length*avector.length)
#        print "cossim: "+str(sim)
        return sim

    def cossim_array(self,avector):
        #replaces cossim using the arrays rather than dictionaries
        if self.length==0:
            self.length = pow(self.array.multiply(self.array).sum(),0.5)
        if avector.length==0:
            avector.length = pow(avector.array.multiply(avector.array).sum(),0.5)

        if self.length*avector.length == 0:
            sim =0
            print "Warning: 0 length vectors"
        else:
            dotprod = self.array.multiply(avector.array).sum()
            sim = dotprod/(self.length*avector.length)
        #print sim
        return sim

    def linsim(self,avector):

        intersect = set(self.vector.keys()).intersection(set(avector.vector.keys()))

        den=0
        num=0
        for feature in self.vector.keys():
            den = den+self.vector[feature]
        for feature in avector.vector.keys():
            den = den+avector.vector[feature]
        for feature in intersect:
            num = num + self.vector[feature]+avector.vector[feature]
        sim = (num*1.0)/(den*1.0)
        return sim

    def precision(self,avector):

        intersect = set(self.vector.keys()).intersection(set(avector.vector.keys()))

        den = 0
        num =0
        for feature in self.vector.keys():
            den = den +self.vector[feature]
            #den = den + 1
        for feature in intersect:
            num = num + min(self.vector[feature],avector.vector[feature])
            #num = num + 1
        sim = (num*1.0)/(den*1.0)
        return sim

    def cr(self,avector,beta,gamma):

        pre = float(self.precision(avector))
        rec = float(avector.precision(self))
        if pre*rec == 0:
            hm =0
        else:
            hm = pre*rec/(pre+rec)
        am = beta *pre + (1-beta)*rec
        sim = gamma *hm + (1-gamma)*am
        return sim


    def linsim_array(self,avector):
        #computes lin similarities over arrays
        #doesn't work because can't find ceil() function?
        den = self.array + avector.array
        denominator = den.sum()
        a = self.array.copy()
        b = avector.array.copy()
        a = a/1000
        a.ceil()
        b=b/1000
        b.ceil()
        intersection = a * b
        num = intersection * den
        numerator = num.sum()
        sim = numerator/denominator
        return sim

    def makecache(self,outstream):
        outstream.write(self.word+"/"+self.pos)
        for feature in self.vector.keys():
            outstream.write("\t"+feature+"\t"+str(self.vector[feature]))
        outstream.write("\n")

    def equals(self,avector):
        #check if it is the same word/pos
        if self.word == avector.word:
            if self.pos == avector.pos:
                return True
        return False

    def analyse(self):
        total =0.0
        count=0
        max=0.0
        squares=0.0
        for sim in self.allsims.values():
            if sim > max:
                max = sim
            total+=float(sim)
            count+=1
            squares+=sim*sim

        self.topsim=max
        self.avgsim=total/count
        self.totalsim=total
        self.squaretotal=squares
        self.nosims=count

    def outputsims(self,outstream):
        outstream.write(self.word+"/"+self.pos+"\t"+str(self.width)+"\t"+str(self.length))
        for word in self.allsims.keys():
            outstream.write("\t"+word+"\t"+str(self.allsims[word]))
        outstream.write("\n")

    def displaysims(self):
        print(self.word+"/"+self.pos+"\t"+str(self.width)+"\t"+str(self.length))
        for word in self.allsims.keys():
            print("\t"+word+"\t"+str(self.allsims[word]))
        print("\n")

    def topk(self,k):
        #only retain top k neighbours

        tuplelist=[]
        for item in self.allsims.keys():
            tuplelist.append((float(self.allsims[item]),item))
        tuplelist.sort()
        self.allsims={}
        done=0
        while done < k:
            (sim,word)=tuplelist.pop()
            self.allsims[word]=float(sim)
            done+=1

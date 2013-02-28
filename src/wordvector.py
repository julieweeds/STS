__author__ = 'juliewe'

import re
import numpy
import scipy

class WordVector:

    windows=True
    windowPATT=re.compile('T:.*')

    def __init__(self, wordpos):

        self.word=wordpos[0]
        self.pos=wordpos[1]
        self.vector={}
        self.length2=0
        self.width=0
        self.length=0
        self.array=""


    def addfeature(self,feature,score):
        if float(score) <=0:
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
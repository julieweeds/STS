__author__ = 'juliewe'

import re

class WordVector:

    windows=False
    windowPATT=re.compile('T:.*')

    def __init__(self, wordpos):

        self.word=wordpos[0]
        self.pos=wordpos[1]
        self.vector={}
        self.length2=0
        self.width=0
        self.length=0


    def addfeature(self,feature,score):
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
            else:
                if WordVector.windows==False:
                    self.vector[feature]=float(score)
                    self.width+=1
                    self.length2+=float(score)*float(score)


    def update(self,featurelist):
        print "Updating "+self.word+"/"+self.pos
        while(len(featurelist)>0):

            self.addfeature(featurelist.pop(),featurelist.pop())
        self.length=pow(self.length2,0.5)
        self.display()

    def add(self,avector):
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

    def getfeature(self,feature):
        if feature in self.vector:
            return vector[feature]
        else:
            return 0

    def display(self):
        print self.word+"/"+self.pos
        print self.vector
        print self.width,self.length2,self.length

    def findsim(self,avector,metric):
        if metric =="cosine":
            return cossim(self,avector)
        else:
            print "Unknown similarity metric "+metric

    def cossim(self,avector):
        dotprod=0
        if self.width<avector.width:
            for feature in self.vector:
                dotprod+=avector.getfeature(feature)*self.getfeature(feature)
        else:
            for feature in avector.vector:
                dotprod+=self.getfeature(feature)*avector.getfeature(feature)

        sim = dotprod/(self.length*avector.length)
        return sim



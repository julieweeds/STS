__author__ = 'juliewe'

from wordvector import WordVector

class SentencePair:
    entrycount=0
    contentPOS=['N','V','J','R']
    def __init__(self, id, fid,testing):
        SentencePair.entrycount +=1
        self.lemmasA = []
        self.lemmasB = []
        self.fid=fid
        self.id = id
        self.tokensA=[]
        self.tokensB=[]
        self.posA=[]
        self.posB=[]
        self.lsim=-1
        self.wsim=-1
        self.gs=-1
        self.cvsplit=-1
        self.prediction=-1
        self.lcsim=-1
        self.tcsim=-1
        self.sentvector ={}
        self.sentsim={}
        self.metric="none"
        self.comp="none"
        self.setsim="none"
        self.testing=testing
        self.totaldiff=0 #to establish helpfulness of technique over baseline

    def addword(self,word,sentid):
        if sentid=='A':
            self.tokensA.append(word)
        else:
            self.tokensB.append(word)
    def addlemma(self,lemma,sentid):
        #need to ensure that lemma is all lowercase for standardisation and matching to thesaurus
        lemma = lemma.lower()
        if sentid=='A':
            self.lemmasA.append(lemma)
        else:
            self.lemmasB.append(lemma)
    def addpos(self,pos,sentid):
        if sentid=='A':
            self.posA.append(pos)
        else:
            self.posB.append(pos)

    def display(self):
        print self.fid, self.id, self.cvsplit, self.gs, self.sim('lemma'), self.sim('lemma_content')
        label=self.metric+"_"+self.comp
        if label in self.sentsim.keys():
            print self.sim('sent_comp')
        label = "set_"+self.metric+"_"+self.setsim
        if label in self.sentsim.keys():
            print self.sim('sent_set')
        #print self.tokensA
        #print self.tokensB
        print self.lemmasA
        print self.posA
        print self.lemmasB
        print self.posB
        #self.sentvector['A'].display()
        #self.sentvector['B'].display()

    def toString(self,type):
        strep=self.fid+"\t"+str(self.id)+"\t"+str(self.gs)+"\t"+str(self.sim('lemma_content'))+"\t"+str(self.sim(type))+"\n"
        strep=strep+str(self.lemmasA)+"\n"
        strep=strep+str(self.lemmasB)+"\n"
        return strep

    def sim(self,type):
        ressim =-1
        if type == "lemma":
            ressim= self.lemmasim()
        else:
            if type == "gs":
                ressim= self.gs
            else:

                if type == "token":
                    ressim=self.wordsim()
                else:
                    if type == "lemma_content":
                        ressim=self.lemcontsim()
                    else:
                        if type=="token_content":
                            ressim=self.tokcontsim()
                        else:
                            if type=="sent_comp": #would be better to have metric and method in type?
                                ressim=self.getsentsim()

                            else:
                                if type =="sent_set":
                                    ressim=self.getsetsim()
                                else:
                                    print "Error - unknown sim type: "+type
#        if ressim <0 :
 #           print type+" similarity error for "
 #           self.display()
        return ressim

    def lemmasim(self):
        if self.lsim<0:
            self.lemmaoverlap()
        return self.lsim

    def lemmaoverlap(self):
        Aoverlap=0
        Boverlap=0
        for lemma in self.lemmasA:
            if lemma in self.lemmasB:
                Aoverlap +=1
        for lemma in self.lemmasB:
            if lemma in self.lemmasB:
                Boverlap +=1
        self.lsim = (Aoverlap+Boverlap)*1.0/(len(self.lemmasA)+len(self.lemmasB))


    def returncontentlemmas(self):
        return (self.returncontentlemmas('A'),self.returncontentlemmas('B'))

    def returncontentlemmas(self,sent):
        lemmalist=[]
        if sent=='A':
            for i in range(0,len(self.posA)):
                if self.posA[i] in SentencePair.contentPOS:
                    lemmalist.append((self.lemmasA[i],self.posA[i]))
        else:
            for i in range(0,len(self.posB)):
                if self.posB[i] in SentencePair.contentPOS:
                    lemmalist.append((self.lemmasB[i],self.posB[i]))
        return lemmalist


    def lemcontsim(self):
        if self.lcsim<0:
            self.lemcontoverlap()
        if self.lcsim<0:
            print "Error computing lemma overlap of content words"
            self.display()
            exit(1)
        return self.lcsim

    def lemcontoverlap(self):

        Aoverlap=0
        Boverlap=0
        Alength=0
        Blength=0
        lemmasA=self.returncontentlemmas('A')
        lemmasB=self.returncontentlemmas('B')
        for lemma in lemmasA:
            Alength+=1
            if lemma in lemmasB:
                Aoverlap+=1
        for lemma in lemmasB:
            Blength+=1
            if lemma in lemmasA:
                Boverlap+=1
        self.lcsim = (Aoverlap+Boverlap)*1.0/(Alength+Blength)

    def tokcontsim(self):
        if self.tcsim<0:
            self.tokcontoverlap()
        if self.tcsim<0:
            print "Error computing token overlap of content words"
            self.display()
            exit(1)
        return self.tcsim

    def tokcontoverlap(self):

        if len(self.posA) != len(self.tokensA):
            print "Error with number of POS tags"
            self.display()
            return
        if len(self.posB) != len(self.tokensB):
            print "Error with number of POS tags"
            self.display()
            return
        Aoverlap=0
        Boverlap=0
        Alength=0
        Blength=0
        for i in range(0,len(self.posA)):
            if self.posA[i] in SentencePair.contentPOS:
                Alength+=1

                if self.tokensA[i] in self.tokensB:
                    Aoverlap+=1
        for i in range(0,len(self.posB)):
            if self.posB[i] in SentencePair.contentPOS:
                Blength+=1
                if self.tokensB[i] in self.tokensA:
                    Boverlap+=1
        self.tcsim = (Aoverlap+Boverlap)*1.0/(Alength+Blength)


    def wordsim(self):
        if self.wsim<0:
            self.wordoverlap()
        return self.wsim

    def wordoverlap(self):
        Aoverlap =0
        Boverlap=0
        for word in self.tokensA:
            if word in self.tokensB:
                Aoverlap+=1
        for word in self.tokensB:
            if word in self.tokensA:
                Boverlap+=1
        self.wsim=(Aoverlap+Boverlap)*1.0/(len(self.tokensA)+len(self.tokensB))

    def compose(self,dict, method,metric):
        print "Warning - using deprecated method SentPair.compose()"
        self.comp=method
        self.metric=metric
        if method=="additive":

            self.add_compose(dict)


        else:
            print "Unknown method of composition "+method
        self.getsentsim()

    def add_compose(self,vectordict):
        print "Warning - using deprecated method SentPair.add_compose()"
        for sent in ['A','B']:
            self.sentvector[sent]=WordVector((sent,'S'))
            lemmalist=self.returncontentlemmas(sent)
            for tuple in lemmalist:
                if tuple in vectordict:
                    self.sentvector[sent].add(vectordict[tuple])
#                    if self.testing:
#                        print "Adding vector for "+tuple[0]+"/"+tuple[1]
#            if self.testing:
#                self.sentvector[sent].display()

    def getsentsim(self):
        label = self.metric+"_"+self.comp
        if label in self.sentsim.keys():
            sim= self.sentsim[label]
        else:
            sim = self.sentvector['A'].findsim(self.sentvector['B'],self.metric)
            self.sentsim[label]=sim
#        print "getsentsim "+str(sim)
        return sim

    def getsetsim(self):
        label = "set_"+self.metric + "_"+self.setsim
        if label in self.sentsim.keys():
            sim=self.sentsim[label]
        else:
            print "Fatal Error - have not computed set similarities"
            exit()
        return sim

    def isidentical(self):
        lengthA = len(self.tokensA)
        lengthB = len(self.tokensB)
        count=0
        if lengthA==lengthB:
            for i in range(0,lengthA):
                if self.tokensA[i]==self.tokensB[i]:
                    count+=1
        #self.display()
        #print count, lengthA, lengthB
        if count == lengthA:
            return True
        else:
            return False
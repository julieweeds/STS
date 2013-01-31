__author__ = 'juliewe'

class SentencePair:
    entrycount=0
    contentPOS=['N','V','J','R']
    def __init__(self, id, fid):
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

    def addword(self,word,sentid):
        if sentid=='A':
            self.tokensA.append(word)
        else:
            self.tokensB.append(word)
    def addlemma(self,lemma,sentid):
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
        print self.fid, self.id, self.cvsplit, self.gs, self.lemmasim(), self.sim('lemma_content')
        #print self.tokensA
        #print self.tokensB
        print self.lemmasA
        print self.posA
        print self.lemmasB
        print self.posB

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
                        print "Error - unknown sim type: "+type
        if ressim <0 :
            print type+" similarity error for "
            self.display()
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

    def lemcontsim(self):
        if self.lcsim<0:
            self.lemcontoverlap()
        if self.lcsim<0:
            print "Error computing lemma overlap of content words"
            self.display()
            exit(1)
        return self.lcsim

    def lemcontoverlap(self):

        if len(self.posA) != len(self.lemmasA):
            print "Error with number of POS tags"
            self.display()
            return
        if len(self.posB) != len(self.lemmasB):
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

                if self.lemmasA[i] in self.lemmasB:
                    Aoverlap+=1
        for i in range(0,len(self.posB)):
            if self.posB[i] in SentencePair.contentPOS:
                Blength+=1
                if self.lemmasB[i] in self.lemmasA:
                    Boverlap+=1
        self.lcsim = (Aoverlap+Boverlap)*1.0/(Alength+Blength)



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
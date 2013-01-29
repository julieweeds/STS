__author__ = 'juliewe'

class SentencePair:
    entrycount=0

    def __init__(self, id, fid):
        SentencePair.entrycount +=1
        self.lemmasA = []
        self.lemmasB = []
        self.fid=fid
        self.id = id
        self.tokensA=[]
        self.tokensB=[]
        self.lsim=-1
        self.gs=-1
        self.cvsplit=-1

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
    def display(self):
        print self.fid, self.id, self.cvsplit, self.gs, self.lemmasim()
        #print self.tokensA
        #print self.tokensB
        print self.lemmasA
        print self.lemmasB


    def sim(self,type):
        ressim =-1
        if type == "lemma":
            ressim= self.lemmasim()
        else:
            if type == "gs":
                ressim= self.gs
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

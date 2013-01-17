__author__ = 'juliewe'

import re
import math


class Totals:
    entrycount=0
    domainPATT = re.compile('^T:')

    def __init__(self):
        Totals.entrycount+=1
        self.domaincolumn={} #dict to store column totals for window features
        self.domainrow={} #dict to store row totals for window features
        self.dependencycolumn={} #dict to store columns totals for dependency features
        self.dependencyrow={} #dict to store row rotals for dependency features
        self.dependencytotal=0
        self.domaintotal=0
        self.linecount=0
        self.filereads=0

#    def readtotals(self,filename):  #for halfway crash recovery
#        f = open(filename,'r')
#        lcount=0
#        for line in f:
#            if (lcount==0):
#                dict=self.profirst(line)
#            if (lcount==1):
#                self.prosecond(line,dict)
#            self.processtotal(line,dict)
#            lcount=lcount+1
#        f.close()
#
#    def profirst(self,line):
#        words=line.split(' ')
#        if((words[0]=="##Domain")&(words[1]=="column")):
#            dict=self.domaincolumn
#            return dict
#        if((words[0]=="##Domain")&(words[1]=="row")):
#            dict=self.domainrow
#            return dict
#        if((words[0]=="##Dependency")&(words[1]=="column")):
#            dict=self.dependencycolumn
#            return dict
#        if((words[0]=="##Dependency")&(words[1]=="row")):
#            dict=self.dependencyrow
#            return dict
#        print "Error with line 1 of file",line
#        exit(1)
#
#    def prosecond(self,line,dict):
#        return
#
#    def processtotal(self,line,dict):
#        return

    def readfile(self,filename):
        self.filename=filename
        outname=filename+"_mi"
        self.outstream = open(outname,"w")
        while(self.filereads<2):
            f = open(filename,'r')
            for line in f:
                self.linecount +=1
                self.process(line.rstrip())
                if((self.linecount % 1000)==0):print "Read line: "+self.linecount
            f.close()
            self.filereads+=1;
            if self.filereads==1:
                self.output() #not necessary but may make it possible to recover crash halfway
        self.outstream.close()

    def process(self,line):

        wordlist = line.split('\t')
        row=wordlist[0]
        printout=row+"\t"
        index=1
        while(index<len(wordlist)):
            column=wordlist[index]
            freq=int(wordlist[index+1])
            mioutput=self.update(row,column,freq)
            if self.filereads>0:
                printout=printout+column+"\t"+str(mioutput)+"\t"
            index = index+2
        if self.filereads>0:
            printout=printout+"\n"
            self.outstream.write(printout)



    def calcdommi(self,row,column,freq):
        gt = self.domaintotal
        if column in self.domaincolumn:
            coltotal=int(self.domaincolumn[column])
        else:
            print "Error - no domain column total for ", column
            exit(1)
        if row in self.domainrow:
            rowtotal=int(self.domainrow[row])
        else:
            print "Error - no domain row total for ", row
            exit(1)
        #print freq, rowtotal, coltotal, gt
        mi = (freq * gt * 1.0)/(rowtotal * coltotal)
        #print mi
        mi = math.log(mi)
        #print mi
        return mi

    def calcdepmi(self,row,column,freq):
        gt = self.dependencytotal
        if column in self.dependencycolumn:
            coltotal=int(self.dependencycolumn[column])
        else:
            print "Error - no dependency column total for ", column
            exit(1)
        if row in self.dependencyrow:
            rowtotal=int(self.dependencyrow[row])
        else:
            print "Error - no dependency row total for ", row
            exit(1)
        #print freq, rowtotal, coltotal, gt
        mi = (freq * gt * 1.0)/(rowtotal * coltotal)
        #print mi
        mi = math.log(mi)
        #print mi
        return mi

    def update(self,row,column,freq):
        mioutput=""
        matchobj=Totals.domainPATT.match(column)
        if matchobj: #domain/window feature
            if self.filereads>0:    #calc mis on second read of file
                mioutput = self.calcdommi(row,column,freq)
            else:   #calc totals on first read of file
                if column in self.domaincolumn:
                    current = int(self.domaincolumn[column])
                else:
                    current = 0
                self.domaincolumn[column]=current+freq
                if row in self.domainrow:
                    current = int(self.domainrow[row])
                else:
                    current=0
                self.domainrow[row]=current+freq
                self.domaintotal+=freq

        else: #dependency feature
            if self.filereads>0:    #calc mis
                mioutput = self.calcdepmi(row,column,freq)
            else:   #calc totals
                if column in self.dependencycolumn:
                    current = int(self.dependencycolumn[column])
                else:
                    current = 0
                self.dependencycolumn[column]=current+freq
                if row in self.dependencyrow:
                    current = int(self.dependencyrow[row])
                else:
                    current=0
                self.dependencyrow[row]=current+freq
                self.dependencytotal+=freq
        return mioutput

    def output(self):
        outname = self.filename+"_depcol"
        outputf = open(outname,'w')
        outputf.write("##Dependency column totals for "+self.filename+"\n")
        outputf.write("#Grandtotal:\t"+str(self.dependencytotal)+"\n")
        for key,value in self.dependencycolumn.iteritems():
            outputf.write(key+"\t"+str(value)+"\n")
        outputf.close()

        outname = self.filename+"_domcol"
        outputf = open(outname,'w')
        outputf.write("##Domain column totals for "+self.filename+"\n")
        outputf.write("#Grandtotal:\t"+str(self.domaintotal)+"\n")
        for key,value in self.domaincolumn.iteritems():
            outputf.write(key+"\t"+str(value)+"\n")
        outputf.close()

        outname = self.filename+"_deprow"
        outputf = open(outname,'w')
        outputf.write("##Dependency row totals for "+self.filename+"\n")
        outputf.write("#Grandtotal:\t"+str(self.dependencytotal)+"\n")
        for key,value in self.dependencyrow.iteritems():
            outputf.write(key+"\t"+str(value)+"\n")
        outputf.close()

        outname = self.filename+"_domrow"
        outputf = open(outname,'w')
        outputf.write("##Domain row totals for "+self.filename+"\n")
        outputf.write("#Grandtotal:\t"+str(self.domaintotal)+"\n")
        for key,value in self.domainrow.iteritems():
            outputf.write(key+"\t"+str(value)+"\n")
        outputf.close()
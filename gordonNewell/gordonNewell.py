#! /usr/bin/python
#coding: utf-8 
'''
Created on 20/dic/2013

@author: Emanuele Paracone
@contact: emanuele.paracone@gmail.com
@author: Serena Mastrogiacomo
@contact: serena.mastrogiacomo@gmail.com

'''

import datetime
from math import factorial

class GordonNewell():
    
    # infinite server declaration between centers
    IS = [True,False,False,True]
    # relative utilization factors
    xs = [1.0, 0.892857108, 0.238095229, 19.83333256 ]
    # the average service times for centers
    ts = [7.0, 0.3, 0.08, 7.0]
    # declaring global variables
    responseTimeAvgs = None
    cycleTimeAvg = None
    throughput = None
    s = None
    sProb = None
    #initializing the lower bound for the probability for a job to be accepted
    sProbBound = 0.78
    
    # the constructor
    def __init__(self, N=50,M=4):
        # initializing the jobs number
        self.N = N
        # declaring centers Number
        self.M = M
        # the relative throughput ratio between centers
        self.vs=[]
        # the service tax for centers
        self.mu = []
        # the productiories for relative utilization factors array
        self.produttorie = []
        # the normalization factor G(N)
        self.normalizationCostant = 0
        # the state probabilities array
        self.stateProbabilities = []
        # initializing the normalization factor sum
        self.sum=0
        # the centers throughputs array
        self.lambdas = []
        # the utilization factors array
        self.rhos = []
        # the average local populations array
        self.nLocalAvg = []
        # the average service times array
        self.executionTimeAvgs = []
        self.array = []
        # the states array
        self.states = []
        # the threasholds probabilities array
        self.sProbs = []
        # the marginal probabilities array
        self.marginalProbabilities = []
        # initializing the average system response times for centers
        self.responseTimeAvg = 0
        # initializing the service taxes
        for i in range(M):
            self.array.append(0)
            self.mu.append(1.0/self.ts[i])
            
    
    # building the states space
    def generaStati(self, index, jobNum):
        for i in reversed(range(jobNum+1)):
            tmpJobN = jobNum -i
            self.array[index]=i
            if (tmpJobN > 0) and ( (index+1) < self.M) :
                self.generaStati(index+1, tmpJobN)
            else:
                for j in range (index+1, len(self.array)):
                    self.array[j]=0
                if tmpJobN == 0:
                    self.addState();
    
    # add a new state to the states array
    def addState(self):
        tmpArray = []
        for i in range (self.M ):
            tmpArray.append(self.array[i])
        self.states.append(tmpArray)
    
    # print states
    def printStates(self):
        for i in range(len(self.states)):
            print '%d. %s'%(i,str(self.states[i]))
    
    # initialize the productories array
    def produttorieInit(self):
        for i in range(len( self.states)):
            tmpProd = 1
            for j in range (self.M):
                tmpExp = self.xs[j]**self.states[i][j]
                if self.IS[j]:
                    tmpProd*= float(tmpExp)/factorial(self.states[i][j])
                else:
                    tmpProd*= tmpExp
                
                
            self.produttorie.append(tmpProd)
            
            
            
    # compute the normalization constant G(N)
    def normalizationCostantCompute(self):
        for produttoria in self.produttorie:
            self.normalizationCostant+=produttoria
    
    # compute all the state probabilities
    def stateProbabilitiesCompute(self):
        self.sum =0.0
        for produttoria in self.produttorie:
            self.stateProbabilities.append( float(produttoria) / self.normalizationCostant )
            self.sum+=self.stateProbabilities[-1]
            if self.stateProbabilities[-1] > 1:
                print 'ops!'
    
    # write the csv file of state probabilities
    def makeCsv(self):
        path='state_probabilities.csv'
        f=open(path,"w")
        f.write('state, probability,\n')
        for i in range(len(self.states)):
            f.write('%s,%s,\n'%(str(self.states[i]).replace(',',';'), str(self.stateProbabilities[i])))
        f.close()
        
        
    #------------------------------------------- local indexes-----------------------------------

    
    # compute the centers utilization factors
    def rhosCompute(self):
        for j in range (self.M):
            rhoJ = 0
            for i in range (len(self.states)):
                if (self.states[i][j]>0):
                    rhoJ+=self.stateProbabilities[i]
            self.rhos.append(rhoJ)
        
    # compute the throughputs for centers
    def lambdasCompute(self):
        for i in range(self.M):
            self.lambdas.append( self.rhos[i]* self.mu[i])
    
    # compute the average populations fro centers
    def nLocalAvgCompute(self):
        for j in range(self.M):
            self.nLocalAvg.append(0)
            for i in range(len(self.states)):
                self.nLocalAvg[-1] += self.states[i][j]*self.stateProbabilities[i]
    
    # compute the average execution time for centers          
    def executionTimeLocalAvg(self):
        for j in range (self.M):
            if self.IS[j]:
                self.executionTimeAvgs.append( self.ts[j] )
            else:
                self.executionTimeAvgs.append( float(self.nLocalAvg[j])/self.lambdas[j] )
            
    # compute the centers average response times
    def responseTimeLocalAvg(self):
        self.vsCompute()
        self.responseTimeAvgCompute()
    
    # compute the marginal probabilities
    def marginalProbabilitiesCompute(self):
        for j in range (self.M):
            self.marginalProbabilities.append([])
            for i in range (self.N+1):
                self.marginalProbabilities[-1].append(0)
        for i in range (len (self.states)):
            for j in range(self.M):
                tmp=self.states[i][j]
                if tmp > 0:
                    self.marginalProbabilities[j][tmp]+= self.stateProbabilities[i]
    
    # compute the relative throughputs
    def vsCompute(self):
        for i in range(self.M):
            self.vs.append([])
            for j in range (self.M):
                self.vs[i].append(float(self.lambdas[i])/self.lambdas[j])
    
    # compute the system response time averages
    def responseTimeAvgCompute(self):
        self.responseTimeAvgs = []
        for j in range (self.M):
            self.responseTimeAvgs.append(0)
            for i in range (self.M):
                if i == j:
                    continue
                self.responseTimeAvgs[j]+= self.vs[i][j]*self.executionTimeAvgs[i]
                
    # --------------------------------------------------- global indexes -------------------------------------
    
    # compute the system response time for Client 1
    def responseTimeAvgGlobalCompute(self):
        # we use the first center as reference
        for i in range (1,self.M):
            self.responseTimeAvg += self.vs[i][1] * self.responseTimeAvgs[i]
    
    # compute the system cycle time for Client 1
    def cycleTimeAvgGlobalCompute(self):
        self.cycleTimeAvg = self.responseTimeAvg + self.responseTimeAvgs[0]
    
    # compute the system throughput for Client 1
    def throughputCompute(self):
        self.throughput = float(self.N)/ self.cycleTimeAvg
    
    # find the lower value of the threashold S which is higher than the lower bound
    def findLowerS(self):
        for i in range (self.N+1):
            self.sProbs.append(0)
        for i in range(len(self.states)):
            tmp = self.states[i][1]+self.states[i][2]
            self.sProbs[tmp]+=self.stateProbabilities[i]
        tmpSum =0.0
        for i in range(self.N+1):
            if tmpSum >self.sProbBound:
                self.s=i
                self.sProb = 1.0-tmpSum
                break
            tmpSum += self.sProbs[i]
    
    # returns the minimum value for a reject threashold S
    def getS(self):
        return self.s
    
    # returns the maximum threashold probability
    def getSProb(self):
        return self.sProb
    
    def getSProbs(self):
        return self.sProbs
    
    def makeSProbCsv(self):
        sProbsFile = open('s_probs_N%d.csv'%(self.N),'w')
        sProbsFile.write('jobs,probability,\n')
        for i in range(1,self.N+1):
            sProbsFile.write( '%d, %s,\n'%(i,str(self.sProbs[i])))
        sProbsFile.close()
    
    # prints all the threasholds probabilities
    def printS(self):
        tmpSum=0.0
        print 'soglie:'
        for i in range(self.N+1):
            print '\t%d. %0.20f'%(i,1.0-tmpSum)
            tmpSum+=self.sProbs[i]
        print 'La soglia s è %d'%(self.s)
        print 'costante norm:%0.20f'%(self.normalizationCostant)
    
    # compute all the local indexes
    def localIndexesCompute(self):
        self.rhosCompute()
        self.lambdasCompute()
        self.nLocalAvgCompute()
        self.executionTimeLocalAvg()
        self.responseTimeLocalAvg()
    
    # compute all the global indexes
    def globalIndexesCompute(self):
        self.responseTimeAvgGlobalCompute()
        self.cycleTimeAvgGlobalCompute()
        self.throughputCompute()
    
    # print all the threasholds probabilities
    def printSProb(self):
        tmpSum = 0.0
        probs = []
        for i in range(self.N+1):
            probs.append(1.0-tmpSum)
            tmpSum+=self.sProbs[i]
        print probs
    
    def makeCumulativeSProbsCsv(self):
        sProbsFile = open('s_cumulative_probs_N%d.csv'%(self.N),'w')
        sProbsFile.write('jobs,probability,\n')
        tmpSum = 0.0
        for i in range(self.N+1):
            if i>0:
                sProbsFile.write('%d,%s,\n'%(i,str(1.0-tmpSum)))
            tmpSum+=self.sProbs[i]
        sProbsFile.close()

    # returns the array of threasholds prbabilities ( which will be useful for parametrizing mva)
    def getSProbsList(self):
        tmpSum = 0.0
        probs = []
        for i in range(self.N+1):
            probs.append(1.0-tmpSum)
            tmpSum+=self.sProbs[i]
        return probs
        
    # print all indexes, both local and global    
    def printIndexes(self):
        print '============================================='
        print '=\t\tLOCAL INDEXES\t\t='
        print '============================================='
        for i in range (self.M):
            if self.IS[i]:
                print '\ncenter %d:\n\tmu:\t\t\t%0.20f\n\tlambda:\t\t\t%0.20f\n\tEn:\
                \t%0.20f\n\tEtr:\t\t\t%0.20f\n\tEt:\t\t\t%0.20f\n'%(i+1,self.mu[i],self.lambdas[i],\
                                                         self.nLocalAvg[i],self.responseTimeAvgs[i],self.executionTimeAvgs[i])
            else:
                print '\ncenter %d:\n\tmu:\t\t\t%0.20f\n\tlambda:\t\t\t%0.20f\n\tutilizationFactor:\t%0.20f\n\tEn:\
                \t%0.20f\n\tEtr:\t\t\t%0.20f\n\tEt:\t\t\t%0.20f\n'%(i+1,self.mu[i],self.lambdas[i],self.rhos[i],\
                                                         self.nLocalAvg[i],self.responseTimeAvgs[i],self.executionTimeAvgs[i])
        print '============================================='
        print '=\t\tGLOBAL INDEXES\t\t='
        print '============================================='
        print 'System Response Time:%0.20f\nSystem Cycle Time:%0.20f\nSystem Troughput:%0.20f'%\
        (self.responseTimeAvg,self.cycleTimeAvg,self.throughput)    
        
    # the Gordon Newell algorithm solver
    def solve(self, verbose=True):
        if verbose:
            print 'generate states...'
            self.generaStati(0, self.N)
            print 'done.'
            print 'Compute state probailities...'
            self.produttorieInit()
            self.normalizationCostantCompute()
            self.stateProbabilitiesCompute()
            print 'done.'
            print 'find lower bound for S (useful for next exercise)...'
            self.findLowerS()
            print 'done'
            print 'calculating local indexes...'
            self.localIndexesCompute()
            print 'done.'
            print 'calculating global indexes...'
            self.globalIndexesCompute()
            print 'done'
        else:
            self.generaStati(0, self.N)
            self.produttorieInit()
            self.normalizationCostantCompute()
            self.stateProbabilitiesCompute()
            self.findLowerS()
            self.localIndexesCompute()
            self.globalIndexesCompute()
        
# the main function for the class
if __name__=="__main__":
    print 'Gordon Newell !!!'
    
    m = 4
    while True:
        print '--------------------------------------------'
        s = raw_input('\t1. Gordon Newell\n\t2. Print thresholds array\n\t[1,2]:')
        if s[0] == '1':
            s = raw_input('inserire n:')
            n = int(s)
            gn = GordonNewell(n,m)
            gn.solve()
            gn.printS()
            gn.printIndexes()
            print 'done!'
        elif s[0] =='2':
            #the array of minimum thresholds
            ss = []
            for n in range(1,51):
                print 'solving Gordon Newell algorithm for n:%d...'%(n),
                gn = GordonNewell(n,m)
                gn.solve(False)
                ss.append(gn.getS())
                print ' done!'
            print 'ss: %s'%(str(ss))
        else:
            print 'bye!'
            break
                
    
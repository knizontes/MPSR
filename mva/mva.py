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
import cPickle as pickle

class MVA():
    
    # customers number
    N = None
    # centers number in the system
    M = None
    
    # thresholds
    s1 = None
    s2 = None
    
    # thresholds probabilities
    ps1 = None
    ps2 = None
    
    # relative throughput matrix
    ys = None
    # relative throughput ratio matrix
    vs = None
    # service time for jobs for each center
    eTs = None
    # infinite server declaration between centers
    IS = [True, False, False, True, True, True]
    
    # centers throughputs
    lambdas = None
    # centers service rates
    mu = None
    # centers utilization factor
    rhos = None
    # centers average population
    nLocalAvgs = None
    nLocalAvgsOld = None
    # average permanence time for jobs to centers
    centersResponseTimeAvgs = None
    # system average response time for centers
    systemResponseTimeAvgs = None
    systemResponseTimeFromC1=None
    
    # global cycle time
    cycleTimeAvg = None
    # global throughput
    throughput = None
    
    probsFile = 'probs.pkl'
    
    # the threasholds probabilities array (to be red from file)
    thresholdProbabilities = None
    
    # the constructor
    def __init__(self,model, M,N,s1=31,s2=50):
        # loading the pribabilities file
        self.loadProbabilitiesFile()

        self.N =  N
        self.M = M
        self.s1 = s1
        self.s2 = s2
        
        # initializing threasholds probabilities
        self.ps1 = self.thresholdProbabilities[N-1][s1]
        self.ps2 = self.thresholdProbabilities[N-1][s2]
        
        self.vs = []
        self.lambdas = []
        self.mu = []
        self.rhos = []
        self.nLocalAvgs = []
        self.nLocalAvgsOld = []
        self.centersResponseTimeAvgs = []
        self.responseTimeAvg=0
        
        # compute the relative troughputs for each center
        # and store them into self.ys[][] matrix
        # if model is 1, then it's the original one, otherwise we consider the support model SM
        if model==1:
            # initializing the average service times for centers
            self.eTs=[7.0, 0.3, 0.08, 7.0, 0.05, 0.05]
            self.ysCompute1()
        else:
            # initializing the average service times for centers
            self.eTs=[7.0, 0.3, 0.08, 7.0, 7.05, 0.05]
            self.ysCompute2()
        
        # initializing global arrays
        for i in range (self.M):
            self.centersResponseTimeAvgs.append(self.eTs[i])
            self.nLocalAvgs.append(0)
            self.nLocalAvgsOld.append(0)
            self.vs.append([])
            self.lambdas.append(0)
            self.mu.append(1.0/self.eTs[i])
            for j in range (self.M):
                self.vs[i].append(float(self.ys[i])/self.ys[j])
                    
    # load the threasholds probabilities file
    def loadProbabilitiesFile(self):
        self.thresholdProbabilities = pickle.load( open(self.probsFile,'rb') )
        
    # the mva recurring function for throughput
    def lambdaMVA(self,j,index):    
        return (float(index+1) / self.lambdaSum(j))
    
    # computing the denominator for the lambda recurring function
    def lambdaSum(self,j):
        retval =0
        for i in range (self.M):
            retval += self.vs[i][j]* self.centersResponseTimeAvgs[i]
        return retval
    
    # the mva recurring function for the average population of center j
    def nAvg(self,j,lambdaJ):
        return lambdaJ*self.centersResponseTimeAvgs[j] #vj == one
    
    # the mva recurring function for the average response time of center j
    def tAvg (self,j):
        if self.IS[j]:
            return self.eTs[j]
        #if N is 0, then the nLocalAvgsOld is 0, so the tAvg is eTs
        return self.eTs[j]*(1.0+self.nLocalAvgsOld[j])
    
    # the mva recurring procedure
    def solve(self):
        for n in range (self.N):
            #Compute the response time for the center j    
            for j in range (self.M):
                self.centersResponseTimeAvgs[j]= self.tAvg(j)
            #Compute the throughput of center j (lambda j)
            for j in range (self.M):
                self.lambdas[j]= self.lambdaMVA(j,n)
            #Compute the average of the number of job in the center j
            for j in range (self.M):
                self.nLocalAvgsOld[j]=self.nLocalAvgs[j]
                self.nLocalAvgs[j]= self.nAvg(j, self.lambdas[j])
            
        self.responseTimeAvgCompute()      
                
        
    #------------------ local indexes --------------------
    #        (computing only the remaining ones)
    
    # compute the utilization factors for all centers
    def rhosCompute(self):
        for i in range (self.M):
            if self.IS[i]:
                self.rhos.append(0.0)
            else:
                self.rhos.append( float(self.lambdas[i] )* self.eTs[i])
            
    
    
    # ----------------- global indexes-----------------------

    # compute the system response time for Client 1 
    def responseTimeAvgGlobalCompute(self):
        self.systemResponseTimeClient1()

    # compute the system cycle time for Client 1
    def cycleTimeAvgGlobalCompute(self):
        self.cycleTimeAvg = self.systemResponseTimeFromC1 + self.eTs[0]
    
    # compute the system throughput for Client 1
    def throughputCompute(self):
        self.throughput = float(self.N)/ self.cycleTimeAvg
    
    # compute the local indexes 
    def localIndexesCompute(self):
        self.rhosCompute()
        
    
    #Compute the ys for the specified threasholds s1,s2
    def ysCompute1(self):
        
        self.ys = []
        # y1 == -6*(ps2 - 1)/((125*ps1 - 137)*ps2 - 363*ps1 + 375)
        self.ys.append( -6.0*(self.ps2 - 1.0)/((125.0*self.ps1 - 137.0)*self.ps2 - 363.0*self.ps1 + 375.0) )
        # y2 == 125*((ps1 - 1)*ps2 - ps1 + 1)/((125*ps1 - 137)*ps2 - 363*ps1 + 375)
        self.ys.append( 125.0*((self.ps1 - 1.0)*self.ps2 - self.ps1 + 1.0)/((125.0*self.ps1 - 137.0)*self.ps2 - 363.0*self.ps1 + 375.0) )
        # y3 == 125*((ps1 - 1)*ps2 - ps1 + 1)/((125*ps1 - 137)*ps2 - 363*ps1 + 375)
        self.ys.append( 125.0*((self.ps1 - 1.0)*self.ps2 - self.ps1 + 1.0)/((125.0*self.ps1 - 137.0)*self.ps2 - 363.0*self.ps1 + 375.0) )
        # y4 == -119*(ps1 - 1)/((125*ps1 - 137)*ps2 - 363*ps1 + 375)
        self.ys.append( -119.0*(self.ps1 - 1.0)/((125.0*self.ps1 - 137.0)*self.ps2 - 363.0*self.ps1 + 375.0) )
        # y5 == -6*(ps1*ps2 - ps1)/((125*ps1 - 137)*ps2 - 363*ps1 + 375)
        self.ys.append( -6.0*(self.ps1*self.ps2 - self.ps1)/((125.0*self.ps1 - 137.0)*self.ps2 - 363.0*self.ps1 + 375.0) )
        # y6 == -119*(ps1 - 1)*ps2/((125*ps1 - 137)*ps2 - 363*ps1 + 375)
        self.ys.append( -119.0*(self.ps1 - 1.0)*self.ps2/((125.0*self.ps1 - 137.0)*self.ps2 - 363.0*self.ps1 + 375.0) )
                       

    #Compute the ys for the specified threasholds s1,s2
    def ysCompute2(self):
        
        self.ys = []
        # y1 == 6*((ps1 - 1)*ps2 - ps1 + 1)/((131*ps1 - 137)*ps2 - 369*ps1 + 375)
        self.ys.append( 6.0*((self.ps1 - 1.0)*self.ps2 - self.ps1 + 1.0)/((131.0*self.ps1 - 137.0)*self.ps2 - 369.0*self.ps1 + 375.0) )
        # y2 == 125*((ps1 - 1)*ps2 - ps1 + 1)/((131*ps1 - 137)*ps2 - 369*ps1 + 375)
        self.ys.append( 125.0*((self.ps1 - 1.0)*self.ps2 - self.ps1 + 1.0)/((131.0*self.ps1 - 137.0)*self.ps2 - 369.0*self.ps1 + 375.0) )
        # y3 == 125*((ps1 - 1)*ps2 - ps1 + 1)/((131*ps1 - 137)*ps2 - 369*ps1 + 375)
        self.ys.append( 125.0*((self.ps1 - 1.0)*self.ps2 - self.ps1 + 1.0)/((131.0*self.ps1 - 137.0)*self.ps2 - 369.0*self.ps1 + 375.0) )
        # y4 == -119*(ps1 - 1)/((131*ps1 - 137)*ps2 - 369*ps1 + 375)
        self.ys.append( -119.0*(self.ps1 - 1.0)/((131.0*self.ps1 - 137.0)*self.ps2 - 369.0*self.ps1 + 375.0) )
        # y5 == -6*(ps1*ps2 - ps1)/((131*ps1 - 137)*ps2 - 369*ps1 + 375)
        self.ys.append( -6.0*(self.ps1*self.ps2 - self.ps1)/((131.0*self.ps1 - 137.0)*self.ps2 - 369.0*self.ps1 + 375.0) )
        # y6 == -119*(ps1 - 1)*ps2/((131*ps1 - 137)*ps2 - 369*ps1 + 375)
        self.ys.append( -119.0*(self.ps1 - 1.0)*self.ps2/((131.0*self.ps1 - 137.0)*self.ps2 - 369.0*self.ps1 + 375.0) )


        
        
    def globalIndexesCompute(self):
        self.responseTimeAvgGlobalCompute()
        self.cycleTimeAvgGlobalCompute()
        self.throughputCompute()
        
    def getExecutionTimeAvg(self,index):
        if index >= self.M:
            print 'error, index out of range'
            return None
        return self.centersResponseTimeAvgs[index]
        
    def getResponseTimeAvg(self,index):
        if index >= self.M:
            print 'error, index out of range'
            return None
        return self.systemResponseTimeAvgs[index]
    
    # aggiunto nuovo tempo di think presso c2 per i job rigettati da c2 (non necessario, opzione da scartare)
    def systemResponseTimeClient1(self):
        if self.systemResponseTimeFromC1:
            return self.systemResponseTimeFromC1
        self.systemResponseTimeFromC1 = 0.0
        for i in range (1,self.M):
            self.systemResponseTimeFromC1+= float(self.vs[i][0])* float(self.centersResponseTimeAvgs[i])
        return self.systemResponseTimeFromC1
    
    
    def responseTimeAvgCompute(self):
        self.systemResponseTimeAvgs = []
        for j in range (self.M):
            self.systemResponseTimeAvgs.append(0)
            for i in range (self.M):
                if i == j:
                    continue
                self.systemResponseTimeAvgs[j]+= self.vs[i][j]*self.centersResponseTimeAvgs[i]
    
    def getS1(self):
        return self.s1
    
    def getS2(self):
        return self.s2 
     
        
    def printIndexes(self):
        print '============================================='
        print '=\t\tLOCAL INDEXES\t\t='
        print '============================================='
        for i in range (self.M):
            print '\ncenter %d:\n\tmu:\t\t\t%0.20f\n\tlambda:\t\t\t%0.20f\n\tEn:\t\
            \t%0.20f\n\tEtr:\t\t\t%0.20f\n'%(i+1,self.mu[i],self.lambdas[i],\
                                                     self.nLocalAvgs[i],self.systemResponseTimeAvgs[i])
        print '============================================='
        print '=\t\tGLOBAL INDEXES\t\t='
        print '============================================='
        print 'System Response Time:%f\nSystem Cycle Time:%f\nSystem Troughput:%f'%\
        (self.systemResponseTimeFromC1,self.cycleTimeAvg,self.throughput)
        print '\n\ndebug indexes:'
        print 's1:%d'%(self.s1)
        print 's2:%d'%(self.s2)
        print 'ps1:%f'%(self.ps1)
        print 'ps2:%f'%(self.ps2)
        print 'y:'
        for i in range (self.M):
            print '\ty%d:%f'%(i,self.ys[i])
        print 'thr size:%d'%(len(self.thresholdProbabilities[self.N-1]))
        
    
    def printFirstIndexes(self):
        
        equivLambda = -self.lambdas[4]
        rho = self.lambdas[0]/self.mu[0]
        equivN = self.nLocalAvgs[0]+self.nLocalAvgs[4]
        print '\ncenter client 1:\n\tmu:\t\t\t%f\n\tlambda:\t\t\t%f\n\tEn:\t\
        \t%f\n\tEtr:\t\t\t%f\n'%(self.mu[0],equivLambda, equivN,self.systemResponseTimeClient1())
        print 's1:%d'%(self.s1)
        print 's2:%d'%(self.s2)
        print 'ps1:%f'%(self.ps1)
        print 'ps2:%f'%(self.ps2)
        print 'y:'
        for i in range (self.M):
            print '\ty%d:%f'%(i,self.ys[i])
    
    
    def printVs(self):
        print 'v:'
        for i in range(self.M):
            for j in range(self.M):
                print '\tv[%d][%d]:%f'%(i,j,self.vs[i][j])
    
    def printLambdas(self):
        print 'lambdas:%s'%(str(self.lambdas))
        
    def makeCsv(self, filename):
        path='%s.csv'%(filename)
        f=open(path,"w")
        f.write('customer number, threshold S1, threshold S2,\n%d,%d,%d,\n\n,'%(self.N,self.s1,self.s2))        
        for i in range(self.M):
            f.write('center %d,'%(i+1))
        f.write('center client1 (with reject),')
        f.write('\nthroughputs,')
        for i in range(self.M):
            f.write('%f,'%(self.lambdas[i]))
        f.write('%f,'%(float(self.lambdas[0])-self.lambdas[4]))
        
        f.write('\nresponse times,')
        for i in range(self.M):
            f.write('%f,'%(self.centersResponseTimeAvgs[i]))
        # the infinite server response time is the service time
        f.write('%f,'%(self.centersResponseTimeAvgs[0]+self.centersResponseTimeAvgs[4]*self.ps1))
        
        f.write('\nsystem response times,')
        for i in range(self.M):
            f.write('%f,'%(self.systemResponseTimeAvgs[i]))
        f.write('%f,'%(self.systemResponseTimeClient1_2()))    
        
        f.write('\ncycle times,')
        for i in range(self.M):
            f.write('%f,'%(self.systemResponseTimeAvgs[i]+self.centersResponseTimeAvgs[i]))
        f.write('%f,'%(self.systemResponseTimeClient1_2()+ self.centersResponseTimeAvgs[0]+self.centersResponseTimeAvgs[4]*self.ps1))  
        
        
        f.close()
        
    def responseTimesToString(self):
        retval = ''
        for i in range(self.M):
            retval+='%f,'%(self.centersResponseTimeAvgs[i])
        return retval
    
    def populationAvgsToString(self):
        retval = ''
        for i in range(self.M):
            retval+='%f,'%(self.nLocalAvgs[i])
        return retval

    def throughputAvgsToString(self):
        retval = ''
        for i in range(self.M):
            retval+='%f,'%(self.lambdas[i])
        return retval

    def utilizationAvgsToString(self):
        retval = ''
        for i in range(self.M):
            retval+='%f,'%(self.nLocalAvgs[i]*self.eTs[i])
        return retval
    
    

    def responseTimesToFile(self,dstFile,toWrite):
        dstFile.write('%s'%toWrite)
        for i in range(self.M):
            dstFile.write('%f,'%(self.centersResponseTimeAvgs[i]))
        # the infinite server response time is the service time
        dstFile.write('%f,\n'%(self.centersResponseTimeAvgs[0]+self.centersResponseTimeAvgs[4]*self.ps1))
        
    
    def systemResponseTimesToFile(self, dstFile,toWrite):
        dstFile.write('%s'%toWrite)
        for i in range(self.M):
            dstFile.write('%f,'%(self.systemResponseTimeAvgs[i]))
        dstFile.write('%f,\n'%(self.systemResponseTimeClient1_2()))    
        
    def shortSystemResponseTimesToFile(self, dstFile,toWrite):
        dstFile.write('%s'%toWrite)
        dstFile.write('%f,\n'%(self.systemResponseTimeClient1_2()))
    
    def sageWrite(self,dstFile,toWrite):
        dstFile.write('%s'%toWrite)
        dstFile.write('%f,\n'%(self.systemResponseTimeClient1_2()))
    

# the main function for mva
if __name__=='__main__':
    m = 6
    cond = False
    
    while True:
        print '--------------------------------------------------'
        times = []
        s = raw_input('inserire n:')
        n = int(s)
        s = raw_input('inserire s1:')
        s1 = int(s)
        s = raw_input('inserire s2:')
        s2 = int(s)
        
        times.append(datetime.datetime.now())
        
        mmva = MVA(m,n,s1,s2)

        mmva.solve()
        mmva.localIndexesCompute()
        mmva.globalIndexesCompute()
        times.append(datetime.datetime.now())

        mmva.printIndexes()
        mmva.printFirstIndexes()
        mmva.makeCsv('testN-%s_S1-%d_S2-%d'%(n,s1,s2))
        mmva.debug2()
        
        

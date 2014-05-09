#! /usr/bin/python
#coding: utf-8

'''
Created on 13/gen/2014

@author: knizontes
'''
import datetime
import cPickle as pickle

class MVA2():
    
    # number of customers
    N = None
    # number of centers in the system
    M = None
    
    # thresholds
    s1 = None
    s2 = None
    
    # threshold probabilities
    ps1 = None
    ps2 = None
    
    # relative throughput matrix
    ys = None
    # relative throughput ratio matrix
    vs = None
    # service time for jobs for each center
    eTs = [7.0, 0.3, 0.08, 7.0, 7.05, 0.05]
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
    # global response time
    #responseTimeAvg = None
    systemResponseTimeFromC1_1=None
    systemResponseTimeFromC1_2=None
    systemResponseTimeFromC1_3=None
    systemResponseTimeFromC1_4=None
    systemResponseTimeFromC1_5=None
    
    # global cycle time
    cycleTimeAvg = None
    # global throughput
    throughput = None
    
    # threashold probabilities matrix, calculated during a special run of Gordon Newell 
    # class through the vector of state probabilities
#     threasholdProbabilities = [1.0, 0.9999995558513936, 0.9999983503051783, 0.9999956765305773,\
#                                 0.9999900982271506, 0.999978820050791, 0.9999565639150845, \
#                                 0.9999136300448891, 0.9998326633389035, 0.9996834504686483, \
#                                 0.9994148659596247, 0.9989429239796322, 0.9981338802992197, \
#                                 0.9967816214506117, 0.9945793712742761, 0.9910872316921008, \
#                                 0.9856993591945439, 0.9776175504598503, 0.9658412006104016, \
#                                 0.9491860772833054, 0.9263447653355067, 0.8959984509487656, \
#                                 0.8569817610978425, 0.8084895895190775, 0.7502989837362828, \
#                                 0.682964140031188, 0.6079338857609975, 0.5275443277687126, \
#                                 0.44485792542112046, 0.36335275754926954, 0.28650502798907196, \
#                                 0.21734207151768703, 0.15805953751317958, 0.10978661705933612, \
#                                 0.07254750706644164, 0.04541615555228218, 0.026811800264007424, \
#                                 0.014851857601651086, 0.007675892018015107, 0.0036778540576656304, \
#                                 0.0016217202534336561, 0.0006524000332996938, 0.00023697708261127826, \
#                                 7.674251622480366e-05, 2.1804950712023263e-05, 5.323681089852705e-06, \
#                                 1.0856403379611024e-06, 1.774887500305411e-07, 2.1805620975534623e-08, \
#                                 1.7892186621182304e-09, 7.352707331875763e-11]

    thresholdProbabilities = None
    
    
    def __init__(self, M,N,s1=31,s2=50):
#         self.debug2()
        self.loadProbabilitiesFile()

        
        self.N =  N
        self.M = M
        self.s1 = s1
        self.s2 = s2
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
        self.ysCalculate()
        
        for i in range (self.M):
            self.centersResponseTimeAvgs.append(self.eTs[i])
            self.nLocalAvgs.append(0)
            self.nLocalAvgsOld.append(0)
            self.vs.append([])
            self.lambdas.append(0)
            self.mu.append(1.0/self.eTs[i])
            for j in range (self.M):
                self.vs[i].append(float(self.ys[i])/self.ys[j])
                    
    
    def loadProbabilitiesFile(self):
        self.thresholdProbabilities = pickle.load( open('probs.pkl','rb') )
        #print '[debug]probs :%s'%(str(self.thresholdProbabilities))
    
    def lambdaMVA(self,j,index):    
        #return (float(self.N) / self.lambdaSum(j))
        #print 'lambda index:%d'%(index+1)
        return (float(index+1) / self.lambdaSum(j))
    
    def lambdaSum(self,j):
        retval =0
        for i in range (self.M):
            retval += self.vs[i][j]* self.centersResponseTimeAvgs[i]
        return retval
    
    def nAvg(self,j,lambdaJ):
        return lambdaJ*self.centersResponseTimeAvgs[j] #vj == one
         
    def tAvg (self,j):
        if self.IS[j]:
            return self.eTs[j]
        #if N is 0, then the nLocalAvgsOld is 0, so the tAvg is eTs
        return self.eTs[j]*(1.0+self.nLocalAvgsOld[j])
    
    def solve(self):
        for n in range (self.N):
            #calculate the response time for the center j    
            for j in range (self.M):
                self.centersResponseTimeAvgs[j]= self.tAvg(j)
            #calculate the throughput of center j (lambda j)
            for j in range (self.M):
                self.lambdas[j]= self.lambdaMVA(j,n)
            #calculate the average of the number of job in the center j
            for j in range (self.M):
                self.nLocalAvgsOld[j]=self.nLocalAvgs[j]
                self.nLocalAvgs[j]= self.nAvg(j, self.lambdas[j])
            
        self.responseTimeAvgCalculate()      
                
    def debug(self, message):
        print message
#         for i in range (self.M):
#             for j in range (self.M):
#                 print 'vs [%d][%d]:%f'%(i,j,self.vs[i][j])
        
        for i in range (self.M):
            print 'centro %d:'%(i)
            print '\teTr:%f'%(self.centersResponseTimeAvgs[i])
            print '\tlambda:%f'%(self.lambdas[i])
            print '\te N:%f'%(self.nLocalAvgs[i])
            if self.IS[i]:
                print '\trho:0'
            else:
                print '\trho:%f'%(float(self.lambdas[i])*self.eTs[i])
            
    def debug2(self):
        print 'ys:%s'%(str(self.ys))
        print 'vs:%s'%(str(self.vs))
        print 'ets:%s'%(str(self.eTs))
        
        
        print 'lambdas:%s'%(str(self.lambdas))
        print 'mu:%s'%(str(self.mu))
        print 'rhos:%s'%(str(self.rhos))
        print 'nLocalAvgs:%s'%(str(self.nLocalAvgs))
        print 'nLocalAvgsOld:%s'%(str(self.nLocalAvgsOld))
        print 'centersResponseTimeAvgs:%s'%(str(self.centersResponseTimeAvgs))
        
        print 'centersResponseTimeAvgs:%s'%(str(self.responseTimeAvg))
        print 'cycleTimeAvg:%s'%(str(self.cycleTimeAvg))
        print 'throughput:%s'%(str(self.throughput))
        print 'N:%s'%(str(self.N))
        print 'M:%s'%(str(self.M))
        print 's1:%s'%(str(self.s1))
        print 's2:%s'%(str(self.s2))
        print 'ps1:%s'%(str(self.ps1))
        print 'ps2:%s'%(str(self.ps2))
        
    #local indexes
    def rhosCalculate(self):
        for i in range (self.M):
            if self.IS[i]:
                self.rhos.append(0.0)
            else:
                self.rhos.append( float(self.lambdas[i] )* self.eTs[i])
            
    
    
    # global indexes
    def responseTimeAvgGlobalCalculate(self):
        self.systemResponseTimeClient1_2()
#         # we use the first center as reference
#         for i in range (1,self.M):
#             self.responseTimeAvg += ( float(self.lambdas[i])/self.lambdas[0] ) * self.eTs[i]
    
    def cycleTimeAvgGlobalCalculate(self):
        self.cycleTimeAvg = self.responseTimeAvg + self.eTs[0]
    
    def throughputCalculate(self):
        self.throughput = float(self.N)/ self.cycleTimeAvg
        
    def localIndexesCalculate(self):
        self.rhosCalculate()
        #self.lambdasCalculate()
        #self.nLocalAvgsCalculate()
        #self.responseTimeLocalAvg()
        #self.marginalProbabilitiesCalculate()
    
    #Calculate the ys for the specified threasholds s1,s2
    def ysCalculate(self):
        
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

        
        
    def globalIndexesCalculate(self):
        self.responseTimeAvgGlobalCalculate()
        self.cycleTimeAvgGlobalCalculate()
        self.throughputCalculate()
        
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
    
    # primo approccio, reject parassita sommata dopo
    def systemResponseTimeClient1_1(self):
        if self.systemResponseTimeFromC1_1:
            return self.systemResponseTimeFromC1_1
        self.systemResponseTimeFromC1_1 = 0.0
        equivY0 = self.ys[0]-self.ys[4]
        
        for i in range (1,self.M):
            if i==4:
                continue
            self.systemResponseTimeFromC1_1+= float(self.ys[i]/equivY0)* float(self.centersResponseTimeAvgs[i])
        # a job which get through the rejection for center 1 must be re-wait the center 1 thinking time 
        self.systemResponseTimeFromC1_1+= (float(self.vs[4][0])* (float(self.centersResponseTimeAvgs[0])+ float(self.centersResponseTimeAvgs[4])+ self.systemResponseTimeFromC1_1 ))
        return self.systemResponseTimeFromC1_1
    
    # aggiunto nuovo tempo di think presso c1 per i job rigettati da c1
    def systemResponseTimeClient1_2(self):
        if self.systemResponseTimeFromC1_2:
            return self.systemResponseTimeFromC1_2
        self.systemResponseTimeFromC1_2 = 0.0
        for i in range (1,self.M):
            if i == 4:
                #continue
                self.systemResponseTimeFromC1_2+= float(self.lambdas[i])* (float(self.centersResponseTimeAvgs[i])+float(self.centersResponseTimeAvgs[0]))
            else:
                self.systemResponseTimeFromC1_2+= float(self.lambdas[i])* float(self.centersResponseTimeAvgs[i])
        #self.systemResponseTimeFromC1_2 += float(self.lambdas[4])* (float(self.centersResponseTimeAvgs[4])+float(self.centersResponseTimeAvgs[0])+self.systemResponseTimeFromC1_2)
        self.systemResponseTimeFromC1_2 = float(self.systemResponseTimeFromC1_2)/ self.lambdas[0]
        return self.systemResponseTimeFromC1_2
    
    # aggiunto nuovo tempo di think presso c2 per i job rigettati da c2 (non necessario, opzione da scartare)
    def systemResponseTimeClient1_3(self):
        if self.systemResponseTimeFromC1_3:
            return self.systemResponseTimeFromC1_3
        self.systemResponseTimeFromC1_3 = 0.0
        for i in range (1,self.M):
            self.systemResponseTimeFromC1_3+= float(self.vs[i][0])* float(self.centersResponseTimeAvgs[i])
        # a job which get through the rejection for center 1 must be re-wait the center 1 thinking time 
        #self.systemResponseTimeFromC1_3 += (float(self.vs[4][0])* (float(self.centersResponseTimeAvgs[0])+ self.systemResponseTimeFromC1_3 ))
        return self.systemResponseTimeFromC1_3
    
    # reitrodotti troughput relativi (molto meglio)
    def systemResponseTimeClient1_4(self):
        if self.systemResponseTimeFromC1_4:
            return self.systemResponseTimeFromC1_4
        self.systemResponseTimeFromC1_4 = 0.0
        for i in range (1,self.M):
            self.systemResponseTimeFromC1_4+= float(self.vs[i][0])* float(self.centersResponseTimeAvgs[i])
        # a job which get through the rejection for center 1 must be re-wait the center 1 thinking time 
        self.systemResponseTimeFromC1_4+= (float(self.vs[4][0])* float(self.centersResponseTimeAvgs[0]))#+self.systemResponseTimeFromC1_4))
        # a job which get through the rejection for center 2 must be re-wait the center 2 thinking time 
        self.systemResponseTimeFromC1_4+= (float(self.vs[5][0])* (float(self.centersResponseTimeAvgs[3])))
        return self.systemResponseTimeFromC1_4
    #             MVAThreasholdSearchRun(1)
#             print '--------------------------------------'
    # la soluzione migliore, i job rigettati da c1 devono aspettare un nuovo tempo di think prima di ripartire e attraversare tutta
    # la sottorete a valle
    def systemResponseTimeClient1_5(self):
        if self.systemResponseTimeFromC1_5:
            return self.systemResponseTimeFromC1_5
        self.systemResponseTimeFromC1_5 = 0.0
        for i in range (1,self.M):
            if i==4:
                continue
            self.systemResponseTimeFromC1_5+= float(self.vs[i][0])* float(self.centersResponseTimeAvgs[i])
        # a job which get through the rejection for center 1 must be re-wait the center 1 thinking time 
        self.systemResponseTimeFromC1_5+= (float(self.vs[4][0])* (float(self.centersResponseTimeAvgs[0])+ float(self.centersResponseTimeAvgs[4])+ self.systemResponseTimeFromC1_5 ))
        return self.systemResponseTimeFromC1_5
    
    
    def responseTimeAvgCalculate(self):
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
            print '\ncenter %d:\n\tmu:\t\t\t%0.20f\n\tlambda:\t\t\t%0.20f\n\tutilizationFactor:\t%0.20f\n\tEn:\t\
            \t%0.20f\n\tEtr:\t\t\t%0.20f\n'%(i+1,self.mu[i],self.lambdas[i],self.rhos[i],\
                                                     self.nLocalAvgs[i],self.systemResponseTimeAvgs[i])
        print '============================================='
        print '=\t\tGLOBAL INDEXES\t\t='
        print '============================================='
        print 'System Response Time:%f\nSystem Cycle Time:%f\nSystem Troughput:%f'%\
        (self.responseTimeAvg,self.cycleTimeAvg,self.throughput)
        print '\n\ndebug indexes:'
        print 's1:%d'%(self.s1)
        print 's2:%d'%(self.s2)
        print 'ps1:%f'%(self.ps1)
        print 'ps2:%f'%(self.ps2)
        print 'y:'
        for i in range (self.M):
            print '\ty%d:%f'%(i,self.ys[i])
        print 'thr size:%d'%(len(self.thresholdProbabilities[self.N-1]))
        
    def _printFirstIndexes(self):
        print '\ncenter %d:\n\tmu:\t\t\t%f\n\tlambda:\t\t\t%f\n\tutilizationFactor:\t%f\n\tEn:\t\
        \t%f\n\tEtr:\t\t\t%f\n'%(0,self.mu[0],self.lambdas[0],self.rhos[0],\
                                 self.nLocalAvgs[0],self.systemResponseTimeAvgs[0])
        print 's1:%d'%(self.s1)
        print 's2:%d'%(self.s2)
        print 'ps1:%f'%(self.ps1)
        print 'ps2:%f'%(self.ps2)
        print 'y:'
        for i in range (self.M):
            print '\ty%d:%f'%(i,self.ys[i])
    
    
    def printFirstIndexes(self):
        equivMu = self.mu[0]#+(1.0/self.ps1)*self.mu[4]
        equivLambda = self.lambdas[0]-self.lambdas[4]
        equivRho = float(equivLambda)/equivMu
        equivN = self.nLocalAvgs[0]+self.nLocalAvgs[4]
        print '\ncenter client 1:\n\tmu:\t\t\t%f\n\tlambda:\t\t\t%f\n\tutilizationFactor:\t%f\n\tEn:\t\
        \t%f\n\tEtr first type:\t\t%f\n\tEtr second type:\t\t%f\n\tEtr third type:\t\t%f\n'%(equivMu,equivLambda,equivRho,\
                                 equivN,self.systemResponseTimeClient1_1(),self.systemResponseTimeClient1_2(),self.systemResponseTimeClient1_3())
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
        # the infinite server response time is the service time
        retval+='%f,'%(self.centersResponseTimeAvgs[0]+self.centersResponseTimeAvgs[4]*self.ps1)
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
    
    
if __name__=='__main__':
    m = 6
    #n = 50
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
        
        mmva = MVA2(m,n,s1,s2)

        mmva.solve()
        mmva.localIndexesCalculate()
        mmva.globalIndexesCalculate()
        times.append(datetime.datetime.now())

        mmva.printIndexes()
        mmva.printFirstIndexes()
        mmva.makeCsv('testN-%s_S1-%d_S2-%d'%(n,s1,s2))
        mmva.debug2()
        
        

'''
Created on 20/dic/2013

@author: Emanuele Paracone
@contact: emanuele.paracone@gmail.com
@author: Serena Mastrogiacomo
@contact: serena.mastrogiacomo@gmail.com

'''

import cPickle as pickle
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


from gordonNewell.gordonNewell import GordonNewell
from mva.mva import MVA

# the minimum threasholds array, obtained from Gordon Newell execution
minSs = [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 7, 7, 8, 8, 9, 10,\
         11, 12, 13, 14, 15, 16, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]


# Run Gordon Newell
def gnRun():
    print 'Risoluzione del primo modello tramite Gordon Newell'
    s = raw_input('\t1. esecuzione standard\n\t2.stampa vettore probabilità in funzione del numero di job N\n\
    \t3.stampa vettore delle probabilità rispetto al nuemro di jobs in Fe Server e Be Server\n[1,2,3]:')
    if s[0]=='1':
        s = raw_input('inserire N:')
        n = int(s)
        gn = GordonNewell(n)
        gn.solve()
        gn.printS()
        gn.printIndexes()
    elif s[0]=='2':
        probList = []
        for n in range(1,51):
            gn = GordonNewell(n)
            gn.solve(False)
            probList.append(gn.getSProbsList())
        print 'serializing...'
        out_pkl = open('probs.pkl','wb')
        pickle.dump(probList,out_pkl)
        print 'done!'
    else:
        s =s = raw_input('inserire N:')
        n = int(s)
        gn = GordonNewell(n)
        gn.solve()
        sProbs = gn.getSProbs()
        for i in range(1,n+1):
            print 'S=%d, prob=%0.20f'%(i,sProbs[i])
        gn.makeSProbCsv()
        gn.makeCumulativeSProbsCsv()
        
# run a single execution of MVA
def MVARun():
    print 'Risoluzione del secondo modello tramite MVA'
    print 'ricerca delle soglie S1, S2 ottimali rispetto al tempo di risposta dell\'impianto visto dal centro client 1...'
    
    sMin = 31
    m = 6
    s = raw_input('inserire n:')
    n = int(s)
    
    s1 = 100
    s2 = 100
    eTrMin = 10000.0
    leastEtrMva = None
    mvas = []
    for i in range(sMin,n+1):
        for j in range(sMin,n+1):
            mvas.append(MVA(1,m,n,i,j))
            mvas[-1].solve()
            mvas[-1].localIndexesCalculate()
            mvas[-1].globalIndexesCalculate()
            eTr = mvas[-1].systemResponseTimeClient1()
            if eTr < eTrMin:
                eTrMin = eTr
                leastEtrMva = mvas[-1]
    leastEtrMva.printIndexes()
    leastEtrMva.printFirstIndexes()

# look for the threasholds which minimizes the system response time for Client1 jobs through multiple runs of MVA
# and write the files of the solved original model parametrized with found values
def MVAThreasholdSearchRun( outputFile = None):
    print 'Risoluzione del secondo modello tramite MVA'
    print 'esecuzione dei possibili modelli al variare di N'
    
    
        
    m = 6
    nMax = 50
    responseTimesFile = open('response_times.csv','w')
    throughputsFile = open('throughputs.csv','w')
    utilizationsFile = open('utilizations.csv','w')
    populationsFile = open('populations.csv','w')
    globalFile = open('globals.csv','w')
    pointsLists = []
    
    responseTimesFile.write('N,Client 1,FE Server,BE Server, Client 2, Client 1 reject, Client 2 reject,\n')
    throughputsFile.write('N,Client 1,FE Server,BE Server, Client 2, Client 1 reject, Client 2 reject,\n')
    utilizationsFile.write('N,Client 1,FE Server,BE Server, Client 2, Client 1 reject, Client 2 reject,\n')
    populationsFile.write('N,Client 1,FE Server,BE Server, Client 2, Client 1 reject, Client 2 reject,\n')
    globalFile.write('N,System Response Time (Client 1), System Cycle Time, System Throughput,\n')
    
    pointsLists.append([])
    for n in range(1,nMax+1):
        pointsLists.append([])
        pointsLists[n].append([])
        pointsLists[n].append([])
        pointsLists[n].append([])
        
        s1 = 100
        s2 = 100
        eTrMin = 10000.0

        mvas = []
        sMin = minSs[n-1]
        for i in range(sMin,n+1):
            mvas.append([])
            for j in range(sMin,n+1):
                mvas[i-sMin].append(MVA(2,m,n,i,j))
                mvas[i-sMin][-1].solve()
                mvas[i-sMin][-1].localIndexesCompute()
                mvas[i-sMin][-1].globalIndexesCompute()
                eTr = mvas[i-sMin][-1].systemResponseTimeClient1()
                pointsLists[n][0].append(i)
                pointsLists[n][1].append(j)
                pointsLists[n][2].append(eTr)
                    
                if eTr < eTrMin:
                    eTrMin = eTr
                    s1 = mvas[i-sMin][-1].getS1()
                    s2 = mvas[i-sMin][-1].getS2()
                            
        print '\tN=%d  min eTr:%f\ts1:%d\ts2:%d'%(n,eTrMin,s1,s2)
        if outputFile:
            outputFile.write('%d,%f,%d,%d,\n'%(n,eTrMin,s1,s2))
        # solve the original model with S1, S2 found
        originalMva = MVA(1,m,n,s1,s2)
        originalMva.solve()
        originalMva.localIndexesCompute()
        originalMva.globalIndexesCompute()
        responseTimesFile.write('%d,%s\n'%(n,originalMva.responseTimesToString()))
        throughputsFile.write('%d,%s\n'%(n,originalMva.throughputAvgsToString()))
        utilizationsFile.write('%d,%s\n'%(n,originalMva.utilizationAvgsToString()))
        populationsFile.write('%d,%s\n'%(n,originalMva.populationAvgsToString()))
        cycleTime = eTrMin+7.0
        globalFile.write('%d,%f,%f,%f,\n'%(n,eTrMin,cycleTime,float(n)/cycleTime  ))
    
    #closing files
    responseTimesFile.close()
    throughputsFile.close()
    utilizationsFile.close()
    populationsFile.close()
    globalFile.close()
    s = raw_input('stampare i grafici del tempo di risposta del sistema subito dal client1?\n[s,n]:')
    if s[0]=='s':
        plotAllPoints(pointsLists)
    
    
    
# the plotting points function - plot a 3d graph using matplot library with mpl toolkit extension
def plotAllPoints(pointsLists):
    print 'plotting points...'
    for n in range (1,len(pointsLists)):
        fig = plt.figure(figsize=(10,7 ), dpi=100)
        ax3D = fig.add_subplot(111, projection='3d')
        x = pointsLists[n][0]
        y = pointsLists[n][1]
        z = pointsLists[n][2]
        ax3D.scatter(x, y, z, s=10, c=z, marker='o')
        ax3D.set_xlabel('S1')
        ax3D.set_ylabel('S2')
        ax3D.set_zlabel('E[Tr]')
        plt.savefig('threasholds_N%d.png'%(n))
        plt.clf()
    print 'done!'
    
# the global main function!
if __name__=="__main__":
    print '\n\n================================================='
    print '=\t Modelli di Prestazione di \t\t='
    print '=\t      Sistemi e Reti\t\t\t='
    print '=\t\t2012-2013\t\t\t='
    print '================================================='
    
    while True:
        s1 = raw_input('\n\nModello da risolvere:\n\t1. modello 1 (algoritmo Gordon-Newell)\
        \n\t2. modello 2 (algoritmo MVA semplice, parametri custom)\n\t3. modello 2 (algoritmo MVA, ricerca soglie minime al variare del numero di utenti)\n\n[1,2,3]:')
        if s1[0]=='1':
            gnRun()
                
        elif s1[0]=='2':
            MVARun()
        
        elif s1[0]=='3':
            outputFile = open('thresholds.csv','w')
            MVAThreasholdSearchRun(outputFile)
            outputFile.close()
        
        elif s1=='exit' or s1=='quit' :
            print 'bye!'
            break
        else:
            print 'inserire 1, 2, 3 o exit'
    
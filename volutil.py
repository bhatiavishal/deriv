#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 21:43:49 2018

@author: vishal
"""
import BS
import deriv.util as du
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
import math


class logvolslice:
    def __init__(self, strikevol, fwd, mat):
        """ strike vol : 2d np array ascending order strike, vol
        """
        self.strikevol = strikevol
        self.fwd = fwd
        self.mat = mat
        self.strikevolinter = interpolate.interp1d(strikevol[:,0], strikevol[:,1], fill_value = "extrapolate")
        nofstrikes = self.strikevol.shape[0]
        strprob = np.ones((nofstrikes-1,2))*0.5
        for i in range(0,nofstrikes-1):
            v0 = self.strikevol[i][1]
            v1 = self.strikevol[i+1][1]
            k0 = self.strikevol[i][0]
            k1 = self.strikevol[i+1][0]
            #cp = -1 if k0 < self.fwd else 1
            cp = -1
            d0 = BS.black(v0,self.fwd,k0,self.mat,cp)
            d1 = BS.black(v1,self.fwd,k1,self.mat,cp)
            strprob[i,0] = (k1+k0)/2
            strprob[i,1] = (d1-d0)/(k1-k0)
        self.cumdf = cdf(strprob)
        
    def getvolforstrike(self, strike):
        return self.strikevolinter(strike)
            
    def deltastrike(self, delta, cp):
        def bounddelta(strike):
            f = self.fwd
            v = self.getvolforstrike(strike)
            mat = self.mat
            return abs(BS.blackdelta(v,f,strike,mat,cp) - delta)
        res = opt.minimize(bounddelta,self.fwd)
        return res.x
           
class cdf:
    def __init__(self,strikeprob):
        self.strikeprob = strikeprob
        self.probinterp = interpolate.interp1d(strikeprob[:,0],strikeprob[:,1], fill_value = "extrapolate")
        self.probinterpinv = interpolate.interp1d(strikeprob[:,1],strikeprob[:,0], fill_value = "extrapolate")
    def getcumprob(self,strike):
        '''
        if strike > self.strikeprob[-1,0]:
            return self.strikeprob[-1,1]
        if strike < self.strikeprob[0,0]:
            return self.strikeprob[0,1]
        '''    
        return self.probinterp(strike)
    def getstrike(self,prob):
        return self.probinterpinv(prob)
    
def main():
    fwd = 15.0
    T = 10
    a =0.5
    b= 0.0001
    c =1.05
    stvol = np.ones([100,2])
    stvol[:,0] = np.exp(np.linspace(np.log(0.5),np.log(100),100))
    stvol[:,1] = 0.2
    stvol[:,1] = 0.2*du.quad(np.log(stvol[:,0]/fwd)/0.2/T,a,b,c)
   
    plt.plot(stvol[:,0], stvol[:,1])
    plt.title("quad vol")
    plt.show()
    
    vol= logvolslice(stvol,fwd,T)
    cdfvol = vol.cumdf.strikeprob
    plt.plot(cdfvol[:,0],cdfvol[:,1])
    plt.title("cdf")
    plt.show()
    
    
    xran = np.random.normal(size=50000)
    vols = 0.2
    sim = fwd*np.exp(-vols*vols*T/2+vols*xran*math.sqrt(T))
    
    lbound = vol.cumdf.getstrike(0.01)
    ubound = vol.cumdf.getstrike(0.99)
    print(lbound,ubound)
    x = np.linspace(ubound , lbound, 15)
    y = [ BS.blackimply(fwd,stri,T,-1, BS.mcoptprice(sim,stri,-1)) for stri in x]
    plt.plot(x,y)
    plt.title("vol from cdf")
    plt.show()
    
    cumdfbase= cdf(BS.mccdf(sim))
    #sim1 = [vol.cumdf.getstrike(cumdfbase.getcumprob(strk)) for strk in sim]
    sim1 = np.array([vol.cumdf.getstrike(cumdfbase.getcumprob(strk)) for strk in sim])
    y = 0.2*du.quad(np.log(x/fwd)/0.2/T,a,b,c)
    y1 = [ BS.blackimply(fwd,stri,T,-1, BS.mcoptprice(sim1,stri,-1)) for stri in x]
    plt.plot(x,y, label="original")
    plt.plot(x,y1, label="marginadj")
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

    plt.show()
    print(vol.deltastrike(0.25,1), vol.deltastrike(0.25,-1))
    
    return vol
    
if __name__ == "__main__":
     vs = main()

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

class logvolslice:
    def __init__(self, strikevol, fwd, mat):
        """ strike vol : 2d np array ascending order strike, vol
        """
        self.strikevol = strikevol
        self.fwd = fwd
        self.mat = mat
        nofstrikes = self.strikevol.shape[0]
        cdf = np.ones((nofstrikes-1,2))*0.5
        for i in range(0,nofstrikes-1):
            v0 = self.strikevol[i][1]
            v1 = self.strikevol[i+1][1]
            k0 = self.strikevol[i][0]
            k1 = self.strikevol[i+1][0]
            #cp = -1 if k0 < self.fwd else 1
            cp = -1
            d0 = BS.black(v0,self.fwd,k0,self.mat,cp)
            d1 = BS.black(v1,self.fwd,k1,self.mat,cp)
            cdf[i,0] = (k1+k0)/2
            cdf[i,1] = (d1-d0)/(k1-k0)
        self.cdf = cdf
        self.probinterp = interpolate.interp1d(cdf[:,0],cdf[:,1])
        self.probinterpinv = interpolate.interp1d(cdf[:,1],cdf[:,0])
        
    def getcdf(self,strike):
        return self.probinterp(strike)
    def getstrike(self,prob):
        return self.probinterpinv(prob)
        
           
        
def main():
    fwd = 15.0
    T = 10
    stvol = np.ones([100,2])
    stvol[:,0] = np.exp(np.linspace(np.log(0.5),np.log(100),100))
    stvol[:,1] = 0.2
    #stvol[:,1] = 0.2*du.quad(np.log(stvol[:,0]/fwd)/0.2/T,0.01,-0.05,1.05)
   
    plt.plot(stvol[:,0], stvol[:,1])
    plt.show()
    
    vol= logvolslice(stvol,fwd,T)
    print(vol.getcdf(fwd))
    print(vol.getstrike(0.5))
    
    
    cdf = vol.cdf
    plt.plot(cdf[:,1],cdf[:,0])
    plt.show()
    
if __name__ == "__main__":
     main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 23:35:55 2018

@author: vishal
"""
from math import sqrt,exp,log,pi
from scipy.stats import norm
import scipy.optimize as opt
import numpy as np

def black(v,F,K,T,cp):
    """ callorput = 1 call/ -1 put 
    """
    N = norm.cdf
    n = norm.pdf
    d1 = (log(F/K)+(0.5*v*v)*T)/(v*sqrt(T))
    d2 = d1-v*sqrt(T)
    price = cp*(F*N(cp*d1)-K*N(cp*d2))
    vega = F*sqrt(T)*n(d1)
    return price

def blackvega(F,K,T,v,cp):
    """ callorput = 1 call/ -1 put 
    """
    N = norm.cdf
    n = norm.pdf
    d1 = (log(F/K)+(0.5*v*v)*T)/(v*sqrt(T))
    vega = F*sqrt(T)*n(d1)
    return vega

def blackdelta(v,F,K,T,cp):
    d1 = (log(F/K)+(0.5*v*v)*T)/(v*sqrt(T))
    return norm.cdf(d1) if cp == 1 else 1 - norm.cdf(d1)

def blackstrikefordelta(v, F, T, cp, delta):
    def errdelta(strike):
        comdelta = blackdelta(v,F,strike,T,cp)
        err = comdelta - delta
        return err * err
    res = opt.minimize(errdelta,np.array(F),bounds = [(F*1e-6,None)])
    return res.x

def optblack(F,K,T,cp,prem):
    def boundblack(vol):
        return black(vol,F,K,T,cp) - prem
    return boundblack

def optblackvega(F,K,T,cp,prem):
    def boundblackvega(vol):
        #print("vega=",blackvega(F,K,T,vol,cp),F,K,T,vol,cp)
        return blackvega(F,K,T,vol,cp)
    return boundblackvega


def blackimply(F,K,T,cp,prem):
    return opt.brentq(optblack(F,K,T,cp,prem),0.000001,10)
    #return opt.newton(optblack(F,K,T,cp,prem), x0=0.1, fprime=optblackvega(F,K,T,cp,prem))
    #return opt.newton(optblack(F,K,T,cp,prem), x0=0.1)

def nblack(v,F,K,T,cp):
    """ callorput = 1 call/ -1 put 
    """
    N = norm.cdf
    d1 = (F - K)/(v*sqrt(T))
    price = cp*(F-K)*N(cp*d1) + v*sqrt(T/2/pi)*exp(-d1*d1/2)
    vega = sqrt(T/2/pi)*exp(-d1*d1/2)
    return price

def mcoptprice(paths, strike, callput):
    payoff = np.mean(np.maximum(callput*(paths[:] - strike),0))
    return payoff

def mccdf(paths):
    pathssor = np.sort(paths)
    noofpoints = paths.shape[0]
    cdf = np.ones((noofpoints,2))*0.5
    for i in range(0,paths.shape[0]):
        cdf[i,0] = pathssor[i]
        cdf[i,1] = paths[paths < pathssor[i]].shape[0]/noofpoints
    return cdf
        
def volfromsim(sim, fwd, strike, mat):
    cp = -1 if fwd < strike else -1
    #cp = -1 
    return blackimply(fwd,strike,mat,cp, mcoptprice(sim, strike, cp))
    
if __name__ == "__main__":
    #print(blackimply(100,105,1,1,3.99))
    print(nblack(10,100,100,1,-1))
    print(blackimply(15,3.806,10,-1,0.03259))
    print(blackstrikefordelta(0.2,15,10,1,0.1))
        
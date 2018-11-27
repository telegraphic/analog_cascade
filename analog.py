#!/usr/bin/env python

import numpy as np

def noise_to_temp(NF, linear=False, amb_temp=290):
    """ Noise Figure to Noise Temperature
    
    Parameters
    ----------
    NF: float
        Noise figure, in dB. If linear arg is also passed
        with value True, then treated as noise factor instead.
    linear: bool
        Default false. If True, treat noise figure as noise
        factor (ie. linear units)
    amb temp: float
        Ambient temperature, in dB. The IEEE defintion of room
        temperature is 290K. 
    
    Notes
    -----
    Noise Figure (NF): dB units
    Noise Factor (F):  linear units
    Noise Temperature (T): in Kelvin
    
    T = 280(F-1) K 
    """
    if not linear:
        F = 10**(NF / 10.0)
    else:
        F = NF
    T = amb_temp*(F-1)
    return T

def lin2db(val):
    """ Convert a value to decibels (dB) """
    return 10 * np.log10(val)

def db2lin(val):
    """ Convert a value to decibels (dB) """
    return 10**(val/10)
    
class AnalogComponent(object):
    """ An analog component 
    
    Parameters
    ----------
    name: str
        name of component
    T: float
        Noise temperature (K)
    G: float
        Gain (linear)
    amb_temp: float
        Ambient temperature. Defaults to 290K
    
    """
    def __init__(self, name, T=0.0, G=1.0, amb_temp=290):
        self.name = name
        
        if type(T) in set((str, unicode)):
            T = T.lower().strip()
            try:
                if 'db' in T:
                    T = noise_to_temp(float(T.strip('db')), linear=False, amb_temp=amb_temp)
                elif 'k' in T:
                    T = float(T.strip('k'))
                elif 'lin' in T:
                    T = noise_to_temp(float(T.strip('lin')), linear=True, amb_temp=amb_temp)
                else:
                    T = float(T)
            except ValueError:
                print "Error: Cannot understand %s"%T
                raise ValueError
        
        if type(G) in set((str, unicode)):
            G = G.lower().strip()
            try:
                if 'db' in G:
                    G = db2lin(float(G.strip('db')))
                elif 'lin' in G:
                    G = float(G.strip('lin'))
                else:
                    G = float(G)
            except ValueError:
                print "Error: Cannot understand %s"%T
                raise ValueError
                
        self.T    = T
        self.G    = G
    
    def __repr__(self):
        n, t, g = self.name.ljust(10), self.T, lin2db(self.G)
        return "Component: %s %04.2fK \t %04.2fdB \n"%(n, t, g)

    def set_noise_figure(self, NF):
        """ Set noise figure NF """
        self.T = noise_to_temp(NF, linear=False)
    
    def set_noise_factor(self, F):
        """ Set noise factor F """
        self.T = noise_to_temp(F, linear=True)
    
    def set_noise_temp(self, T):
        """ Set noise temperature T """
        self.T = T
    
    def set_gain_db(self, G):
        """ Set gain in dB """
        self.G = lin2db(G)
    
    def set_gain_linear(self, g):
        """ Set gain in linear units """
        self.G = g
        
    
class AnalogSystem(object):
    """ Analog receiver system """
    def __init__(self):
        self.components = []
        self.Tsys = 0
        self.Gsys = 1
    
    def __repr__(self):
        toprint = 'AnalogSystem\n------------\n'
        for c in self.components:
            toprint += str(c)
        return toprint
    
    def add_component(self, comp):
        """ Add a component to the receiver chain 
        
        Parameters
        ----------
        comp: Component()
            Analog Component object to add
        """
        
        self.components.append(comp)
    
    def compute_tsys(self):
        """ Compute the Tsys of the analog system 
        
        Notes
        -----
        Tsys = T1 + T2 / G1 + T3 / G1*G2 + ... 
        """
        
        Tsys = 0.0
        Gsys = 1.0
        
        for comp in self.components:
            
            Tx = comp.T
            Gx = comp.G
            
            Tx_w  = Tx / Gsys
            
            Tsys += Tx_w
            Gsys *= Gx
            
            G_db = 10*np.log10(Gsys)
            cstr = str(comp.__repr__()).strip()
            print "%s \t | Tsys: %04.2fK \t Gsys: %04.2f dB"%(cstr, Tsys, G_db)

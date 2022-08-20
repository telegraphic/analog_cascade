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
    def __init__(self, name, T=0.0, G=1.0, amb_temp=290, IP3=np.inf):
        self.name = name
        
        if type(T) in set((str, bytes)):
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
                print("Error: Cannot understand %s"%T)
                raise ValueError
        
        if type(G) in set((str, bytes)):
            G = G.lower().strip()
            try:
                if 'db' in G:
                    G = db2lin(float(G.strip('db')))
                elif 'lin' in G:
                    G = float(G.strip('lin'))
                else:
                    G = float(G)
            except ValueError:
                print("Error: Cannot understand %s"%T)
                raise ValueError

        if type(IP3) in set((str, bytes)):
            IP3 = IP3.lower().strip()
            try:
                if 'db' in IP3:
                    IP3 = db2lin(float(IP3.strip('dbm')))
                elif 'lin' in G:
                    IP3 = float(IP3.strip('lin'))
                else:
                    IP3 = IP3
            except ValueError:
                print("Error: Cannot understand %s"%T)
                raise ValueError
                
        self.T    = T
        self.G    = G
        self.IP3  = IP3
        
    
    def __repr__(self):
        n, t, g = self.name.ljust(16), self.T, lin2db(self.G)
        return f"{n:<16s} | {t:^10.2f} | {g:^10.2f} \n"

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

class SkySpectrum(AnalogComponent):
    def __init__(self, freqs):
        from pygdsm import GlobalSkyModel
        self.freqs = freqs
        self.skymodel    = GlobalSkyModel()
        self.spectrum = self.skymodel.generate(freqs).mean(axis=1)
        T = self.spectrum.mean()

        super().__init__('SkyModel', T)

class ADC(object):
    def __init__(self, nbits, mVpp, Z0=50, name='ADC'):
        self.nbits = nbits
        self.mVpp  = mVpp
        self.name  = name
        
        min_voltage_rms = (mVpp * 1e-3) / (2**nbits * np.sqrt(2))
        self.min_power_dbm = lin2db((min_voltage_rms**2 / Z0) / 1e-3)

        max_voltage_rms =  (mVpp * 1e-3) / np.sqrt(2)
        self.max_power_dbm = lin2db((max_voltage_rms**2 / Z0) / 1e-3)
    
    def __repr__(self):
        toprint = f"{self.name}: {self.nbits} bits, {self.mVpp} mVpp\n"
        toprint += f"    Minimum input power: {self.min_power_dbm:2.2f} dBm\n"
        toprint += f"    Maximum input power: {self.max_power_dbm:2.2f} dBm\n"
        return toprint


    
class AnalogSystem(object):
    """ Analog receiver system """
    def __init__(self, bw, name='Analog System'):
        self.components = []
        self.Tsys = 0
        self.Gsys = 1
        self.bw   = bw
        self.name = name
    
    def __repr__(self):
        toprint = f'\n############   {self.name}  ########### \n'
        toprint+= f"System bandwidth: {self.bw/1e6} MHz \n"
        toprint += "\n###  Signal chain: \n"
        toprint += f"{'Component':<16s}  | {'Temp (K)':<10s} | {'Gain (dB)':<10s} \n"
        toprint += "-" * 42 + "\n"
        for c in self.components:
            if not str(c).startswith('-'):
                toprint += " " + str(c)
            #else:
            #    toprint += "\n" + str(c) + "\n"
                
        toprint += "-" * 45 + "\n"
        return toprint
    
    def add_component(self, comp):
        """ Add a component to the receiver chain 
        
        Parameters
        ----------
        comp: Component()
            Analog Component object to add
        """
        
        self.components.append(comp)

    def add_break(self, breakname):
        breakstr = "{:-^98}".format(breakname)
        self.components.append(breakstr)
    
    def compute_tsys(self):
        """ Compute the Tsys of the analog system 
        
        Notes
        -----
        Tsys = T1 + T2 / G1 + T3 / G1*G2 + ... 
        """
        
        Tsys = 0.0
        Gsys = 1.0
        kB = 1.380649e-23 * 1e6  
        inv_IP3 = 10e-101
        
        print(self.__repr__())

        print("\n### Cascaded system: \n")
        print("   " + "-" * 98 )
        print("     Component        |   T_comp   |   G_comp      ||   T_sys    |    G_sys   |   P_sys    |   IP3 ")
        print("                      |     (K)    |    (dB)       ||    (K)     |    (dB)    |   (dBm)    |  (dBm)")
        print("   " + "-" * 98)
        for comp in self.components:
            if isinstance(comp, str):
                print("   " + comp)
            else:
                Tx = comp.T
                Gx = comp.G
                inv_IP3x = 1 / comp.IP3
                
            
                Tx_w  = Tx / Gsys
                
                Tsys += Tx_w
                Gsys *= Gx
                inv_IP3 += inv_IP3x
                #print(inv_IP3x, inv_IP3)
            
                G_db = 10*np.log10(Gsys)
                IP3_dbm = 10*np.log10(1.0/inv_IP3)
                P0    = kB * self.bw * Tsys
                P_dbm = 10 * np.log10( P0 / 1e3) + G_db
                cstr = str(comp.__repr__()).strip()
                print(f"{cstr:^50} || {Tsys:^10.2f} | {G_db:^10.2f} | {P_dbm:^10.2f} | {IP3_dbm:^10.2f}")
        print("   " + "-" * 98 + "\n")

        return {'Tsys_K': Tsys, 'Gsys_dbm': Gsys, 'IP3_dbm': IP3_dbm, 'Pout_dbm': P_dbm}
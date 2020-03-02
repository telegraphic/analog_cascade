#!/usr/bin/env python

import numpy as np
from analog import AnalogSystem, AnalogComponent

if __name__ == '__main__':
    
    # Misc stuff
    sky       = AnalogComponent('Skynoise',   '6K',  '0dB')
    spillover = AnalogComponent('Spillover',   '5K',  '0dB')
    balun  = AnalogComponent('Balun loss', '0.3dB', '-0.3dB', amb_temp=290)
    bpf    = AnalogComponent('Bandpass',   '0.3dB', '-0.3dB', amb_temp=290)
    sawfil = AnalogComponent('TA1494A',    '3.0dB', '-3dB',   amb_temp=290)
    rfof   = AnalogComponent('RFoF',       '7dB', '23.0dB')

    cable0  = AnalogComponent('Cable loss', '1.0dB', '-1.0dB', amb_temp=290)
    cable_to_ground  = AnalogComponent('Cable loss', '8.0dB', '-8.0dB', amb_temp=290)
    
    bf_insertion_loss = AnalogComponent('Bmfmr loss', '10.0dB', '-10.0dB', amb_temp=290)
    
    # Attenuators
    att_3  = AnalogComponent('VAT3-pad',  '3.00dB',   '-3.00dB')
    att_7  = AnalogComponent('Loss 7dB',  '7.00dB',   '-7.00dB')
    att_10  = AnalogComponent('Att 10dB',  '10.00dB',   '-10.00dB')
    att_05 = AnalogComponent('Loss 0.5 dB', '0.5dB',  '-0.5dB')
    att_01 = AnalogComponent('Loss 0.1 dB', '0.1dB',  '-0.1dB')

    # LNAs
    gali74 = AnalogComponent('Gali-74',   '2.66dB', '25.06dB')
    gali6  = AnalogComponent('Gali-6',    '4.5dB', '12.2dB')
    mga633 = AnalogComponent('MGA-633P8', '0.37dB', '18.0dB')
    sky671 = AnalogComponent('SKY67151',  '0.35dB', '19.0dB')
    pga103 = AnalogComponent('PGA-103', '0.6dB', '16.2dB')
    ag303  = AnalogComponent('AG3030-86', '3.0dB', '20.3dB')
    
    switch   = AnalogComponent('Switch', '0.5dB', '-0.5dB')
    combiner2 = AnalogComponent('2-way combiner', '0.6dB','2.4dB')
    combiner4 = AnalogComponent('4-way combiner', '0.7dB','5.3dB')
    combiner8 = AnalogComponent('8-way combiner', '0.8dB','8.2dB')
    
    zfl1000 = AnalogComponent('ZFL-1000', '6.29dB', '18.5dB') 
    
    snap800 = AnalogComponent('SNAP@800MHz', '14dB', '-14dB') 
    
    # Cascade network components
    utmost = AnalogSystem(bw=50e6)
    utmost.add_component(sky)
    utmost.add_break("Antenna")
    utmost.add_component(spillover)    
    utmost.add_component(balun)
    utmost.add_component(sky671)
    utmost.add_component(cable0)
    
    # BEAMFORMER
    utmost.add_break("Beamformer")
    utmost.add_component(pga103)
    utmost.add_component(sawfil)
    utmost.add_component(switch)
    utmost.add_component(switch)
    utmost.add_component(switch)
    utmost.add_component(switch)
    utmost.add_component(switch)
    utmost.add_component(switch)
    utmost.add_component(switch)
    utmost.add_component(switch)
    utmost.add_component(combiner4)
    utmost.add_component(combiner2)
    utmost.add_component(sawfil)
    utmost.add_component(pga103)
    
    # RFOF
    utmost.add_break("Backhaul")
    utmost.add_component(cable_to_ground)
    
    #utmost.add_component(ag303)
    #utmost.add_component(ag303)
    utmost.add_component(att_10)
    utmost.add_component(rfof)
    utmost.add_component(sawfil)
    utmost.add_component(pga103)
    utmost.add_component(snap800)

    
    print(utmost)
    utmost.compute_tsys()


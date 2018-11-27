#!/usr/bin/env python

import numpy as np
from analog import AnalogSystem, AnalogComponent

if __name__ == '__main__':
    
    # Misc stuff
    sky    = AnalogComponent('Skynoise',   '6K',  '0dB')
    balun  = AnalogComponent('Balun loss', '0.3dB', '-0.3dB', amb_temp=290)
    bpf    = AnalogComponent('Bandpass',   '0.3dB', '-0.3dB', amb_temp=290)
    rfof   = AnalogComponent('RFoF',       '7dB', '23.0dB')
    combiner = AnalogComponent('8-way combiner', '8.2dB','-0.8dB')
    
    # Attenuators
    att_3  = AnalogComponent('VAT3-pad',  '3.00dB',   '-3.00dB')
    att_7  = AnalogComponent('Loss 7dB',  '7.00dB',   '-7.00dB')
    att_05 = AnalogComponent('Loss 0.5 dB', '0.5dB',  '-0.5dB')
    att_01 = AnalogComponent('Loss 0.1 dB', '0.1dB',  '-0.1dB')

    # LNAs
    gali74 = AnalogComponent('Gali-74',   '2.66dB', '25.06dB')
    gali6  = AnalogComponent('Gali-6',    '4.5dB', '12.2dB')
    mga633 = AnalogComponent('MGA-633P8', '0.37dB', '18.0dB')
    sky671 = AnalogComponent('SKY67151',  '0.35dB', '19.0dB')
    
    zfl1000 = AnalogComponent('ZFL-1000', '6.29dB', '18.5dB') 
    
    
    # Cascade network components
    utmost = AnalogSystem()
    utmost.add_component(sky)
    utmost.add_component(balun)
    #utmost.add_component(bpf)
    utmost.add_component(att_01)
    utmost.add_component(sky671)
    #utmost.add_component(gali6)
    utmost.add_component(combiner)
    utmost.add_component(gali6)
    utmost.add_component(att_7)
    #utmost.add_component(sky671)
    utmost.add_component(zfl1000)
    #utmost.add_component(sky671)
    #utmost.add_component(rfof)
    
    print utmost
    utmost.compute_tsys()


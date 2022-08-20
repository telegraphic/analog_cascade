#!/usr/bin/env python

import numpy as np
from analog import AnalogSystem, AnalogComponent, SkySpectrum, ADC

# 8-bit ADC (500 mVpp) 
# -44.1 dBm input minimum, 4.0 dBm maximum input
# Nominal input power -27 dBm, allowing 5 bits overhead

if __name__ == '__main__':
    
    # Components
    sky_freqs  = np.arange(50, 300, 10)
    sky        = SkySpectrum(sky_freqs)
    coupler    = AnalogComponent('Cplr ZX30-20-4-S', '0.29dB', '-0.29dB')
    amp_zfl500 = AnalogComponent('ZFL-500HLN', '3.8dB', '19dB', IP3='30dBm')
    xswitch    = AnalogComponent('xSw MTS-18-12B', '0.1dB', '-0.1dB')
    splitter   = AnalogComponent('Power split', '3dB', '-3dB')
    cable_100m = AnalogComponent('100m Cable', '11.1dB', '-11.1dB')
    adc        = ADC(nbits=8, mVpp=500, name='Signatek card')
    
    
    # Cascade network components
    hyp = AnalogSystem(bw=300e6, name='HYPEREION Analog chain')
    hyp.add_break("Sky")
    hyp.add_component(sky)
    
    hyp.add_break("Frontend")
    hyp.add_component(coupler)
    hyp.add_component(amp_zfl500)
    hyp.add_component(xswitch)
    hyp.add_component(splitter)
    
    hyp.add_break("Backend")
    hyp.add_component(cable_100m)
    hyp.add_component(amp_zfl500)
    hyp.add_component(amp_zfl500)
    
    stats = hyp.compute_tsys()

    #print(stats['Pout_dbm'], 'dBm')
    print(adc)
    adc.bit_occupancy(stats['Pout_dbm'])
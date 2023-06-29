import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
from tqdm import tqdm

from AH2550A import AH2550A
from AbsorberAttractorAssembly import *

micron_per_cm = 1e6/1e2
cap_to_sep = lambda c: 50*140/c  # very rough --> get real numbers from Albert

piezo_controller_port = 'COM3'
bridge_resource_name = 'GPIB0::28::INSTR'

basename = '20230629_voltagescan_fullrange'

AAA = AbsorberAttractorAssembly(piezo_controller_port)

bridge = AH2550A(bridge_resource_name, timeout=1e4)
c, l, v = bridge.single_measurement()

initial_separation = cap_to_sep(c)

voltages, step = np.linspace(0, 150, 150*100 + 1, retstep=True)
assert step==0.01, "something wrong with linspace"

voltages = voltages[::-1]
outfilebase = basename + '_decreasingV'


samples_per_voltage = 10

start_voltages = AAA.get_voltages()
outdata = []
for i in tqdm(range(len(voltages))):
    AAA.set_voltages(np.array([voltages[i]]*3))
    time.sleep(0.1)
    c = np.zeros(samples_per_voltage)
    l = np.zeros(samples_per_voltage)
    v = np.zeros(samples_per_voltage)
    for j in range(samples_per_voltage):
        c[j], l[j], v[j] = bridge.single_measurement() # TODO: add multi-measurement taking
    outdict = dict(
        voltage=voltages[i],
        cmean=c.mean(),
        cstd=c.std(),
        lmean=l.mean(),
        lstd=l.std(),
        vmean=v.mean(),
        vstd=v.std(),
    )
    print(outdict)
    outdata.append(outdict)
    with open(outfilebase+'.dat', 'a') as f:
        f.write(' '.join(map(str, list(outdict.values()))) + '\n')
df = pd.DataFrame(outdata)
df.to_csv(outfilebase+'.csv')
plt.plot(df.voltage, 1.0/df.cmean, label='decreasing voltage')

# go backward
voltages = voltages[::-1]
outfilebase = basename + '_increasingV'
start_voltages = AAA.get_voltages()
outdata = []
for i in range(len(voltages)):
    AAA.set_voltages(np.array([voltages[i]]*3))
    c = np.zeros(samples_per_voltage)
    l = np.zeros(samples_per_voltage)
    v = np.zeros(samples_per_voltage)
    for j in range(samples_per_voltage):
        c[j], l[j], v[j] = bridge.single_measurement() # TODO: add multi-measurement taking
    outdict = dict(
        voltage=voltages[i],
        cmean=c.mean(),
        cstd=c.std(),
        lmean=l.mean(),
        lstd=l.std(),
        vmean=v.mean(),
        vstd=v.std(),
    )
    print(outdict)
    outdata.append(outdict)
    with open(outfilebase+'.dat', 'a') as f:
        f.write(' '.join(map(str, list(outdict.values()))) + '\n')
df = pd.DataFrame(outdata)
df.to_csv(outfilebase+'.csv')
plt.plot(df.voltage, 1.0/df.cmean, label='voltage')

plt.xlabel('piezo voltage')
plt.ylabel('1/C [pF-1]')
plt.savefig(basename + '.png')
plt.show()

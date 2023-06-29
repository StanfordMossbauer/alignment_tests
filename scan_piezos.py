import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time

from AH2550A import AH2550A
from MDT693B import MDT693B

cap_to_sep = lambda c: 50*140/c  # very rough --> get real numbers from Albert

piezo_controller_port = 'COM3'
bridge_resource_name = 'GPIB0::28::INSTR'

volts_per_micron = 150.0/1150  # using available stroke of piezo
micron_per_cm = 1e6/1e2
two_piezo_distance_cm = 9.128  # from SW model

piezo_controller = MDT693B(piezo_controller_port)
#piezo_controller.set_all_voltage(75)

bridge = AH2550A(bridge_resource_name, timeout=1e4)
c, l, v = bridge.single_measurement()

#c = 100.  # pF
initial_separation = cap_to_sep(c)

test_angle_max = 6*np.arcsin((initial_separation)/(two_piezo_distance_cm*micron_per_cm/2))  # keep plates from crashing

angles_to_try = np.linspace(-test_angle_max, test_angle_max, 11)

matrices = dict(
	theta =  -1 * np.sqrt(3)/4 * two_piezo_distance_cm * micron_per_cm * np.array([1.0, -0.5, -0.5]),
	phi = two_piezo_distance_cm * micron_per_cm * np.array([0., -0.5, 0.5])
)

samples_per_angle = 2

filename_base = '20230628_thetascan_30umsep_1'
start_str = 'Radians\tpF\tLoss[nS]\tVolts'
print(start_str)

dfs = {}
start_voltages = piezo_controller.get_voltages()
#for axis in ('phi',):
for axis in ('theta', 'phi'):
	matrix = matrices[axis]
	outdata = []
	for angle in angles_to_try:
		distance_adjustment = matrix * np.sin(angle)
		voltage_adjustments = -1 * matrix * np.sin(angle) * volts_per_micron
		voltages = start_voltages + voltage_adjustments
		_ = piezo_controller.set_voltages(voltages)
		time.sleep(0.1)
		assert (_==[1,1,1]),"voltage setting failed"
		for trial in range(samples_per_angle):
			c, l, v = bridge.single_measurement()
			data_str = f'{voltages}\t{angle}\t{c}\t{l}\t{v}\n'
			print(data_str)
			outdata.append(
				dict(
					dist1=distance_adjustment[1],
					v0=voltages[0],
					v1=voltages[1],
					v2=voltages[2],
					angle=angle, capacitance=c, loss=l, voltage=v)
				)
	dfs[axis] = pd.DataFrame(outdata)
	dfs[axis].to_csv(filename_base + f'_{axis}.csv')
	plt.plot(dfs[axis].dist1, dfs[axis].capacitance, '.', label=axis)
piezo_controller.set_voltages(start_voltages)  # return to start

plt.xlabel('Distance 2 [um]')
plt.ylabel('capacitance [pF]')
plt.legend()
plt.savefig(filename_base + '.png')
plt.show()
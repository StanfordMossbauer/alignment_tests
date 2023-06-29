import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from AH2550A import AH2550A
from MDT693B import MDT693B

cap_to_sep = lambda c: 50*140/c  # very rough --> get real numbers from Albert

piezo_controller_port = 'COM3'
bridge_resource_name = 'GPIB0::28::INSTR'

volts_per_micron = 150.0/1150  # using available stroke of piezo
micron_per_cm = 1e6/1e2
two_piezo_distance_cm = 9.128  # from SW model

piezo_controller = MDT693B(piezo_controller_port)
piezo_controller.set_all_voltage(90)

bridge = AH2550A(bridge_resource_name, timeout=1e4)
c, l, v = bridge.single_measurement()


matrices = dict(
	theta =  np.sqrt(3)/4 * two_piezo_distance_cm * micron_per_cm * np.array([1.0, -0.5, -0.5]),
	phi = two_piezo_distance_cm * micron_per_cm * np.array([0., -0.5, 0.5])
)

angles_to_try = np.linspace(0, 1*np.pi/180, 10)

start_str = 'Radians\tpF\tLoss[nS]\tVolts'
start_voltages = piezo_controller.get_voltages()
for axis in ('theta', 'phi'):
	matrix = matrices[axis]
	for angle in angles_to_try:
		voltage_adjustments = matrix * np.sin(angle) * volts_per_micron
		voltages = start_voltages + voltage_adjustments
		_ = piezo_controller.set_voltages(voltages)
		c, l, v = bridge.single_measurement()
		angledeg = angle*180/np.pi
		data_str = f'{angledeg}\t{c}\t{l}\t{v}\n'
		print(data_str)
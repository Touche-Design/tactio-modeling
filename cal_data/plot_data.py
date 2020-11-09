import json
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit 


filename = 'cal_data/run1_no_weight.json'
weight_file = {
    0:'cal_data/run1_no_weight.json',
    50:'cal_data/run2_50g_center.json',
    100:'cal_data/run10_100g_center.json',
    200:'cal_data/run11_200g_center.json',
    300:'cal_data/run12_300g_center.json',
    400:'cal_data/run13_400g_center.json',
    600:'cal_data/run14_600g_center.json',
    700:'cal_data/run15_700g_center.json',
    800:'cal_data/run16_800g_center.json',
    900:'cal_data/run17_900g_center.json',
    950:'cal_data/run18_950g_center.json',
    1000:'cal_data/run19_1000g_center.json'}

weight_values = []
avg_sensor_values = []
max_sensor_values = []
for weight in weight_file:
    file = open(weight_file[weight],'r')
    data = json.load(file)
    focusData = data["0"]
    averagedData = np.average(np.average(focusData,axis=0))
    maxData = np.max(focusData)
    weight_values.append(weight)
    avg_sensor_values.append(averagedData)
    max_sensor_values.append(maxData) 


fig = plt.figure()
ax = fig.add_axes([0, 0, 1, 1])

ax.plot(weight_values,avg_sensor_values, 'ro')
ax.plot(weight_values,max_sensor_values, 'bo')
ax.set_xscale('log')
ax.set_yscale('log')

plt.show()
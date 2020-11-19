import json
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.stats import linregress
import os
import scipy.optimize as optim

def rmse(data, model):
    return np.sqrt(((model - data) ** 2).mean())

def my_logistic_growth(x,a,c,d,e):
    return a/(1+c*np.exp(-d*(x+e)))

def my_log(x,a,b,c,d,e):
    return a*np.log(d*((x+.1)+e)) + b

def my_exp(x,a,b,c,d,e):
    return a*(1-c*np.exp(-d*(x-e))) + b

def my_velostat_model(x,a,b,c,d,e):
    return a*(np.power(c*(x+e),d)) + b

position_label = ['bl', 'br', 'tl','tr']
file_path = 'cal_data'
files_present = []
nodes = []
for root, dirs, files in os.walk(file_path):
    if len(dirs) > 0:
        nodes.extend(dirs)
    
    if len(files) > 0:
        files_present.extend(files)

#Filters only node files and directories
nodes = [x for x in nodes if x.startswith('node')]
files_present = [x for x in files_present if x.startswith('node')]

full_data = {}
# Data organization
for node in nodes:
    node_data = {}
    node_files = []
    for file in files_present:
        file_name_split = file.split("_")
        if(node == file_name_split[0]):
            node_files.append(file)

    for position in position_label:
        position_data = {}
        postions_files_present = [x for x in node_files if x.endswith(position)]
        for node_file in postions_files_present:
            file = open(file_path+"/"+node+"/"+node_file,'r')
            data = json.load(file)
            file.close()
            node_number = node[4:]
            focusData = data[node_number]
            weight = node_file.split("_")[1]
            position = node_file.split("_")[2]
            position_data[int(weight)] = focusData
        node_data[position] = position_data
    
    full_data[node] = node_data


voltage = 3300
r2 = 390

ax0 = plt.subplot()
fig2, (ax2, ax3) = plt.subplots(ncols=2)
fig3, (ax4, ax5) = plt.subplots(ncols=2)
fig4, (ax6, ax7) = plt.subplots(ncols=2)
fig5, (ax8, ax9) = plt.subplots(ncols=2)
fig6, (ax10, ax11) = plt.subplots(ncols=2)

ax0.set_title("Conductance vs. Applied Pressure")
ax0.set_xlabel("Applied Pressure (kPa)")
ax0.set_ylabel("Conductance (S)")
ax2.set_title("Linear Models")
ax2.set_xlabel("Applied Pressure (kPa)")
ax2.set_ylabel("Conductance (S)")
ax3.set_title("Total Residual")
ax3.set_xlabel("Applied Pressure (kPa)")
ax3.set_ylabel("Conductance (S)")
ax4.set_title("Logistic Growth Models")
ax4.set_xlabel("Applied Pressure (kPa)")
ax4.set_ylabel("Conductance (S)")
ax5.set_title("Total Residual")
ax6.set_title("Logarithmic Models")
ax6.set_xlabel("Applied Pressure (kPa)")
ax6.set_ylabel("Conductance (S)")
ax7.set_title("Total Residual")
ax8.set_title("Exponential Models")
ax8.set_xlabel("Applied Pressure (kPa)")
ax8.set_ylabel("Conductance (S)")
ax9.set_title("Total Residual")
ax10.set_title("Velostat Model")
ax10.set_xlabel("Applied Pressure (kPa)")
ax10.set_ylabel("Conductance (S)")
ax11.set_title("Total Residual")

single_node = 'node20'
#full_cond_press_regression_param = {}
rmse_values = {}
for node_name in full_data:
    rmse_values_node = {}
    if node_name == node_name:
        pressure_values = []
        avg_sensor_values = []
        std_sensor_values = []
        for position in position_label:
            for weight in full_data[node_name][position]:
                current_data = full_data[node_name][position]
                current_data = np.array(current_data[weight])
                current_conductance = current_data/(r2*voltage  - r2 * current_data)
                current_conductance_time_avg = np.average(current_conductance,axis=0)

                # Samples the center 4 elements 
                time_avg_center_sample = np.zeros((2,2))
                time_avg_center_sample[0][0] = current_conductance_time_avg[1][1]
                time_avg_center_sample[0][1] = current_conductance_time_avg[1][2]
                time_avg_center_sample[1][0] = current_conductance_time_avg[2][1]
                time_avg_center_sample[1][1] = current_conductance_time_avg[2][2]
            
                # 0.125 in -> 0.003175 m
                # looking at 4 points so area is 4x
                area = 0.003175**2 * 4
                # weight in grams
                force = (weight/1000)*9.81

                #In KPa
                pressure = force / area / 1000

                averaged_data = np.average(time_avg_center_sample)
                pressure_values.append(pressure)
                avg_sensor_values.append(averaged_data)
                sample_data = np.array(current_data)

            pressure_values_np = np.array(pressure_values)
            avg_sensor_values_np = np.array(avg_sensor_values)

            # data scatter plots
            ax0.scatter(pressure_values, avg_sensor_values_np, color='orange', edgecolor='black')

            rmse_values_methods = {}
            # regression line plots
            # linear regression
            slope, intercept, r_value, p_value, std_err = linregress(pressure_values_np, avg_sensor_values_np)
            modeled_sensor_values = pressure_values_np * slope + intercept
            ax2.plot(pressure_values_np, modeled_sensor_values, '.', label = node_name)
            ax3.plot(pressure_values_np, modeled_sensor_values - avg_sensor_values_np, '.', label = node_name)
            rmse_values_methods['linear'] = rmse(avg_sensor_values_np,modeled_sensor_values)

            # logistic growth
            initial_weights = np.random.exponential(size=4)
            bounds = (0,100)
            (a,c,d,e),cov = optim.curve_fit(my_logistic_growth,pressure_values_np,avg_sensor_values_np, bounds = bounds, p0 = initial_weights)
            modeled_sensor_values = my_logistic_growth(pressure_values_np,a,c,d,e)
            ax4.plot(pressure_values_np, modeled_sensor_values, '.', label = node_name)
            ax5.plot(pressure_values_np, modeled_sensor_values - avg_sensor_values_np, '.', label = node_name)
            rmse_values_methods['logistic'] = rmse(avg_sensor_values_np,modeled_sensor_values)

            # logarithmic plots
            initial_weights = np.random.exponential(size=5)
            bounds = ([-100,-100,-1000,0,0],[100,100,100,100,1000])
            (a,b,c,d,e),cov = optim.curve_fit(my_log,pressure_values_np,avg_sensor_values_np, bounds = bounds, p0 = initial_weights)
            modeled_sensor_values = my_log(pressure_values_np,a,b,c,d,e)
            ax6.plot(pressure_values_np, modeled_sensor_values, '.', label = node_name)
            ax7.plot(pressure_values_np, modeled_sensor_values - avg_sensor_values_np, '.', label = node_name)
            rmse_values_methods['logarithmic'] = rmse(avg_sensor_values_np,modeled_sensor_values)

            # exponential plots
            initial_weights = np.random.exponential(scale=1/5,size=5)
            bounds = (0,1.5)
            (a,b,c,d,e),cov = optim.curve_fit(my_exp,pressure_values_np,avg_sensor_values_np, bounds = bounds, p0 = initial_weights)
            modeled_sensor_values = my_exp(pressure_values_np,a,b,c,d,e)
            ax8.plot(pressure_values_np, modeled_sensor_values, '.', label = node_name)
            ax9.plot(pressure_values_np, modeled_sensor_values - avg_sensor_values_np, '.', label = node_name)
            rmse_values_methods['exponential'] = rmse(avg_sensor_values_np,modeled_sensor_values)

            # velostat model plots
            '''initial_weights = np.random.exponential(scale=1/10,size=5)
            bounds = (0,.95)
            (a,b,c,d,e),cov = optim.curve_fit(my_velostat_model,pressure_values_np,avg_sensor_values_np, bounds = bounds, p0 = initial_weights)
            modeled_sensor_values = my_velostat_model(pressure_values_np,a,b,c,d,e)
            ax10.plot(pressure_values_np, modeled_sensor_values, '.', label = node_name)
            ax11.plot(pressure_values_np, modeled_sensor_values - avg_sensor_values_np, '.', label = node_name)
            rmse_values_methods['velostat'] = rmse(avg_sensor_values_np,modeled_sensor_values)'''

            rmse_values_node[position] = rmse_values_methods
        rmse_values[node_name] = rmse_values_node

linear = []
logistic = []
logarithmic = []
exponential = []
velostat = []
for node_name in full_data:
    for position in position_label:
        for method in rmse_values_methods:
            if method == 'linear':
                linear.append(rmse_values[node_name][position][method])
            if method == 'logistic':
                logistic.append(rmse_values[node_name][position][method])
            if method == 'logarithmic':
                logarithmic.append(rmse_values[node_name][position][method])
            if method == 'exponential':
                exponential.append(rmse_values[node_name][position][method])
            if method == 'velostat':
                velostat.append(rmse_values[node_name][position][method])
print(np.average(np.array(linear)))
print(np.average(np.array(logistic)))
print(np.average(np.array(logarithmic)))
print(np.average(np.array(exponential)))
print(np.average(np.array(velostat)))
plt.show()

from os import uname
import cantera as ct
import numpy as np
import pandas as pd
import os
import sys
import csv
import scipy
import scipy.optimize

############# functions for flamespeed analysis 
# Estimate uncertainty from grid size and speeds
# ----------------------------------------------

def extrapolate_uncertainty(grids, speeds):

    grids = list(grids)
    speeds = list(speeds)

    def speed_from_grid_size(grid_size, true_speed, error):
        return true_speed + error / np.array(grid_size)

    # Fit the chosen form of speed_from_grid_size, to the last four
    # speed and grid size values.
    popt, pcov = scipy.optimize.curve_fit(speed_from_grid_size, grids[-4:], speeds[-4:])

    # How bad the fit was gives you some error, `percent_error_in_true_speed`.
    perr = np.sqrt(np.diag(pcov))
    true_speed_estimate = popt[0]
    percent_error_in_true_speed = perr[0] / popt[0]
    print(
        f"Fitted true_speed is {popt[0] * 100:.4f} ± {perr[0] * 100:.4f} cm/s "
        f"({percent_error_in_true_speed:.1%})"
    )

    # How far your extrapolated infinite grid value is from your extrapolated
    # (or interpolated) final grid value, gives you some other error, `estimated_percent_error`
    estimated_percent_error = (
        speed_from_grid_size(grids[-1], *popt) - true_speed_estimate
    ) / true_speed_estimate
    print(f"Estimated error in final calculation {estimated_percent_error:.1%}")

    # The total estimated error is the sum of these two errors.
    total_percent_error_estimate = abs(percent_error_in_true_speed) + abs(
        estimated_percent_error
    )
    print(f"Estimated total error {total_percent_error_estimate:.1%}")

    return true_speed_estimate, total_percent_error_estimate

def make_callback(flame):
    speeds = []
    grids = []

    def callback(_):
        speed = flame.velocity[0]
        grid = len(flame.grid)
        speeds.append(speed)
        grids.append(grid)
        print(f"Iteration {len(grids)}")
        print(f"Current flame speed is is {speed * 100:.4f} cm/s")
        if len(grids) < 5:
            return 1.0  #
        try:
            extrapolate_uncertainty(grids, speeds)
        except Exception as e:
            print("Couldn't estimate uncertainty. " + str(e))
            return 1.0  # continue anyway
        return 1.0

    return callback, speeds, grids


#------------------------------------------------------------------


print("Running Cantera Version: " + str(ct.__version__))

To = 298
Po = 1e5 # ct.one_atm

#find the chemkin file that starts with final_model
# chemkin_file = [f for f in os.listdir(f'./chemkin/') if 'final_model' in f]
# assert len(chemkin_file)==1

directory = f'./chemkin/change_this'
print(directory)

slurm_i = int(sys.argv[-1])

gas = ct.Solution(directory)
blend_name = os.path.basename(os.getcwd())

blend_components = blend_name.split('_')

if any([s.name == f'{blend_components[0]}(1)' for s in gas.species()]):
    comp_1 = f'{blend_components[0]}(1)'
    comp_2 = f'{blend_components[1]}(2)'

if any([s.name == f'{blend_components[0]}(2)' for s in gas.species()]):
    comp_1 = f'{blend_components[1]}(1)'
    comp_2 = f'{blend_components[0]}(2)'

print(f' Found matching species: {comp_1} , {comp_2}')

vol_frac_list = list(np.linspace(0.025, 0.25, 60))
# vol_frac_list = [0.10]
results = dict()


#this part calculates the flame calcs for all of the vol_frac list, using the previous vol frac count as a guess for the current one
best_true_speed_estimates = []
best_total_percent_error_estimates = []
for i in [slurm_i-1]:
    try:

        string = f'****************************starting new volume fraction **************************'
        print(string)
        
        x = vol_frac_list[i]
        print(f'total volume fraction: {x}')
        norm_ox = (1-x)*.21

        vol_frac_dict = {comp_1: (x/2/norm_ox), comp_2: (x/2/norm_ox), 'O2(3)':((1-x)*.21)/norm_ox, 'N2':((1-x)*0.79)/norm_ox}
        gas.TPX = To, Po, vol_frac_dict
        width = 0.08
        flame = ct.FreeFlame(gas, width=width)
        flame.set_refine_criteria(ratio=3, slope=0.1, curve=0.1) 
        flame.max_time_step_count = 5000

        # Set maximum number of grid points to be very high (otherwise default is 1000)
        flame.set_max_grid_points(flame.domains[flame.domain_index("flame")], 1e4)
        
        # Set up the the callback function and lists of speeds and grids
        callback, speeds, grids = make_callback(flame)
        flame.set_steady_callback(callback)

        
        loglevel = 1 
        # try:
        #     if i!=0:
        #         d = f'speeds/speed_{i-1}.yaml'
        #         if os.path.exists(d):  
        #             # arr2 = ct.SolutionArray(gas)
        #             # arr2.read_csv(d)
        #             flame.set_initial_guess(data=d)
        #             print(' initial guess has been set')
        # except: 
        #     print('initial guess not set for this volume fraction')
        
        
        #"False" stops the calculation from retrying over and over
        flame.solve(loglevel=loglevel, auto=True)
        Su = flame.velocity[0]
        print(f'flamespeed = {Su}')
        # results[x] = Su
        flame.save(f'./speeds_134/speed_134_{x}.yaml')
        
        # sltn = flame.to_solution_array()
        # df1 = sltn.to_pandas()
        # df1.to_csv(f'./speeds/speed_{x}.txt', index=False)    
        
        if not os.path.exists('./speeds'): #make the directory if it isn't already made
            os.mkdir('./speeds')
    

        best_true_speed_estimate, best_total_percent_error_estimate = extrapolate_uncertainty(grids, speeds)
        print('got uncertainty')
        #once you get these, write them to a csv
        with open(f'./speeds_134/errors_134_{x}.csv', 'w+') as g:
            writers = csv.writer(g)
            writers.writerow([best_true_speed_estimate])   
            writers.writerow([best_total_percent_error_estimate])
    
        best_true_speed_estimates.append(best_true_speed_estimate)
        best_total_percent_error_estimates.append(best_total_percent_error_estimate)

        
        #error_data = analyze_errors(grids, speeds, best_true_speed_estimate)

        
            
    except Exception as e: 
        print(f'********************passed volume fraction:{vol_frac_list[i]}, error: {e}*************************************')
        pass

# vol_fracs = list(results.keys())
# flame_speeds = list(results.values())


# print("volume fractions are:")
# print(vol_fracs)

# print("flame speeds are:")
# print(flame_speeds)

# print('best_true_speed_estimates:')
# print(best_true_speed_estimates)

# print('best_total_percent_error_estimates:')
# print(best_total_percent_error_estimates)

    
# with open(f'./speeds/final_speeds.csv', 'w+') as g:
#     writers = csv.writer(g)
#     writers.writerow(vol_fracs)
#     writers.writerow(flame_speeds)
#     # writers.writerow(directory)
#     writers.writerow(best_true_speed_estimates)   
#     writers.writerow(best_total_percent_error_estimates)

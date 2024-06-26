import sys
sys.path.append('/')  # I dont know why this is there
import json
import os
import harreveltools.plot as hplot
from objective_helper.fourteenT import ReadMatData, OptimizeData
from objective_configuration.fourteenT import CALC_OPTIONS, DDATA, MAX_ITER

"""
This script is used to optimize the data for the given CALC_OPTIONS.
The CALC_OPTIONS describe where we store the data, what kind of regularization is used and what kind of mask we use
Where we store the data depends on the options given.


"""

file_list = os.listdir(DDATA)
mat_files = [x for x in file_list if x.endswith('mat')]

for i_options in CALC_OPTIONS:
    full_mask = i_options['full_mask']
    type_mask = i_options['type_mask']
    objective_str = i_options['objective_str']
    ddest = i_options['ddest']
    print(ddest)
    # Here we load one simulation file
    print('mat files', mat_files)
    for sel_mat_file in mat_files:
        print('\t\t', sel_mat_file)
        # This is a wrapper to read all the data and do a bit of preprocessing. Initially it does nothing.
        mat_reader = ReadMatData(ddata=DDATA, mat_file=sel_mat_file)
        # Here we load all the data (in the parentclass called DataCollector)
        # This is also the object where the optimization takes place
        data_obj = OptimizeData(ddest=ddest, objective_str=objective_str,
                                mat_reader=mat_reader, full_mask=full_mask, type_mask=type_mask)
        print('Data is loaded')
        # Here we run the optimization multiple times, because we were getting local optima
        # Running it multiple times helped to find the global optima a bit better over all iterations
        # Note that this means that more post-processing is needed after we have obtained all the results
        for iteration in range(MAX_ITER):
            iteration_str = str(iteration).zfill(2)
            result_dict_list = data_obj.solve_trade_off_objective(max_iter=100)
            result_dict_list['opt_shim'] = [[list(x.real), list(x.imag)] for x in result_dict_list['opt_shim']]
            json_ser_obj = json.dumps(result_dict_list)
            # Create the file path for the optimal thing..
            ddest_dict = os.path.join(data_obj.ddest_optim_shim_coil, f'opt_shim_{iteration_str}.json')
            with open(ddest_dict, 'w') as f:
                f.write(json_ser_obj)

            hplot.close_all()
        # Remove these objects to release some memory
        del mat_reader
        del data_obj


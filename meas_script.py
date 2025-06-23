import time
from PyLTSpice import SimRunner
from pathlib import Path
from spicelib.editor.asc_editor import AscEditor

from pathlib import Path
from PyLTSpice import RawRead
import numpy as np
import csv
from openpyxl import Workbook
start = time.time()


def is_component_line(line):
    skip_keywords = ['.model', '.lib', '.tran', '.TEMP', '.end', '.backanno']
    if not line or line.startswith(('*', ';')):
        return False
    return not any(line.lower().startswith(k.lower()) for k in skip_keywords)

# To identify the nodes between the devices

def parse_netlist(filepath):
    netlist_path = Path(filepath)
    components = {}

    with netlist_path.open() as f:
        for line in f:
            line = line.strip()
            if not is_component_line(line):
                continue

            tokens = line.split()
            if not tokens:
                continue

            comp_name = tokens[0]
            nodes = [t for t in tokens[1:] if t.upper().startswith("N") or t == '0']
            
            components[comp_name] = tuple(nodes)

    return components


# Set your schematic folder as the custom library path for .asy and .lib files
project_folder = r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata"

AscEditor.set_custom_library_paths(
    project_folder,  # for .lib files (subcircuits)
    project_folder   # for .asy files (symbols)
)

# Paths
asc_file_path = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata\FPL_center.asc")
netfile_path = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata\FPL_center_netlist.txt")
out_path = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata")

# Load the schematic netlist
netlist = AscEditor(str(asc_file_path))



comp_dict = parse_netlist(netfile_path)




meas_cmds = []
for comp in comp_dict:
    if comp[0] not in ['Q','X']:
        meas_cmds.append(f".meas TRAN I_max_{comp} MAX I({comp}) FROM=0 TO=10m")
        meas_cmds.append(f".meas TRAN nI_max_{comp} MAX -I({comp}) FROM=0 TO=10m")
        v_plus,v_minus = comp_dict[comp][:2]
        print(v_plus,v_minus)

        if v_minus == '0':
            meas_cmds.append(f".meas TRAN V_max_{comp} MAX V({v_plus}) FROM=0 TO=10m")
            meas_cmds.append(f".meas TRAN nV_max_{comp} MAX -V({v_plus}) FROM=0 TO=10m")
            meas_cmds.append(f".meas TRAN p_max_{comp} MAX V({v_plus})*I({comp}) FROM=0 TO=10m")
            meas_cmds.append(f".meas TRAN np_max_{comp} MAX -V({v_plus})*I({comp}) FROM=0 TO=10m")
        elif v_plus == '0':
            meas_cmds.append(f".meas TRAN V_max_{comp} MAX V({v_minus}) FROM=0 TO=10m")
            meas_cmds.append(f".meas TRAN nV_max_{comp} MAX -V({v_minus}) FROM=0 TO=10m")
            meas_cmds.append(f".meas TRAN p_max_{comp} MAX V({v_minus})*I({comp}) FROM=0 TO=10m")
            meas_cmds.append(f".meas TRAN np_max_{comp} MAX -V({v_minus})*I({comp}) FROM=0 TO=10m")
        else:
            meas_cmds.append(f".meas TRAN V_max_{comp} MAX V({v_plus},{v_minus}) FROM=0 TO=10m")
            meas_cmds.append(f".meas TRAN nV_max_{comp} MAX -V({v_plus},{v_minus}) FROM=0 TO=10m")
            meas_cmds.append(f".meas TRAN p_max_{comp} MAX V({v_plus},{v_minus})*I({comp}) FROM=0 TO=10m")
            meas_cmds.append(f".meas TRAN np_max_{comp} MAX -V({v_plus},{v_minus})*I({comp}) FROM=0 TO=10m")
    if comp[0] == 'Q':
        meas_cmds.append(f".meas TRAN Ic_max_Q1 MAX Ic(Q1)")
        meas_cmds.append(f".meas TRAN Ib_max_Q1 MAX Ib(Q1)")
        meas_cmds.append(f".meas TRAN Ie_max_Q1 MAX Ie(Q1)")
        meas_cmds.append(f'.meas TRAN V_max_Q1 MAX V(N005,N006)')
        meas_cmds.append(f".meas TRAN P_max_Q1 MAX (V(N005)*Ic(Q1))")
    if comp[0] == 'X':
        meas_cmds.append(f".meas TRAN id_max_X MAX Ix(U2:1)")
        meas_cmds.append(f".meas TRAN nid_max_X  MAX -Ix(U2:1)")
        meas_cmds.append(f".meas TRAN ig_max_X  MAX Ix(U2:2)")
        meas_cmds.append(f".meas TRAN nig_max_X  MAX -Ix(U2:2)")
        meas_cmds.append(f".meas TRAN is_max_X  MAX Ix(U2:3)")
        meas_cmds.append(f".meas TRAN nis_max_X  MAX -Ix(U2:3)")
        meas_cmds.append(f".meas TRAN P_max_X MAX ((V(N004)*Ix(U2:1)) + (V(N005)*Ix(U2:2)) +(V(N006)*Ix(U2:3)))")
    # # .meas TRAN Imax_Q1 MAX @Q1[ic]
    # # .meas TRAN Vmax_Q1 MAX V(N005,0)
    # #  .meas TRAN Pmax_Q1 MAX PARAM (V(N005,0)*@Q1[ic])

    
    else:
        continue
       
    

netlist.set_component_value("V2", "{V2}")
# Add simulation directives
netlist.add_instructions(
    "; Simulation settings",
    ".tran 10u 10m 0 10u",
    ".step param V2 list 9 12 16",  # ✅ correct

    ".step temp list -10 25 85",
    *meas_cmds
)

# Output directory
output_folder = out_path / "batch_run"
output_folder.mkdir(parents=True, exist_ok=True)

# Run the simulation
sim = SimRunner(output_folder=str(output_folder), simulator=None)
ksim = sim.run(netlist)
print("\u2705 Batch simulation completed")

end = time.time()
print(f"\u2705 Execution time: {end - start:.3f} seconds")

# import time
# from PyLTSpice import SimRunner
# from pathlib import Path
# from spicelib.editor.asc_editor import AscEditor

# start = time.time()

# # === CONFIGURATION ===
# project_folder = r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata"
# asc_file_path = Path(project_folder) / "FPL_center.asc"
# out_path = Path(project_folder)

# # Set custom paths for .lib and .asy files
# AscEditor.set_custom_library_paths(
#     project_folder,  # Subcircuit libraries
#     project_folder   # Symbol files
# )

# # === LOAD SCHEMATIC ===
# netlist = AscEditor(str(asc_file_path))

# # Define components to analyze
# components = [
#     "D1", "D2", "D4", "D10", "R1", "R2", "R4", "R5"
# ]

# # === GENERATE .meas STATEMENTS FOR MAX VOLTAGE DROP ===
# meas_cmds = []

# for comp in components:
#     pins = netlist.get_component_nodes(comp)
#     print(pins)
#     if len(pins) >= 2:
#         n_plus, n_minus = pins[:2]
#         meas_cmds.append(
#             f".meas TRAN V_max_{comp} MAX V({n_plus},{n_minus}) FROM=0 TO=10m"
#         )
#     else:
#         print(f"⚠️ Component {comp} has fewer than 2 nodes: {pins}")

# # === SET PARAMETERIZED VALUES ===
# netlist.set_component_value("V2", "{V2}")

# # === ADD SIMULATION DIRECTIVES ===
# netlist.add_instructions(
#     "; Simulation settings",
#     ".tran 10u 10m 0 10u",
#     ".step param V2 list 9 12 16",
#     ".step temp list -10 25 85",
#     *meas_cmds
# )

# # === RUN SIMULATION ===
# output_folder = out_path / "batch_run"
# output_folder.mkdir(parents=True, exist_ok=True)

# sim = SimRunner(output_folder=str(output_folder), simulator=None)
# ksim = sim.run(netlist)

# print("✅ Batch simulation completed")

# end = time.time()
# print(f"✅ Execution time: {end - start:.3f} seconds")
# import re
# import csv
# from collections import defaultdict
# from pathlib import Path

# # === Replace this with your actual LTspice log file path ===
# log_file_path = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata\batch_run\FPL_center_1.log")

# # Define step condition map (index starts from 1 in LTspice)
# step_conditions = [
#     (-10, 9),
#     (-10, 12),
#     (-10, 16),
#     (25, 9),
#     (25, 12),
#     (25, 16),
#     (85, 9),
#     (85, 12),
#     (85, 16),
# ]


# # Data structure: {component: {metric: [values]}}
# component_data = defaultdict(lambda: defaultdict(list))

# # Regular expressions
# measure_header_pattern = re.compile(r"Measurement:\s+(\w+)")
# data_line_pattern = re.compile(r"\s*(\d+)\s+([\d.eE+-]+)")

# current_component = None
# current_metric = None

# with open(log_file_path, 'r') as file:
#     for line in file:
#         # Check for measurement header
#         match_header = measure_header_pattern.match(line)
#         if match_header:
#             measure_name = match_header.group(1)
#             # Metric will be something like i_max_d1 → i_max, component = d1
#             parts = measure_name.split('_')
#             if len(parts) >= 3:
#                 metric = f"{parts[0]}_{parts[1]}"  # e.g. i_max
#                 component = parts[2].upper()        # e.g. D1
#             else:
#                 metric = parts[0]
#                 component = parts[1].upper()
#             current_component = component
#             current_metric = metric
#             continue

#         # Parse numerical measurement rows
#         match_data = data_line_pattern.match(line)
#         if match_data and current_component and current_metric:
#             step_index = int(match_data.group(1)) - 1  # 0-based index
#             value = float(match_data.group(2))
#             component_data[current_component][current_metric].append(value)

# # === CSV Output ===
# script_dir = Path(__file__).resolve().parent
# output_folder = script_dir / "component_csvs"
# output_folder.mkdir(parents=True, exist_ok=True)

# for component, metrics in component_data.items():
    
#     filename =  output_folder / f"{component}.csv"

#     with open(filename, mode='w', newline='') as f:
#         writer = csv.writer(f)
#         writer.writerow(["Temperature (°C)", "Voltage Level (V)", "Peak Voltage (V)", "Peak Current (A)", "Peak Power (W)"])
        
#         for i in range(len(step_conditions)):
#             temp, volt = step_conditions[i]
#             v_peak = metrics.get("v_max", [None]*9)[i]
#             i_peak = metrics.get("i_max", [None]*9)[i]
#             p_peak = metrics.get("p_max", [None]*9)[i]
#             writer.writerow([temp, volt, v_peak, i_peak, p_peak])

# print("\u2705 CSV files generated for all components.")
'''--------------------------------------------------------------------------------------------------------------------------'''
'''Works for two termianl devices'''
# import re
# import csv
# from collections import defaultdict
# from pathlib import Path

# # === Replace this with your actual LTspice log file path ===
# log_file_path = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata\batch_run\FPL_center_1.log")

# # Define step condition map (index starts from 1 in LTspice)
# step_conditions = [
#     (-10, 9), (-10, 12), (-10, 16),
#     (25, 9),  (25, 12),  (25, 16),
#     (85, 9),  (85, 12),  (85, 16),
# ]

# # Data structure: {component: {metric: [values]}}
# component_data = defaultdict(lambda: defaultdict(list))

# # Regex patterns
# measure_header_pattern = re.compile(r"Measurement:\s+(\w+)")
# data_line_pattern = re.compile(r"\s*(\d+)\s+([-+eE\d.]+)")

# current_component = None
# current_metric = None

# with open(log_file_path, 'r') as file:
#     for line in file:
#         # Detect measurement block start
#         match_header = measure_header_pattern.match(line)
#         if match_header:
#             measure_name = match_header.group(1)
#             parts = measure_name.split('_')
#             if len(parts) >= 3:
#                 metric = f"{parts[0]}_{parts[1]}"  # e.g. i_max, ni_max, nv_max, etc.
#                 component = parts[2].upper()
#             else:
#                 metric = parts[0]
#                 component = parts[1].upper()
#             current_component = component
#             current_metric = metric
#             continue

#         # Extract numerical measurement
#         match_data = data_line_pattern.match(line)
#         if match_data and current_component and current_metric:
#             value = float(match_data.group(2))
#             component_data[current_component][current_metric].append(value)

# # === CSV Output ===
# script_dir = Path(__file__).resolve().parent
# output_folder = script_dir / "component_csvs_updated"
# output_folder.mkdir(parents=True, exist_ok=True)

# for component, metrics in component_data.items():
#     filename = output_folder / f"{component}.csv"

#     with open(filename, mode='w', newline='') as f:
#         writer = csv.writer(f)
#         writer.writerow([
#             "Temperature (°C)",
#             "Voltage Level (V)",
#             "Peak Voltage (V)",
#             "Negative Peak Voltage (V)",
#             "Peak Current (A)",
#             "Negative Peak Current (A)",
#             "Peak Power (W)",
#             "Negative Peak Power (W)"
#         ])

#         for i in range(len(step_conditions)):
#             temp, volt = step_conditions[i]
#             v_peak   = metrics.get("v_max",   [None]*9)[i]
#             nv_peak  = metrics.get("nv_max",  [None]*9)[i]
#             i_peak   = metrics.get("i_max",   [None]*9)[i]
#             ni_peak  = metrics.get("ni_max",  [None]*9)[i]
#             p_peak   = metrics.get("p_max",   [None]*9)[i]
#             np_peak  = metrics.get("np_max",  [None]*9)[i]

#             writer.writerow([temp, volt, v_peak, nv_peak, i_peak, ni_peak, p_peak, np_peak])

# print("\u2705 CSV files updated with negative peak voltage and power.")

import re
import csv
from collections import defaultdict
from pathlib import Path

# === Replace this with your actual LTspice log file path ===
log_file_path = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata\batch_run\FPL_center_1.log")

# Define step condition map (index starts from 1 in LTspice)
step_conditions = [
    (-10, 9), (-10, 12), (-10, 16),
    (25, 9),  (25, 12),  (25, 16),
    (85, 9),  (85, 12),  (85, 16),
]

# Data structure: {component: {metric: [values]}}
component_data = defaultdict(lambda: defaultdict(list))

# Regex patterns
measure_header_pattern = re.compile(r"Measurement:\s+(\w+)")
data_line_pattern = re.compile(r"\s*(\d+)\s+([-+eE\d.]+)")

current_component = None
current_metric = None

with open(log_file_path, 'r') as file:
    for line in file:
        # Detect measurement block start
        match_header = measure_header_pattern.match(line)
        if match_header:
            measure_name = match_header.group(1).lower()
            parts = measure_name.split('_')
            if len(parts) >= 3:
                metric = f"{parts[0]}_{parts[1]}"  # e.g. id_max
                component = parts[2].upper()
            else:
                metric = parts[0]
                component = parts[1].upper()
            current_component = component
            current_metric = metric
            # print(current_component,current_metric)
            continue
            
        # Extract numerical measurement
        match_data = data_line_pattern.match(line)
        if match_data and current_component and current_metric:
            value = float(match_data.group(2))
            component_data[current_component][current_metric].append(value)


#=== CSV Output ===
script_dir = Path(__file__).resolve().parent
output_folder = script_dir / "final_run"
output_folder.mkdir(parents=True, exist_ok=True)

for component, metrics in component_data.items():
    filename = output_folder / f"{component}.csv"

    # Special case: Q1 (BJT)
    if component == "Q1":
        with open(filename, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Temperature (°C)",
                "Voltage Level (V)",
                "Vce (V)",
                "Ic (A)",
                "Ib (A)",
                "Ie (A)",
                "Power Dissipation (W)"
            ])
            for i in range(len(step_conditions)):
                temp, volt = step_conditions[i]
                ic = metrics.get("ic_max", [None]*9)[i]
                ib = metrics.get("ib_max", [None]*9)[i]
                ie = metrics.get("ie_max", [None]*9)[i]
                vce = metrics.get("v_max",  [None]*9)[i]
                p   = metrics.get("p_max",  [None]*9)[i]
                writer.writerow([temp, volt, vce, ic, ib, ie, p])

    # Special case: X (U2 subcircuit)
    elif component[0] == "X":
        filename = output_folder / f"{component[0]}.csv"

        with open(filename, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Temperature (°C)", "Voltage Level (V)",
                "Id (A)", "-Id (A)",
                "Ig (A)", "-Ig (A)",
                "Is (A)", "-Is (A)",
                "Power (W)"
            ])
            for i in range(len(step_conditions)):
                temp, volt = step_conditions[i]
                id_  = metrics.get("id_max",    [None]*9)[i]
                nid  = metrics.get("nid_max",    [None]*9)[i]
                ig   = metrics.get("ig_max",    [None]*9)[i]
                nig  = metrics.get("nig_max",   [None]*9)[i]
                is_  = metrics.get("is_max",    [None]*9)[i]
                nis  = metrics.get("nis_max",   [None]*9)[i]
                p    = metrics.get("p_max",     [None]*9)[i]
                writer.writerow([temp, volt, id_, nid, ig, nig, is_, nis, p])

    # Default case: all other components
    else:
        with open(filename, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Temperature (°C)",
                "Voltage Level (V)",
                "Peak Voltage (V)",
                "Negative Peak Voltage (V)",
                "Peak Current (A)",
                "Negative Peak Current (A)",
                "Peak Power (W)",
                "Negative Peak Power (W)"
            ])
            for i in range(len(step_conditions)):
                temp, volt = step_conditions[i]
                v_peak  = metrics.get("v_max",   [None]*9)[i]
                nv_peak = metrics.get("nv_max",  [None]*9)[i]
                i_peak  = metrics.get("i_max",   [None]*9)[i]
                ni_peak = metrics.get("ni_max",  [None]*9)[i]
                p_peak  = metrics.get("p_max",   [None]*9)[i]
                np_peak = metrics.get("n_pmax",  [None]*9)[i]
                writer.writerow([temp, volt, v_peak, nv_peak, i_peak, ni_peak, p_peak, np_peak])

print("✅ CSV files generated, including special handling for Q1 (BJT) and X (U2 subcircuit).")

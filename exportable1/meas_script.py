# import time
# from PyLTSpice import SimRunner
# from pathlib import Path
# from spicelib.editor.asc_editor import AscEditor

# from pathlib import Path
# from PyLTSpice import RawRead
# import numpy as np
# import csv
# from openpyxl import Workbook
# start = time.time()


# def is_component_line(line):
#     skip_keywords = ['.model', '.lib', '.tran', '.TEMP', '.end', '.backanno']
#     if not line or line.startswith(('*', ';')):
#         return False
#     return not any(line.lower().startswith(k.lower()) for k in skip_keywords)

# # To identify the nodes between the devices

# def parse_netlist(filepath):
#     netlist_path = Path(filepath)
#     components = {}

#     with netlist_path.open() as f:
#         for line in f:
#             line = line.strip()
#             if not is_component_line(line):
#                 continue

#             tokens = line.split()
#             if not tokens:
#                 continue

#             comp_name = tokens[0]
#             nodes = [t for t in tokens[1:] if t.upper().startswith("N") or t == '0']
            
#             components[comp_name] = tuple(nodes)

#     return components

# pf = input("enter the project folder path, include all the .lib files and .asy and schematics into this folder:")
# # Set your schematic folder as the custom library path for .asy and .lib files
# project_folder = r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata"

# AscEditor.set_custom_library_paths(
#     project_folder,  # for .lib files (subcircuits)
#     project_folder   # for .asy files (symbols)
# )

# # Paths
# asc_file_path = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata\FPL_center.asc")
# netfile_path = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata\FPL_center_netlist.txt")
# out_path = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata")

# # Load the schematic netlist
# netlist = AscEditor(str(asc_file_path))



# comp_dict = parse_netlist(netfile_path)




# meas_cmds = []
# for comp in comp_dict:
    
#     # two terminal devices
#     if comp[0] not in ['Q','X']:
#         meas_cmds.append(f".meas TRAN I_max_{comp} MAX I({comp}) FROM=0 TO=10m")
#         meas_cmds.append(f".meas TRAN nI_max_{comp} MAX -I({comp}) FROM=0 TO=10m")
#         v_plus,v_minus = comp_dict[comp][:2]
#         print(v_plus,v_minus)

#         if v_minus == '0':
#             meas_cmds.append(f".meas TRAN V_max_{comp} MAX V({v_plus}) FROM=0 TO=10m")
#             meas_cmds.append(f".meas TRAN nV_max_{comp} MAX -V({v_plus}) FROM=0 TO=10m")
#             meas_cmds.append(f".meas TRAN p_max_{comp} MAX V({v_plus})*I({comp}) FROM=0 TO=10m")
#             meas_cmds.append(f".meas TRAN np_max_{comp} MAX -V({v_plus})*I({comp}) FROM=0 TO=10m")
#         elif v_plus == '0':
#             meas_cmds.append(f".meas TRAN V_max_{comp} MAX V({v_minus}) FROM=0 TO=10m")
#             meas_cmds.append(f".meas TRAN nV_max_{comp} MAX -V({v_minus}) FROM=0 TO=10m")
#             meas_cmds.append(f".meas TRAN p_max_{comp} MAX V({v_minus})*I({comp}) FROM=0 TO=10m")
#             meas_cmds.append(f".meas TRAN np_max_{comp} MAX -V({v_minus})*I({comp}) FROM=0 TO=10m")
#         else:
#             meas_cmds.append(f".meas TRAN V_max_{comp} MAX V({v_plus},{v_minus}) FROM=0 TO=10m")
#             meas_cmds.append(f".meas TRAN nV_max_{comp} MAX -V({v_plus},{v_minus}) FROM=0 TO=10m")
#             meas_cmds.append(f".meas TRAN p_max_{comp} MAX V({v_plus},{v_minus})*I({comp}) FROM=0 TO=10m")
#             meas_cmds.append(f".meas TRAN np_max_{comp} MAX -V({v_plus},{v_minus})*I({comp}) FROM=0 TO=10m")
    
#     if comp[0] == 'Q':
#         meas_cmds.append(f".meas TRAN Ic_max_Q1 MAX Ic(Q1)")
#         meas_cmds.append(f".meas TRAN Ib_max_Q1 MAX Ib(Q1)")
#         meas_cmds.append(f".meas TRAN Ie_max_Q1 MAX Ie(Q1)")
#         meas_cmds.append(f'.meas TRAN Vce_max_Q1 MAX V(N005)')
#         meas_cmds.append(f'.meas TRAN Vbe_max_Q1 MAX V(N005,N006)')
#         meas_cmds.append(f".meas TRAN P_max_Q1 MAX (V(N005)*Ic(Q1))")
#     if comp == 'XÂ§U2':
#         meas_cmds.append(f".meas TRAN id_max_X MAX Ix(U2:1)")
#         meas_cmds.append(f".meas TRAN nid_max_X  MAX -Ix(U2:1)")
#         meas_cmds.append(f".meas TRAN ig_max_X  MAX Ix(U2:2)")
#         meas_cmds.append(f".meas TRAN nig_max_X  MAX -Ix(U2:2)")
#         meas_cmds.append(f".meas TRAN is_max_X  MAX Ix(U2:3)")
#         meas_cmds.append(f".meas TRAN nis_max_X  MAX -Ix(U2:3)")
#         meas_cmds.append(f'.meas TRAN vdss_max_X MAX V(N004,N006)')
#         meas_cmds.append(f'.meas TRAN vgss_max_X MAX V(N005,N006)')

#         meas_cmds.append(f".meas TRAN P_max_X MAX ((V(N004)*Ix(U2:1)) + (V(N005)*Ix(U2:2)) +(V(N006)*Ix(U2:3)))")
        
#     else:
#         continue
       
    

# netlist.set_component_value("V2", "{V2}")

# # Add simulation directives
# netlist.add_instructions(
#     "; Simulation settings",
#     ".tran 10u 10m 0 10u",
#     ".step param V2 list 9 12 16",  # ✅ correct

#     ".step temp list -10 25 45 85",
#     *meas_cmds
# )

# # Output directory
# output_folder = out_path / "batch_run"
# output_folder.mkdir(parents=True, exist_ok=True)

# # Run the simulation
# sim = SimRunner(output_folder=str(output_folder), simulator=None)
# ksim = sim.run(netlist)
# print("\u2705 Batch simulation completed")

# end = time.time()
# print(f"\u2705 Execution time: {end - start:.3f} seconds")

# ------------------------------------------------------------------------------------------------------------------------

import time
from PyLTSpice import SimRunner
from pathlib import Path
from spicelib.editor.asc_editor import AscEditor

from PyLTSpice import RawRead
import numpy as np
import csv
from openpyxl import Workbook
import os

start = time.time()

def is_component_line(line):
    skip_keywords = ['.model', '.lib', '.tran', '.TEMP', '.end', '.backanno']
    if not line or line.startswith(('*', ';')):
        return False
    return not any(line.lower().startswith(k.lower()) for k in skip_keywords)

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

# --- User Inputs ---
pf = input("Enter the project folder path (include all .lib, .asy and schematic files): ")
project_folder = Path(pf.strip('"').strip()).resolve()

# Ask for special node names
Q_collector = input("Enter the collector node for Q1: ")
Q_base = input("Enter the base node for Q1: ")
Q_emitter = input("Enter the emitter node for Q1: ")

X_drain = input("Enter the drain node for U2: ")
X_gate = input("Enter the gate node for U2: ")
X_source = input("Enter the source node for U2: ")

# Set custom library paths
AscEditor.set_custom_library_paths(project_folder, project_folder)

# Paths
asc_file_path = Path(project_folder) / "FPL_center.asc"
netfile_path = Path(project_folder) / "FPL_center_netlist.txt"
out_path = Path(project_folder)

# Load schematic and netlist
netlist = AscEditor((asc_file_path))
comp_dict = parse_netlist(netfile_path)

meas_cmds = []
for comp in comp_dict:
    if comp[0] not in ['Q', 'X']:
        meas_cmds.append(f".meas TRAN I_max_{comp} MAX I({comp}) FROM=0 TO=10m")
        meas_cmds.append(f".meas TRAN nI_max_{comp} MAX -I({comp}) FROM=0 TO=10m")
        v_plus, v_minus = comp_dict[comp][:2]
        print(v_plus, v_minus)

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
        meas_cmds.append(f".meas TRAN Ic_max_{comp} MAX Ic({comp})")
        meas_cmds.append(f".meas TRAN Ib_max_{comp} MAX Ib({comp})")
        meas_cmds.append(f".meas TRAN Ie_max_{comp} MAX Ie({comp})")
        if Q_emitter == "0":
            meas_cmds.append(f".meas TRAN Vce_max_{comp} MAX V({Q_collector})")
            meas_cmds.append(f".meas TRAN Vbe_max_{comp} MAX V({Q_base})")

        else:
            meas_cmds.append(f".meas TRAN Vce_max_{comp} MAX V({Q_collector},{Q_emitter})")
            meas_cmds.append(f".meas TRAN Vbe_max_{comp} MAX V({Q_base},{Q_emitter})")

        meas_cmds.append(f".meas TRAN P_max_{comp} MAX (V({Q_collector})*Ic(Q1))")

    if comp[0] == 'X':
        meas_cmds.append(f".meas TRAN id_max_X MAX Ix(U2:1)")
        meas_cmds.append(f".meas TRAN nid_max_X  MAX -Ix(U2:1)")
        meas_cmds.append(f".meas TRAN ig_max_X  MAX Ix(U2:2)")
        meas_cmds.append(f".meas TRAN nig_max_X  MAX -Ix(U2:2)")
        meas_cmds.append(f".meas TRAN is_max_X  MAX Ix(U2:3)")
        meas_cmds.append(f".meas TRAN nis_max_X  MAX -Ix(U2:3)")
        meas_cmds.append(f".meas TRAN vdss_max_X MAX V({X_drain},{X_source})")
        meas_cmds.append(f".meas TRAN vgss_max_X MAX V({X_gate},{X_source})")
        meas_cmds.append(f".meas TRAN P_max_X MAX ((V({X_drain})*Ix(U2:1)) + (V({X_gate})*Ix(U2:2)) + (V({X_source})*Ix(U2:3)))")

netlist.set_component_value("V2", "{V2}")
print('ran this')


# Add simulation directives
netlist.add_instructions(
    "; Simulation settings",
    ".tran 10u 10m 0 10u",
    ".step param V2 list 9 12 16",
    ".step temp list -10 25 45 85",
    *meas_cmds
)
print('ran this')
# Output directory
output_folder = out_path / "batchf_run"
output_folder.mkdir(parents=True, exist_ok=True)

# Run simulation
sim = SimRunner(output_folder=str(output_folder), simulator=None)
ksim = sim.run(netlist)
print("\u2705 Batch simulation completed")

end = time.time()
print(f"\u2705 Execution time: {end - start:.3f} seconds")

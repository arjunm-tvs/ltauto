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
    
    # two terminal devices
    # if comp[0] not in ['Q','X']:
    #     meas_cmds.append(f".meas TRAN I_max_{comp} MAX I({comp}) FROM=0 TO=10m")
    #     meas_cmds.append(f".meas TRAN nI_max_{comp} MAX -I({comp}) FROM=0 TO=10m")
    #     v_plus,v_minus = comp_dict[comp][:2]
    #     print(v_plus,v_minus)

    #     if v_minus == '0':
    #         meas_cmds.append(f".meas TRAN V_max_{comp} MAX V({v_plus}) FROM=0 TO=10m")
    #         meas_cmds.append(f".meas TRAN nV_max_{comp} MAX -V({v_plus}) FROM=0 TO=10m")
    #         meas_cmds.append(f".meas TRAN p_max_{comp} MAX V({v_plus})*I({comp}) FROM=0 TO=10m")
    #         meas_cmds.append(f".meas TRAN np_max_{comp} MAX -V({v_plus})*I({comp}) FROM=0 TO=10m")
    #     elif v_plus == '0':
    #         meas_cmds.append(f".meas TRAN V_max_{comp} MAX V({v_minus}) FROM=0 TO=10m")
    #         meas_cmds.append(f".meas TRAN nV_max_{comp} MAX -V({v_minus}) FROM=0 TO=10m")
    #         meas_cmds.append(f".meas TRAN p_max_{comp} MAX V({v_minus})*I({comp}) FROM=0 TO=10m")
    #         meas_cmds.append(f".meas TRAN np_max_{comp} MAX -V({v_minus})*I({comp}) FROM=0 TO=10m")
    #     else:
    #         meas_cmds.append(f".meas TRAN V_max_{comp} MAX V({v_plus},{v_minus}) FROM=0 TO=10m")
    #         meas_cmds.append(f".meas TRAN nV_max_{comp} MAX -V({v_plus},{v_minus}) FROM=0 TO=10m")
    #         meas_cmds.append(f".meas TRAN p_max_{comp} MAX V({v_plus},{v_minus})*I({comp}) FROM=0 TO=10m")
    #         meas_cmds.append(f".meas TRAN np_max_{comp} MAX -V({v_plus},{v_minus})*I({comp}) FROM=0 TO=10m")
    
    if comp[0] == 'Q':
        meas_cmds.append(f".meas TRAN Ic_max_Q1 MAX Ic(Q1)")
        meas_cmds.append(f".meas TRAN Ib_max_Q1 MAX Ib(Q1)")
        meas_cmds.append(f".meas TRAN Ie_max_Q1 MAX Ie(Q1)")
        meas_cmds.append(f'.meas TRAN Vce_max_Q1 MAX V(N005)')
        meas_cmds.append(f'.meas TRAN Vbe_max_Q1 MAX V(N005,N006)')
        meas_cmds.append(f".meas TRAN P_max_Q1 MAX (V(N005)*Ic(Q1))")
    if comp == 'XÂ§U2':
        meas_cmds.append(f".meas TRAN id_max_X MAX Ix(U2:1)")
        meas_cmds.append(f".meas TRAN nid_max_X  MAX -Ix(U2:1)")
        meas_cmds.append(f".meas TRAN ig_max_X  MAX Ix(U2:2)")
        meas_cmds.append(f".meas TRAN nig_max_X  MAX -Ix(U2:2)")
        meas_cmds.append(f".meas TRAN is_max_X  MAX Ix(U2:3)")
        meas_cmds.append(f".meas TRAN nis_max_X  MAX -Ix(U2:3)")
        meas_cmds.append(f'.meas TRAN vdss_max_X MAX V(N004,N006)')
        meas_cmds.append(f'.meas TRAN vgss_max_X MAX V(N005,N006)')

        meas_cmds.append(f".meas TRAN P_max_X MAX ((V(N004)*Ix(U2:1)) + (V(N005)*Ix(U2:2)) +(V(N006)*Ix(U2:3)))")
        
    else:
        continue
       
    

netlist.set_component_value("V2", "{V2}")

# Add simulation directives
netlist.add_instructions(
    "; Simulation settings",
    ".tran 10u 10m 0 10u",
    ".step param V2 list 9 12 14 160",  # ✅ correct

    ".step temp list -10 25 45 85",
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

# ------------------------------------------------------------------------------------------------------------------------
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

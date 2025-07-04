

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
    multi_node_components = []

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

            if len(set(nodes)) > 2:
                multi_node_components.append((comp_name, nodes))

    return components,multi_node_components

# --- User Inputs ---
pf = input("Enter the project folder path (include all .lib, .asy and schematic files): ")
project_folder = Path(pf.strip('"').strip()).resolve()



# Set custom library paths
AscEditor.set_custom_library_paths(project_folder, project_folder)

# Paths
asc_file_path = Path(project_folder) / "FPL_center.asc"
netfile_path = Path(project_folder) / "FPL_center_netlist.txt"
out_path = Path(project_folder)

# Load schematic and netlist
netlist = AscEditor((asc_file_path))

comp_dict, multi_nodal_comp = parse_netlist(netfile_path)
print('='*60)

print("The automation won't work reliably for these components (more than 2 connected nodes):")
for comp, nodes in multi_nodal_comp:
    print(f"  - {comp}: connected to nodes {nodes}")

print('='*60)

multi_nodal_names = {name for name, _ in multi_nodal_comp}


# Ask for special node names
Q_collector = input("Enter the collector node for Q1: ")
Q_base = input("Enter the base node for Q1: ")
Q_emitter = input("Enter the emitter node for Q1: ")

X_drain = input("Enter the drain node for U2: ")
X_gate = input("Enter the gate node for U2: ")
X_source = input("Enter the source node for U2: ")

meas_cmds = []



for comp in comp_dict:
    if comp not in multi_nodal_names:
        meas_cmds.append(f".meas TRAN I_max_{comp} MAX I({comp}) FROM=0 TO=10m")
        meas_cmds.append(f".meas TRAN nI_max_{comp} MAX -I({comp}) FROM=0 TO=10m")
        v_plus, v_minus = comp_dict[comp][:2]
        # print(v_plus, v_minus)

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

temps = input("enter the temperature steps seperated by spaces(enter more than one value):").strip()
print(temps)
volts = input("enter the voltage steps seperated by spaces(enter more than one value):").strip()
print(volts)

# Add simulation directives
netlist.add_instructions(
    "; Simulation settings",
    ".tran 10u 10m 0 10u",
    f".step param V2 list {volts}",
    f".step temp list {temps}",
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

import json
script_dir = Path(__file__).parent.resolve()
# Save temperature and voltage steps to config.json
config_path = script_dir / "config.json"
config_data = {
    "project_folder": str(project_folder),
    "temperatures": list(map(int, temps.strip().split())),
    "voltages": list(map(int, volts.strip().split()))
}

with open(config_path, "w") as f:
    json.dump(config_data, f, indent=2)

print(f"✅ Configuration saved to {config_path}")

end = time.time()
print(f"\u2705 Execution time: {end - start:.3f} seconds")

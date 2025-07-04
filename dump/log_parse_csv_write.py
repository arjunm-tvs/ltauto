

import re
import csv
from collections import defaultdict
from pathlib import Path

# === Replace this with your actual LTspice log file path ===
log_file_path = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata\batch_run\FPL_center_1.log")

# Define step condition map (index starts from 1 in LTspice)

# step_conditions = [
#     (-10, 9), (-10, 12), (-10, 16),
#     (25, 9),  (25, 12),  (25, 16),
#     (85, 9),  (85, 12),  (85, 16),
# ]

temperatures = [-10, 25,45,85]
voltages = [9, 12,14, 160]

# Generate combinations using nested loops
step_conditions = [(temp, volt) for temp in temperatures for volt in voltages]

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
output_folder = script_dir / "trial_run"
output_folder.mkdir(parents=True, exist_ok=True)
i = 0
for component, metrics in component_data.items():
    
    i +=1 
    print(component,end = "||")
    if i%10 == 9:
        print('\n')
for component, metrics in component_data.items():
    filename = output_folder / f"{component}.csv"
    
    # print(component)

    # Special case: Q1 (BJT)
    if component == "Q1":
        with open(filename, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Temperature ",
                "Voltage Level (V)",
                "Peak collector emitter voltage (V)",
                "peak base emitter voltage",
                "peak Collector current (A)",
                "peak Base current (A)",
                "peak emitter current (A)",
                "peak Power"
            ])
            for i in range(len(step_conditions)):
                temp, volt = step_conditions[i]
                vce  = metrics.get('vce_max', [None]*9)[i]
                vbe = metrics.get('vbe_max', [None]*9)[i]
                ic = metrics.get("ic_max", [None]*9)[i]
                
                ib = metrics.get("ib_max", [None]*9)[i]
                ie = metrics.get("ie_max", [None]*9)[i]
                
                p   = metrics.get("p_max",  [None]*9)[i]
                writer.writerow([temp, volt, vce,vbe, ic, ib, ie, p])
                
                # print(temp, volt, vce,vbe, ic, ib, ie, p)

    # Special case: X (U2 subcircuit)
    if component[0] == "X":
        filename = output_folder / f"{component[0]}.csv"

        with open(filename, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Temperature ", "Voltage Level (V)",
                'peak dss voltage',
                'peak gss voltage',
                "peak drain current (A)", 
                "peak gate current (A)", 
                "peak source current (A)", 
                "peak Power"
            ])
            for i in range(len(step_conditions)):
                temp, volt = step_conditions[i]
                Vdss = metrics.get('vdss_max', [None]*9)[i]
                Vgss = metrics.get('vgss_max', [None]*9)[i]
                id_  = metrics.get("id_max",    [None]*9)[i]
                # nid  = metrics.get("nid_max",    [None]*9)[i]
                ig   = metrics.get("ig_max",    [None]*9)[i]
                # nig  = metrics.get("nig_max",   [None]*9)[i]
                is_  = metrics.get("is_max",    [None]*9)[i]
                # nis  = metrics.get("nis_max",   [None]*9)[i]
                p    = metrics.get("p_max",     [None]*9)[i]
                writer.writerow([temp, volt,Vdss,Vgss, id_, ig, is_, p])

    # # Default case: all other components
    # elif component not in ['X','Q1']:
    #     with open(filename, mode='w', newline='') as f:
    #         writer = csv.writer(f)
    #         writer.writerow([
    #             "Temperature ",
    #             "Voltage Level (V)",
    #             "Peak Voltage (V)",
    #             "peak reverse Voltage (V)",
    #             "Peak forward Current (A)",
    #             "peak reverse Current (A)",
    #             "Peak Power (W)",
    #             "peak negative Power (W)"
    #         ])
    #         for i in range(len(step_conditions)):
    #             temp, volt = step_conditions[i]
    #             v_peak  = metrics.get("v_max",   [None]*9)[i]
    #             nv_peak = metrics.get("nv_max",  [None]*9)[i]
    #             i_peak  = metrics.get("i_max",   [None]*9)[i]
    #             ni_peak = metrics.get("ni_max",  [None]*9)[i]
    #             p_peak  = metrics.get("p_max",   [None]*9)[i]
    #             np_peak = metrics.get("np_max",  [None]*9)[i]
    #             writer.writerow([temp, volt, v_peak, nv_peak, i_peak, ni_peak, p_peak, np_peak])

print("✅ CSV files generated, including special handling for Q1 (BJT) and X (U2 subcircuit).")

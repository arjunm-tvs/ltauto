'''USES NETLIST PARSER AND USES RAW FILE TIME WAVEFORM'''



from pathlib import Path
from PyLTSpice import RawRead
import numpy as np
import csv

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

            if len(nodes) == 1:
                nodes.append("0")

            components[comp_name] = tuple(nodes)

    return components

def analyze_power(raw_file, component_nodes):
    raw = RawRead(raw_file)
    results = {}
    time = raw.get_trace('time').get_wave()

    trace_names = raw.get_trace_names()
    # print(trace_names)
    time = raw.get_trace('time').get_wave()
    

    for comp, nodes in component_nodes.items():
        print(comp)
        if len(nodes) != 2:
            continue

        n_plus, n_minus = nodes
        
        # print(n_plus,n_minus)

        v_plus_trace = f"V({n_plus.lower()})"
        v_minus_trace = f"V({n_minus.lower()})"
        
        # print(v_plus_trace,v_minus_trace)

        v_plus = raw.get_trace(v_plus_trace).get_wave() if v_plus_trace in trace_names else 0
        v_minus = raw.get_trace(v_minus_trace).get_wave() if v_minus_trace in trace_names else 0
        
        # print(v_plus,v_minus)
        
        voltage = v_plus - v_minus

        current_trace = f"I({comp})"
        current = raw.get_trace(current_trace).get_wave() 

        power = voltage * current

        results[comp] = {
            "peak_voltage": np.max(np.abs(voltage)),
            "peak_current": np.max(np.abs(current)),
            "peak_power": np.max(np.abs(power))
        }

    return results

def export_to_csv(results, output_csv_path):
    with open(output_csv_path, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Component', 'Peak Voltage (V)', 'Peak Current (A)', 'Peak Power (W)'])

        for comp, data in results.items():
            writer.writerow([
                comp,
                f"{data['peak_voltage']:.6f}",
                f"{data['peak_current']:.6f}",
                f"{data['peak_power']:.6f}"
            ])

# --- File Paths ---
netlist_path = r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata1\FPL_CENTER_NETLIST.txt"
raw_file = r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata1\FPL_center_1.raw"
csv_output = r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata1\exported\peak_analysis_output.csv"

# --- Run Analysis ---
components = parse_netlist(netlist_path)
peak_results = analyze_power(raw_file, components)
export_to_csv(peak_results, csv_output)

# --- Done ---
print(f"✅  Peak analysis exported to:\n{csv_output}")

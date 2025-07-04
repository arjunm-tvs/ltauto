from pathlib import Path
from PyLTSpice import RawRead
import numpy as np
import csv
from openpyxl import Workbook





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

            if len(nodes) == 1:
                nodes.append("0")

            components[comp_name] = tuple(nodes)

    return components

c = parse_netlist(Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata1\TEMP_-10\Voltage_level_9\FPL_center_1_1.net"))
for k in c:
    print(k,c[k])



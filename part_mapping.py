import re
from pathlib import Path
from collections import defaultdict

def parse_netlist_components(netlist_path):
    part_map = defaultdict(list)

    # Regex patterns
    comment_line = re.compile(r"^\s*\*|^\s*;|^\s*\.")  # skip comments, directives
    component_line = re.compile(r"^(\S+)\s+(.+)")
    
    with open(netlist_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or comment_line.match(line):
                continue

            match = component_line.match(line)
            if not match:
                continue

            comp_name = match.group(1)
            tokens = line.split()

            # Skip voltage/current sources and simulation directives
            if comp_name.upper().startswith(('V', 'I', '.')):
                continue

            # Extract last token as part number (assuming it's the model name or subckt)
            part_number = tokens[-1]
            part_map[part_number].append(comp_name)

    return part_map


# === Example usage ===
if __name__ == "__main__":
    netlist_file = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata\FPL_center_netlist.txt")
    part_to_components = parse_netlist_components(netlist_file)

    for part, comps in part_to_components.items():
        print(f"{part}: {comps}")

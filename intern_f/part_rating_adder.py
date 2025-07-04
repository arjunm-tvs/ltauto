import re
from pathlib import Path
from collections import defaultdict
import pandas as pd
import numpy as np

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

# pf = input("Enter the project folder path (include all .lib, .asy and schematic files): ")
# project_folder = Path(pf.strip('"').strip()).resolve()
# === Example usage ===
if __name__ == "__main__":
    import json
    from pathlib import Path

    # 👇 Path to config.json (in same folder as this script)
    config_path = Path(__file__).parent / "config.json"

    # 📥 Load config
    with open(config_path, "r") as f:
        config = json.load(f)

# 🔄 Get all values from config
    project_folder = Path(config["project_folder"])
    
    
    netlist_file = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata\FPL_center_netlist.txt")
    netlist_file = project_folder / 'FPL_center_netlist.txt'
    
    part_to_components = parse_netlist_components(netlist_file)

    xlsx_dir = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata\datasheets")
    xlsx_dir = project_folder / 'datasheets'
    csv_dir = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata\batchf_run\csv_files")
    csv_dir = project_folder / 'batchf_run'
    csv_dir = csv_dir / 'csv_files'

    # for part, comps in part_to_components.items():
    #     print(f"{part}: {comps}")
    #     if f'{part}.xlsx'  in Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata\datasheets"):
    #         for comp in comps:
    #             open  Path(f"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata\final_run\{comp}.csv") :
    #             and compare the columsn in the .csv and .xlsx using re, where they have same key words like power current and voltage
            
    for part, comps in part_to_components.items():
        print(part,comps)
        xlsx_file = xlsx_dir / f"{part}.xlsx"
        
        if not xlsx_file.exists():
            print(f"Missing Excel: {xlsx_file}")
            continue

        try:
            xlsx_df = pd.read_excel(xlsx_file)
        except Exception as e:
            print(f"Error reading Excel {xlsx_file}: {e}")
            continue

        for comp in comps:
            csv_file = csv_dir / f"{comp}.csv"

            if comp[0] == 'X':
                csv_file = csv_dir / f"{comp[0]}.csv"

            if not csv_file.exists():
                print(f"  Missing CSV: {csv_file}")
                continue

            try:
                csv_df = pd.read_csv(csv_file, encoding='cp1252')
            except Exception as e:
                print(f"  Error reading CSV {csv_file}: {e}")
                continue

            num_rows = len(csv_df)
            excel_rows = len(xlsx_df)

            # Log info
            if excel_rows == 0:
                print(f"  ⚠ Excel file {xlsx_file.name} has no rows, skipping.")
                continue

            # Repeat Excel data to match number of rows in CSV
            repeat_times = -(-num_rows // excel_rows)  # Ceiling division without importing math
            repeated_excel_df = pd.concat([xlsx_df] * repeat_times, ignore_index=True).iloc[:num_rows]

            # ✅ Ensure both DataFrames have default RangeIndex
            csv_df = csv_df.reset_index(drop=True)
            repeated_excel_df = repeated_excel_df.reset_index(drop=True)

            # Concatenate side-by-side
            try:
                combined_df = pd.concat([csv_df, repeated_excel_df], axis=1)
                combined_df.to_csv(csv_file, index=False)
                print(f"  ✓ Appended Excel data to {csv_file.name} ({num_rows} rows)")
            except Exception as e:
                print(f"  ❌ Error combining data for {csv_file.name}: {e}")

    
import csv
from pathlib import Path
from collections import defaultdict
from openpyxl import Workbook

# --- Constants ---
netlist_path_general = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata1")
temps = [-10, 25, 85]
voltage_levels = [9, 12, 16]

# --- Accumulate data per component ---
component_data = defaultdict(list)  # { 'R1': [ {temp, vlevel, peakV, peakI, peakP}, ... ] }

# --- Read all CSVs ---
for temp in temps:
    netlist_temp_general = netlist_path_general / f'TEMP_{temp}'

    for voltage_level in voltage_levels:
        csv_file = netlist_temp_general / f'Peak_values_voltage_level_{voltage_level}_csv.csv'

        if not csv_file.exists():
            print(f"❌ Missing file: {csv_file}")
            continue

        with open(csv_file, 'r', newline='') as file:
            reader = csv.reader(file)
            rows = list(reader)

        # Find where the actual header starts
        header_index = None
        for i, row in enumerate(rows):
            if row == ['Component', 'Peak Voltage (V)', 'Peak Current (A)', 'Peak Power (W)']:
                header_index = i
                break

        if header_index is None:
            print(f"⚠️ Skipping malformed file: {csv_file}")
            continue

        # Read component data until "Peak Node Voltages"
        for row in rows[header_index + 1:]:
            if not row or "Peak Node Voltages" in row[0]:
                break
            try:
                comp = row[0]
                peak_v = float(row[1])
                peak_i = float(row[2])
                peak_p = float(row[3])
                component_data[comp].append({
                    'Temperature': temp,
                    'Voltage Level': voltage_level,
                    'Peak Voltage (V)': peak_v,
                    'Peak Current (A)': peak_i,
                    'Peak Power (W)': peak_p,
                })
            except Exception as e:
                print(f"⚠️ Error parsing row {row} in {csv_file}: {e}")

# --- Write to Excel: one file per component ---
output_dir = netlist_path_general / "Component_Excel_Files"
output_dir.mkdir(parents=True, exist_ok=True)

for comp, records in component_data.items():
    wb = Workbook()
    ws = wb.active
    ws.title = "Component Data"

    # Header
    ws.append(['Temperature (°C)', 'Voltage Level (V)', 'Peak Voltage (V)', 'Peak Current (A)', 'Peak Power (W)'])

    # Data rows
    for entry in sorted(records, key=lambda x: (x['Temperature'], x['Voltage Level'])):
        ws.append([
            entry['Temperature'],
            entry['Voltage Level'],
            round(entry['Peak Voltage (V)'], 6),
            round(entry['Peak Current (A)'], 6),
            round(entry['Peak Power (W)'], 6),
        ])

    # Save Excel
    excel_path = output_dir / f"{comp}_analysis.xlsx"
    wb.save(excel_path)
    print(f"✅ Saved: {excel_path}")

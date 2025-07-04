import pandas as pd
from pathlib import Path
import numpy as np

# Your part-component mapping


# Base paths
xlsx_dir = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata\datasheets")
csv_dir = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata\final_run")

for part, comps in part_to_components.items():
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

        # Repeat Excel data enough times to match CSV rows
        repeat_times = (num_rows + excel_rows - 1) // excel_rows  # Ceiling division
        repeated_excel_df = pd.concat([xlsx_df] * repeat_times, ignore_index=True).iloc[:num_rows]

        # Combine and save
        combined_df = pd.concat([csv_df, repeated_excel_df.reset_index(drop=True)], axis=1)
        combined_df.to_csv(csv_file, index=False)
        print(f"  ✓ Appended repeated Excel data to {csv_file.name} ({num_rows} rows)")

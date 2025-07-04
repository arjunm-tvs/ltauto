

#--------------------------------------------------------------------------------------------------

import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import ttk

def show_results_gui(title, all_logs, all_failures_df):
    root = tk.Tk()
    root.title(title)
    root.geometry("1200x600")

    # Logs panel
    log_frame = tk.Frame(root)
    log_frame.pack(fill="x", padx=10, pady=(10, 0))

    text_widget = tk.Text(log_frame, height=15)
    text_widget.pack(fill="x")

    for line in all_logs:
        text_widget.insert(tk.END, line + "\n")
    text_widget.config(state="disabled")

    # Failures panel
    if not all_failures_df.empty:
        tree = ttk.Treeview(root)
        tree["columns"] = list(all_failures_df.columns)
        tree["show"] = "headings"

        for col in all_failures_df.columns:
            tree.heading(col, text=col)
            if col == "Condition":
                tree.column(col, width=350, anchor="w")  # wider and left-aligned
            else:
                tree.column(col, width=150, anchor="center")


        for _, row in all_failures_df.iterrows():
            tree.insert("", "end", values=list(row))

        vsb = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        vsb.pack(side="right", fill="y")

    root.mainloop()


def check_peak_vs_max(csv_file_path, all_logs, all_failures):
    csv_file = Path(csv_file_path)
    logs = [f"\n📄 Processing: {csv_file.name}"]

    try:
        df = pd.read_csv(csv_file)
        failures = []

        check_columns = df.columns[2:]
        peak_cols = [col for col in check_columns if 'peak' in col.lower()]
        max_cols = [col for col in check_columns if 'maximum' in col.lower()]

        def normalize(col_name):
            return col_name.lower().replace('peak', '').replace('maximum', '').replace('(a)', '').replace('(v)', '').replace('(w)', '').strip()

        match_map = {}
        for pcol in peak_cols:
            pnorm = normalize(pcol)
            for mcol in max_cols:
                if normalize(mcol) == pnorm:
                    match_map[pcol] = mcol
                    break

        if match_map:
            logs.append("🔍 Matched column pairs:")
            for p, m in match_map.items():
                logs.append(f"   {p} ⇨ {m}")
        else:
            logs.append("ℹ No peak–maximum pairs matched.")

        for i, row in df.iterrows():
            for pcol, mcol in match_map.items():
                try:
                    peak_val = row[pcol]
                    max_val = row[mcol]
                    if pd.notnull(peak_val) and pd.notnull(max_val) and float(peak_val) > float(max_val):
                        failures.append({
                            'File': csv_file.name,
                            'Row': i,
                            'Voltage Level (V)': row['Voltage Level (V)'],
                            'Temperature': row['Temperature '],
                            'Condition': f"{pcol} > {mcol}",
                            'Peak': peak_val,
                            'Max': max_val
                        })
                except ValueError:
                    continue

        if failures:
            logs.append(f"⚠ Failures Detected: {len(failures)} issue(s) found.")
            all_failures.extend(failures)
        else:
            logs.append("✅ All rows pass the maximum ratings check.")

    except Exception as e:
        logs.append(f"❌ Failed to process {csv_file.name}: {e}")

    all_logs.extend(logs)

def export_logs_to_text_and_csv(log_lines, output_dir, base_filename="log_export"):
    """
    Save logs to both .txt and .csv format
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    txt_path = output_dir / f"{base_filename}.txt"
    # csv_path = output_dir / f"{base_filename}.csv"

    try:
        # Write to .txt
        with open(txt_path, "w", encoding="utf-8") as f:
            for line in log_lines:
                f.write(line + "\n")

        # Write to .csv
        # df = pd.DataFrame({'Log': log_lines})
        # df.to_csv(csv_path, index=False)

        print(f"✅ Logs exported to:\n- {txt_path}")
    except Exception as e:
        print(f"❌ Failed to export logs: {e}")


def export_failures_to_csv(failure_df, output_dir, base_filename="failures_export"):
    """
    Save failure table to a CSV file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / f"{base_filename}.csv"

    try:
        if not failure_df.empty:
            failure_df.to_csv(csv_path, index=False)
            print(f"⚠ Failures exported to: {csv_path}")
        else:
            print("✅ No failures to export.")
    except Exception as e:
        print(f"❌ Failed to export failure table: {e}")



# === Process all files ===

import json


project_folder = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata\batchf_run")  # or make it relative
config_path = Path(__file__).parent / "config.json"

# 📥 Load config
with open(config_path, "r") as f:
    config = json.load(f)

# 🔄 Get all values from config
project_folder = Path(config["project_folder"])

folder = Path(r'D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata\batchf_run\csv_files')
folder = project_folder / 'batchf_run'
folder = folder / 'csv_files'
all_logs = []
all_failures = []

# Get relevant files
all_cleaned = list(folder.glob("*_cleaned.csv"))
filtered_files = [f for f in all_cleaned if not f.name.endswith("_cleaned_cleaned.csv")]
print(filtered_files)
for csv_file in filtered_files:
    check_peak_vs_max(csv_file, all_logs, all_failures)

# Show single GUI popup with everything
fail_df = pd.DataFrame(all_failures)
show_results_gui("Simulation Limit Check Report", all_logs, fail_df)


output_folder = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata\batchf_run\exports")
output_folder = project_folder / 'batchf_run'
output_folder = output_folder / 'exports'

output_folder.mkdir(parents=True, exist_ok=True)

export_logs_to_text_and_csv(all_logs, output_folder)
export_failures_to_csv(fail_df, output_folder)
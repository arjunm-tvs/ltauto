# import pandas as pd
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_pdf import PdfPages
# from pathlib import Path

# # --- Folder containing all Excel files ---
# excel_folder = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata1\Component_Excel_Files")
# output_folder = excel_folder / "Combined_PDFs"
# output_folder.mkdir(exist_ok=True)

# # --- Metrics to Plot ---
# metrics = {
#     "Peak Voltage (V)": "Peak Voltage",
#     "Peak Current (A)": "Peak Current",
#     "Peak Power (W)": "Peak Power"
# }

# # --- Batch process all Excel files ---
# for excel_file in excel_folder.glob("*_analysis.xlsx"):
#     component_name = excel_file.stem.replace("_analysis", "")
#     df = pd.read_excel(excel_file)
#     df.columns = [col.strip() for col in df.columns]  # Clean headers

#     pdf_path = output_folder / f"{component_name}_plots.pdf"
#     with PdfPages(pdf_path) as pdf:
#         for metric, title in metrics.items():
#             plt.figure(figsize=(8, 5))
#             for temp in sorted(df["Temperature (°C)"].unique()):
#                 subset = df[df["Temperature (°C)"] == temp]
#                 plt.plot(
#                     subset["Voltage Level (V)"],
#                     subset[metric],
#                     marker='o',
#                     label=f"{temp}°C"
#                 )
#             plt.title(f"{title} vs Voltage Level for {component_name}")
#             plt.xlabel("Voltage Level (V)")
#             plt.ylabel(metric)
#             plt.grid(True)
#             plt.legend()
#             plt.tight_layout()

#             # Save this figure to the PDF
#             pdf.savefig()
#             plt.close()
    
#     print(f"✅ Saved plots to: {pdf_path}")


import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from pathlib import Path

# --- Folder containing all CSV files ---
csv_folder = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\PyStart\component_csvs")
output_folder = csv_folder / "Combined_PDFs"
output_folder.mkdir(exist_ok=True)

# --- Metrics to Plot ---
metrics = {
    "Peak Voltage (V)": "Peak Voltage",
    "Peak Current (A)": "Peak Current",
    "Peak Power (W)": "Peak Power"
}

# --- Batch process all CSV files ---
for csv_file in csv_folder.glob("*.csv"):
    component_name = csv_file.stem
    df = pd.read_csv(csv_file, encoding='latin1') 
    df.columns = [col.strip() for col in df.columns]  # Clean headers

    pdf_path = output_folder / f"{component_name}_plots.pdf"
    with PdfPages(pdf_path) as pdf:
        for metric, title in metrics.items():
            plt.figure(figsize=(8, 5))
            for temp in sorted(df["Temperature (°C)"].unique()):
                subset = df[df["Temperature (°C)"] == temp]
                plt.plot(
                    subset["Voltage Level (V)"],
                    subset[metric],
                    marker='o',
                    label=f"{temp}°C"
                )
            plt.title(f"{title} vs Voltage Level for {component_name}")
            plt.xlabel("Voltage Level (V)")
            plt.ylabel(metric)
            plt.grid(True)
            plt.legend()
            plt.tight_layout()

            # Save this figure to the PDF
            pdf.savefig()
            plt.close()
    
    print(f"✅ Saved plots to: {pdf_path}")

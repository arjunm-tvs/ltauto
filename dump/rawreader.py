from PyLTSpice import RawRead
import pandas as pd
from pathlib import Path

# Define path
output_folder = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata1")
raw_file_path = output_folder / "FPL_center_1.raw"

# Load waveform data
raw_data = RawRead(str(raw_file_path))

# Get all signal names
signal_names = raw_data.get_trace_names()

# Extract each trace
data = {name: raw_data.get_trace(name).get_wave() for name in signal_names}

# Create DataFrame
df = pd.DataFrame(data)

# Insert time column if exists
if "time" in df.columns:
    df = df.set_index("time")

# Export
csv_output = output_folder / "exported\\transient_output.csv"


df.to_csv(csv_output)

print(f"✅ Exported waveform data:\nCSV: {csv_output}")


# #Set path to the .op.raw file

# op_raw_file = output_folder / "FPL_center_1.op.raw"

# # Load the raw operating point file
# raw_op = RawRead(str(op_raw_file))

# # Get signal names and corresponding scalar values
# op_data = {
#     name: raw_op.get_trace(name).data[0]
#     for name in raw_op.get_trace_names()
# }

# # Create DataFrame
# op_df = pd.DataFrame(op_data.items(), columns=["Node/Device", "Value"])

# # Export to CSV
# op_csv_path = output_folder / "op_point_values.csv"
# op_df.to_csv(op_csv_path, index=False)

# print(f"✅ OP point values exported to CSV:\n{op_csv_path}")




from PyLTSpice import RawRead
import pandas as pd
from pathlib import Path

# Path to the binary .op.raw file
output_folder = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata1")
raw_file = output_folder / "FPL_center_1.op.raw"

# Load raw file
raw_data = RawRead(str(raw_file))

# Process each signal
data = []
for name in raw_data.get_trace_names():
    value = raw_data.get_trace(name).data[0]

    # Classification based on name pattern
    if name.startswith("V("):
        type_ = "voltage"
    elif name.startswith("I("):
        type_ = "device_current"
    elif name.lower().startswith("ix(") or name.startswith("Ix(") or name.startswith("I(") and ":" in name:
        type_ = "subckt_current"
    else:
        type_ = "unknown"

    data.append((name, value, type_))

# Create DataFrame
df = pd.DataFrame(data, columns=["Node/Device", "Value", "Type"])

# Save to CSV
csv_output_path = output_folder / "exported\\op_point_values_extracted.csv"
df.to_csv(csv_output_path, index=False)

print(f"✅ OP point values extracted from binary and saved to:\n{csv_output_path}")

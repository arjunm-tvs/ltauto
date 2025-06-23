# import time
# from PyLTSpice import SimRunner
# from pathlib import Path
# from spicelib.editor.asc_editor import AscEditor


# start = time.time()


# # Set your schematic folder as the custom library path for .asy and .lib files
# project_folder = r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata1"

# AscEditor.set_custom_library_paths(
#     project_folder,  # for .lib files (subcircuits)
#     project_folder   # for .asy files (symbols)
# )

# # Paths
# asc_file_path = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata1\FPL_center_1.asc")
# output_folder = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata1\DC-Sweep")

# # Ensure output folder exists
# output_folder.mkdir(parents=True, exist_ok=True)

# # Load the schematic netlist
# netlist = AscEditor(str(asc_file_path))

# # Optional: add simulation instructions if needed
# netlist.add_instructions(
#     "; Simulation settings", # 10ms transient simulation
#     ".temp -40 100 25",
#     ".tran 10m"
# )

# # Initialize simulator (None means default LTspice)
# sim = SimRunner(output_folder=str(output_folder), simulator=None)

# # Run the simulation
# sim.run(netlist)



# # Print paths of output files
# for raw, log in sim:
#     print(f"Raw file: {raw}")
#     print(f"Log file: {log}")

# end = time.time()
# print(f"Execution time: {end - start:.3f} seconds")


import time
from PyLTSpice import SimRunner
from pathlib import Path
from spicelib.editor.asc_editor import AscEditor


start = time.time()


# Set your schematic folder as the custom library path for .asy and .lib files
project_folder = r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata1"

AscEditor.set_custom_library_paths(
    project_folder,  # for .lib files (subcircuits)
    project_folder   # for .asy files (symbols)
)

# Paths
asc_file_path = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata1\FPL_center_1.asc")
out_path = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata1")

for temp in [-10,25,85]:
    
    out_temp_path = out_path / f'TEMP_{temp}'
    
    for voltage_level in [9,12,16]:

        output_folder = out_temp_path / f"Voltage_level_{voltage_level}"

        # Ensure output folder exists
        output_folder.mkdir(parents=True, exist_ok=True)

        # Load the schematic netlist
        netlist = AscEditor(str(asc_file_path))

        netlist.set_component_value("V2", voltage_level)

        # Optional: add simulation instructions if needed
        netlist.add_instructions(
            "; Simulation settings", # 10ms transient simulation
            f".temp {temp}",
            ".tran 10m"
        )

        # Initialize simulator (None means default LTspice)
        sim = SimRunner(output_folder=str(output_folder), simulator=None)

        # Run the simulation
        ksim = sim.run(netlist)
        print(f'\u2705 done for Temp = {temp}, Voltage = {voltage_level}' )

# for raw, log in sim:
#     print(f"\n--- Log File: {log} ---\n")
    
#     with open(log, 'r') as log_file:
#         log_content = log_file.read()
#         print(log_content)


end = time.time()
print(f"\u2705 Execution time: {end - start:.3f} seconds")



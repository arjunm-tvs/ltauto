import time
from PyLTSpice import SimRunner
from pathlib import Path
from spicelib.editor.asc_editor import AscEditor

start = time.time()

project_folder = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\FPL_CENTER")
asc_file_path = project_folder / "FPL_center.asc"

# Set library search paths for symbols and .lib files
AscEditor.set_custom_library_paths(str(project_folder), str(project_folder))

# Voltage values to sweep
voltages = [9, 29, 40]

for voltage in voltages:
    # Output folder per run
    output_folder = project_folder / f"simdata_{voltage}v"
    output_folder.mkdir(parents=True, exist_ok=True)

    # Load schematic
    netlist = AscEditor(str(asc_file_path))

    # Modify the V2 source value
    netlist.set_component_value("V2", voltage)

    # Add (or replace) .tran command
    netlist.add_instruction(".tran 10m")

    # Run the simulation
    sim = SimRunner(output_folder=str(output_folder), simulator=None)
    sim.run(netlist)

    # Report where output is saved
    for raw, log in sim:
        print(f"[{voltage} V] Raw: {raw}")
        print(f"[{voltage} V] Log: {log}")

end = time.time()
print(f"Total execution time: {end - start:.2f} seconds")

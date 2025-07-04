import subprocess
from pathlib import Path
import sys

# List your scripts in order
scripts = [
    "meas_script.py",
    "log_parse_csv_write.py",
    "part_rating_adder.py",
    "csv_cleaner.py",
    "rating_comparing.py"
]

import subprocess
from pathlib import Path
import sys


working_dir = Path(__file__).parent
python_exec = sys.executable  # Use venv Python

print(f"✅ Master script using Python: {python_exec}")

for script in scripts:
    script_path = working_dir / script
    print(f"\n🚀 Running {script}...")

    try:
        result = subprocess.run([python_exec, str(script_path)])
        if result.returncode != 0:
            print(f"❌ {script} failed with return code {result.returncode}")
            print("⛔ Execution halted due to failure.")
            sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("⛔ Execution interrupted by user.")
        sys.exit(1)

    print(f"✅ {script} completed successfully.")

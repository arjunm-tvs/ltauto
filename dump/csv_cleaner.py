from pathlib import Path
import pandas as pd

def remove_containing_duplicate_columns(csv_file_path):
    csv_file = Path(csv_file_path)
    output_file = csv_file.with_name(csv_file.stem + '_cleaned.csv')

    try:
        df = pd.read_csv(csv_file)

        cleaned_columns = []
        seen = set()

        for col in df.columns:
            matched = False
            for seen_col in seen:
                if col != seen_col and seen_col in col:
                    print(f"Dropping column: '{col}' (contains original column name '{seen_col}')")
                    matched = True
                    break
            if not matched:
                cleaned_columns.append(col)
                seen.add(col)

        df_cleaned = df[cleaned_columns]
        df_cleaned.to_csv(output_file, index=False)
        print(f"✅ Cleaned file saved as: {output_file}")

    except Exception as e:
        print(f"❌ Failed to process {csv_file.name}: {e}")


# === Apply to all CSVs in folder ===
folder = Path(r'D:\OneDrive - TVS Motor Company Ltd\Desktop\PyStart\trial_run')

for csv_file in folder.glob("*.csv"):  #  Fix: "*.csv" should be a string
    print(f" Processing: {csv_file.name}")
    remove_containing_duplicate_columns(csv_file)





# import fitz  # PyMuPDF
# import pandas as pd
# import re
# from difflib import get_close_matches
# from pathlib import Path

# def extract_absolute_maximum_ratings(pdf_path):
#     """
#     Extracts the 'Absolute Maximum Ratings' section from a datasheet PDF and
#     prints the extracted table, then saves it as an Excel file.

#     Args:
#         pdf_path (str or Path): Path to the datasheet PDF file.

#     Returns:
#         Path or None: Path to the saved Excel file, or None if extraction failed.
#     """
#     pdf_path = Path(pdf_path)
#     if not pdf_path.exists() or pdf_path.suffix.lower() != '.pdf':
#         print(f"❌ Invalid PDF file: {pdf_path}")
#         return None

#     output_excel_path = pdf_path.with_stem(pdf_path.stem + "_abs_max_ratings").with_suffix(".xlsx")
    
#     target_phrases = [
#         "absolute maximum ratings", "absolute maximum rating", "maximum ratings",
#         "absolute limits", "maximum limits", "limiting values", "rating (at",
#         "maximum electrical ratings", "absolute maximum limits"
#     ]

#     stop_phrases = [
#         "thermal characteristics", "electrical characteristics", 
#         "recommended", "package information", "ordering information"
#     ]

#     doc = fitz.open(str(pdf_path))

#     def find_matching_section(pages, threshold=0.8):
#         for page_num, page in enumerate(pages):
#             text = page.get_text("text")
#             lines = text.splitlines()
#             candidates = [line.strip() for line in lines if 5 < len(line.strip()) < 60]
#             for candidate in candidates:
#                 match = get_close_matches(candidate.lower(), target_phrases, n=1, cutoff=threshold)
#                 if match:
#                     return page_num, lines, candidate
#         return None, None, None

#     page_index, lines, matched_header = find_matching_section(doc)

#     if page_index is None:
#         print("❌ Could not find any matching section.")
#         return None

#     print(f"✅ Found section: '{matched_header}' on page {page_index + 1}")

#     start_line = next((i for i, line in enumerate(lines) if matched_header.lower() in line.lower()), None)
#     if start_line is None:
#         print("⚠️ Match found but line not located.")
#         return None

#     def extract_table_from_lines(lines, start_line):
#         table_lines = []
#         for line in lines[start_line + 1:]:
#             if any(stop.lower() in line.lower() for stop in stop_phrases):
#                 break
#             if len(line.strip()) < 3:
#                 continue
#             table_lines.append(line.strip())
#         return table_lines

#     def parse_table_lines(lines):
#         # Remove any known non-data lines
#         clean_lines = [l.strip() for l in lines if l.strip() and not l.strip().lower().startswith("http")]

#         # 1. Extract part numbers
#         device_line = next((l for l in clean_lines if "MBRS" in l and ',' in l), None)
#         if device_line:
#             parts = [p.strip() for p in device_line.split(',')]
#         else:
#             print("❌ Device part numbers not found.")
#             return []

#         # 2. Find where actual data starts
#         try:
#             start_index = clean_lines.index("Unit") + 1
#         except ValueError:
#             print("❌ 'Unit' keyword not found.")
#             return []

#         data = clean_lines[start_index:]

#         # 3. Process blocks (rating rows, symbol, values, unit)
#         rows = []
#         i = 0
#         while i < len(data):
#             rating_lines = []

#             # Grab rating description (usually multiple lines)
#             while i < len(data) and re.search(r'[A-Za-z]', data[i]) and not re.match(r'^[A-Z]*\(?.*\)?$', data[i]) and data[i] not in ["Amps", "Volts", "°C/W", "°C"]:
#                 rating_lines.append(data[i])
#                 i += 1

#             rating_name = " ".join(rating_lines).strip()

#             # Symbol
#             if i >= len(data):
#                 break
#             symbol = data[i]
#             i += 1

#             # Values for each device (up to 4 devices, flexible)
#             values = []
#             while i < len(data) and re.search(r'\d', data[i]) or '–' in data[i] or '@' in data[i]:
#                 values.append(data[i])
#                 i += 1

#             # Pad missing device values
#             while len(values) < len(parts):
#                 values.append("")

#             # Unit
#             if i < len(data):
#                 unit = data[i]
#                 i += 1
#             else:
#                 unit = ""

#             rows.append([rating_name, symbol] + values + [unit])

#         headers = ["Rating", "Symbol"] + parts + ["Unit"]
#         return [headers] + rows

#     table_lines = extract_table_from_lines(lines, start_line)

#     # Handle redirected tables on next page
#     if (not table_lines or any("see" in l.lower() and "following" in l.lower() for l in table_lines)) and page_index + 1 < len(doc):
#         print("🔁 Table likely on next page, checking page", page_index + 2)
#         next_lines = doc[page_index + 1].get_text("text").splitlines()
#         table_lines = [line.strip() for line in next_lines if len(line.strip()) > 3]

#     if not table_lines:
#         print("⚠️ No table lines found after header or on next page.")
#         return None

#     # Show raw lines for confirmation
#     print("\n🔎 Raw lines found:")
#     for line in table_lines:
#         print(line)
    
#     if not table_lines:
#         print("⚠️ No table lines found after header.")
#         return None

#     table = parse_table_lines(table_lines)

#     # Create the DataFrame
#     if len(table) > 1 and all(any(char.isalpha() for char in cell) for cell in table[0]):
#         df = pd.DataFrame(table[1:], columns=table[0])
#     else:
#         df = pd.DataFrame(table)

#     # 🖨️ Print to console before exporting
#     print("\n📋 Extracted DataFrame:")
#     print(df)

#     # Export to Excel
#     # df.to_excel(output_excel_path, index=False)
#     # print(f"\n📦 Exported to: {output_excel_path}")
#     # return output_excel_path


# from pathlib import Path
from pathlib import Path
import fitz  # PyMuPDF
from difflib import get_close_matches

def extract_all_absolute_maximum_sections(pdf_path):
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"❌ File not found: {pdf_path}")
        return

    doc = fitz.open(str(pdf_path))

    target_phrases = [
        "absolute maximum ratings", "maximum ratings", "maximum rating",
        "limiting values", "absolute limits", "rating (at", "rating:", "maximum electrical ratings"
    ]

    stop_phrases = ["thermal", "electrical", "recommended", "ordering", "characteristics"]

    output_txt_path = pdf_path.with_stem(pdf_path.stem + "_abs_max_ratings_all").with_suffix(".txt")

    all_sections = []

    for i, page in enumerate(doc):
        text = page.get_text("text")
        lines = text.splitlines()

        for j, line in enumerate(lines):
            match = get_close_matches(line.lower(), target_phrases, n=1, cutoff=0.8)
            if match:
                print(f"✅ Found section: '{line.strip()}' on page {i + 1}")

                start_line_index = j + 1
                section_lines = lines[start_line_index:]

                # Check for "see next page"
                if any("see" in l.lower() and "next" in l.lower() for l in section_lines[:5]) and i + 1 < len(doc):
                    print(f"🔁 Following 'see next page' hint → page {i + 2}")
                    section_lines = doc[i + 1].get_text("text").splitlines()

                # Clean and truncate
                cleaned_lines = []
                for l in section_lines:
                    if any(stop in l.lower() for stop in stop_phrases):
                        break
                    if l.strip():
                        cleaned_lines.append(l.strip())

                # Add marker and lines
                all_sections.append(f"\n--- Section from page {i + 1} ---\n")
                all_sections.extend(cleaned_lines)

    if not all_sections:
        print("❌ No matching sections found.")
        return None

    # Save all matched blocks to .txt
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_sections))

    print(f"📄 All matched sections saved to: {output_txt_path}")
    return output_txt_path

extract_all_absolute_maximum_sections("C:/Users/Arjun.M/Downloads/BC846.PDF")

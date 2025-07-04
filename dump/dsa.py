# def profitmaximizer(stock):
#     maxprofit = 0
#     buyprice = stock[0]

#     for i in range(len(stock)-1):
#         if stock[i]<stock[i+1]:
#             maxprofit = stock[i+1] - buyprice
#         else:
#             buyprice = stock[i]
#         print("max profit:", maxprofit, "min buy price", buyprice)

# profitmaximizer([1,2,3,8,4,5,6])

# def pl(ar):
#     maxright = ar[-1]
#     maxrigtharray = []
#     minleftarray = []
#     minleft = ar[0]
#     for k in range(len(ar)):
#         if ar[len(ar)-k-1]>maxright:
#             maxright = ar[k]
#         maxrigtharray.append(maxright)
#     for k in range(len(ar)):
#         if ar[k]<minleft:
#             minleft = ar[k]
#         minleftarray.append(minleft)
    
#     maxrigtharray.reverse()
#     maxprft = 0
#     for k in range(len(ar)):
#         if maxrigtharray[k] - minleftarray[k] > maxprft:
#             maxprft = maxrigtharray[k] - minleftarray[k]
#     print(maxprft)

# pl([1,2,3,56,8,4,23,5,6])
from pathlib import Path
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
from difflib import get_close_matches

# Optional: set the Tesseract path manually if not in PATH
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Arjun.M\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

def extract_abs_max_ratings_ocr_all(pdf_path):
    pdf_path = Path(pdf_path)
    doc = fitz.open(str(pdf_path))

    # Match headings like "Absolute Maximum Ratings"
    target_phrases = [
        "absolute maximum ratings", "maximum ratings", "maximum rating",
        "limiting values", "absolute limits", "rating (at", "rating:", "maximum electrical ratings"
    ]

    # Used to stop the section once another block is reached
    stop_phrases = [
        "thermal", "electrical", "recommended", "ordering", "characteristics",
        "junction", "forward voltage", "reverse recovery", "package", "device marking"
    ]

    all_sections = []
    output_txt_path = pdf_path.with_stem(pdf_path.stem + "_abs_max_ocr_all").with_suffix(".txt")

    for i, page in enumerate(doc):
        # OCR the entire page
        pix = page.get_pixmap(dpi=300)
        image = Image.open(io.BytesIO(pix.tobytes("png")))
        ocr_text = pytesseract.image_to_string(image)
        lines = ocr_text.splitlines()

        # Find the heading match in OCR text
        for j, line in enumerate(lines):
            if get_close_matches(line.lower(), target_phrases, cutoff=0.8):
                print(f"✅ OCR found heading: '{line.strip()}' on page {i + 1}")

                section_lines = lines[j + 1:]

                # Extract text until we hit a section boundary
                block = []
                for l in section_lines:
                    if any(stop in l.lower() for stop in stop_phrases):
                        break
                    if l.strip():
                        block.append(l.strip())

                if block:
                    all_sections.append(f"\n--- Section from page {i + 1} ---\n")
                    all_sections.extend(block)
                break  # stop after first match per page

    # Save output to text file
    if all_sections:
        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(all_sections))
        print(f"\n📄 Extracted all Absolute Maximum Ratings sections to: {output_txt_path}")
    else:
        print("❌ No Absolute Maximum Ratings sections found via OCR.")

extract_abs_max_ratings_ocr_all("C:/Users/Arjun.M/Downloads/BC846.PDF")


import os
import fitz  # PyMuPDF
from zipfile import ZipFile

# Set the base directories
BASE_DIR = os.path.expanduser("~/Desktop/PDF")
OUTPUT_DIR = os.path.expanduser("~/Desktop/Output")

def convert_pdf_to_cbz(pdf_path, relative_path):
    """Convert a PDF file to a CBZ file while maintaining folder structure."""
    output_folder = os.path.join(OUTPUT_DIR, relative_path)
    os.makedirs(output_folder, exist_ok=True)

    cbz_path = os.path.join(output_folder, os.path.splitext(os.path.basename(pdf_path))[0] + ".cbz")
    temp_image_folder = os.path.join(output_folder, "temp_images")

    # Create a temporary folder for images
    os.makedirs(temp_image_folder, exist_ok=True)

    # Open the PDF
    pdf = fitz.open(pdf_path)

    image_files = []
    for page_num in range(len(pdf)):
        page = pdf.load_page(page_num)
        pix = page.get_pixmap()

        image_filename = os.path.join(temp_image_folder, f"page_{page_num:03}.png")
        pix.save(image_filename)
        image_files.append(image_filename)

    pdf.close()

    # Create CBZ file
    with ZipFile(cbz_path, 'w') as cbz:
        for image_file in image_files:
            cbz.write(image_file, os.path.basename(image_file))

    # Cleanup temporary image files
    for image_file in image_files:
        os.remove(image_file)

    # Remove the temporary folder
    os.rmdir(temp_image_folder)

    print(f"✅ Converted '{pdf_path}' to '{cbz_path}'")

# Recursively search for PDF files and convert them
for root, _, files in os.walk(BASE_DIR):
    for file in files:
        if file.lower().endswith(".pdf"):
            pdf_path = os.path.join(root, file)
            
            # Get relative path for output folder structure
            relative_path = os.path.relpath(root, BASE_DIR)
            
            convert_pdf_to_cbz(pdf_path, relative_path)

print("\n🎉 ✅ All PDFs converted to CBZ files with folder structure maintained!")

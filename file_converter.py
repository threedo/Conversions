import os
import fitz  # PyMuPDF for PDF handling
from zipfile import ZipFile
import shutil

# Supported file types for conversion
SUPPORTED_FORMATS = ['PDF', 'CBZ']

# Function to get user input for conversion types
def get_conversion_choice(prompt, choices):
    print(f"{prompt}")
    for i, choice in enumerate(choices, start=1):
        print(f"{i}. {choice}")
    while True:
        try:
            selection = int(input("Select an option: "))
            if 1 <= selection <= len(choices):
                return choices[selection - 1]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

# Function to convert PDF to CBZ
def pdf_to_cbz(pdf_path, output_path):
    temp_dir = os.path.join(output_path, 'temp_images')
    os.makedirs(temp_dir, exist_ok=True)

    with fitz.open(pdf_path) as pdf_doc:
        for page_num in range(len(pdf_doc)):
            page = pdf_doc.load_page(page_num)
            img_path = os.path.join(temp_dir, f"{page_num:03}.png")
            pix = page.get_pixmap()
            pix.save(img_path)

    cbz_path = os.path.join(output_path, os.path.splitext(os.path.basename(pdf_path))[0] + '.cbz')
    with ZipFile(cbz_path, 'w') as cbz:
        for img_file in sorted(os.listdir(temp_dir)):
            cbz.write(os.path.join(temp_dir, img_file), img_file)

    shutil.rmtree(temp_dir)
    print(f"✅ Converted {pdf_path} to {cbz_path}")

# Function to convert CBZ to PDF
def cbz_to_pdf(cbz_path, output_path):
    temp_dir = os.path.join(output_path, 'temp_images')
    os.makedirs(temp_dir, exist_ok=True)

    with ZipFile(cbz_path, 'r') as cbz:
        cbz.extractall(temp_dir)

    image_files = [os.path.join(temp_dir, f) for f in sorted(os.listdir(temp_dir))]
    pdf_path = os.path.join(output_path, os.path.splitext(os.path.basename(cbz_path))[0] + '.pdf')
    pdf_doc = fitz.open()

    for img_path in image_files:
        img = fitz.open(img_path)
        rect = img[0].rect
        pdf_page = pdf_doc.new_page(width=rect.width, height=rect.height)
        pdf_page.show_pdf_page(rect, img, 0)

    pdf_doc.save(pdf_path)
    pdf_doc.close()
    shutil.rmtree(temp_dir)
    print(f"✅ Converted {cbz_path} to {pdf_path}")

# Main script
def main():
    # Ask for source and target formats
    source_format = get_conversion_choice("What file type are we converting FROM?", SUPPORTED_FORMATS)
    target_format = get_conversion_choice("What file type are we converting TO?", SUPPORTED_FORMATS)

    if source_format == target_format:
        print("Source and target formats cannot be the same. Exiting.")
        return

    # Define the source folder and output folder
    source_folder = os.path.expanduser("~/Desktop/PDF")
    output_folder = os.path.expanduser("~/Desktop/Output")
    os.makedirs(output_folder, exist_ok=True)

    # Walk through all files and convert them based on the chosen formats
    for root, _, files in os.walk(source_folder):
        relative_path = os.path.relpath(root, source_folder)
        target_subfolder = os.path.join(output_folder, relative_path)
        os.makedirs(target_subfolder, exist_ok=True)

        for file in files:
            file_path = os.path.join(root, file)

            if source_format == 'PDF' and target_format == 'CBZ' and file.lower().endswith('.pdf'):
                pdf_to_cbz(file_path, target_subfolder)

            elif source_format == 'CBZ' and target_format == 'PDF' and file.lower().endswith('.cbz'):
                cbz_to_pdf(file_path, target_subfolder)

    print("🎉 All files have been converted!")

if __name__ == '__main__':
    main()

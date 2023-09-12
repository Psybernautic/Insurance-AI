#               ______ _____ _      _____  ____________ _____ _____  _____ _____ _____ _____ _   _ _____ 
#               |  ___|_   _| |    |  ___| | ___ \ ___ \  _  /  __ \|  ___/  ___/  ___|_   _| \ | |  __ \
#               | |_    | | | |    | |__   | |_/ / |_/ / | | | /  \/| |__ \ `--.\ `--.  | | |  \| | |  \/
#               |  _|   | | | |    |  __|  |  __/|    /| | | | |    |  __| `--. \`--. \ | | | . ` | | __ 
#               | |    _| |_| |____| |___  | |   | |\ \\ \_/ / \__/\| |___/\__/ /\__/ /_| |_| |\  | |_\ \
#               \_|    \___/\_____/\____/  \_|   \_| \_|\___/ \____/\____/\____/\____/ \___/\_| \_/\____/
#------------------------------------------------------------------------------------------------------------ 
#------------------------------------------------------------------------------------------------------------                                                                                          

                                                                               
#   Project         :   Insurance-AI
#   File            :   file_processing.py
#   Programmers     :   Alonzo Gutierrez, Sebastian Posada
#   Description     :   This module provides functions for working with PDF files.
#                       It includes a function to determine the MIME type of a file based on its extension
#                       and a function to split a PDF into groups of specified pages and save them as separate files.

#   First Version   :   September 11, 2023


import PyPDF2
import os

def get_mime_type(file_name):
    """
    Determine the MIME type of a file based on its file extension.

    Args:
        file_name (str): The name of the file including its extension.

    Returns:
        str: The MIME type of the file, or 'error' for unsupported file types.
    """
    # Process the current file based on its mime type
    if file_name.lower().endswith('.pdf'):
        mime_type = 'application/pdf'
    elif file_name.lower().endswith(('.jpg', '.jpeg')):
        mime_type = 'image/jpeg'
    elif file_name.lower().endswith('.png'):
        mime_type = 'image/png'
    elif file_name.lower().endswith('.tiff'):
        mime_type = 'image/tiff'
    else:
        print(f"Unsupported file type: {file_name}")
        mime_type = 'error'

    return mime_type


def get_file_name_without_extension(file_name):
    root_name, _ = os.path.splitext(file_name)
    return root_name

def split_pdf_into_groups(filename, pdf, output_directory, pages_per_group=15):
    """
    Split a PDF into groups of specified number of pages and save each group as a separate PDF file.

    Args:
        input_pdf_path (str): The path to the input PDF file to be split.
        output_directory (str): The directory where the split PDF groups will be saved.
        pages_per_group (int, optional): The number of pages per group (default is 15).

    Returns:
        None
    """
    
    total_pages = len(pdf.pages)

    # Calculate the number of groups
    num_groups = (total_pages + pages_per_group - 1) // pages_per_group

    for group_number in range(num_groups):
        pdf_writer = PyPDF2.PdfWriter()

        # Calculate the range of pages for the current group
        start_page = group_number * pages_per_group
        end_page = min((group_number + 1) * pages_per_group, total_pages)

        # Add pages to the PDF writer for the current group
        for page_num in range(start_page, end_page):
            pdf_writer.add_page(pdf.pages[page_num])

        # Save the current group as a separate PDF file
        output_pdf_path = f"{output_directory}/{filename}_part_{group_number + 1}.pdf"
        with open(output_pdf_path, "wb") as output_pdf_file:
            pdf_writer.write(output_pdf_file)


def delete_file(file_path):
    """
    Deletes a file from the specified file path.

    Args:
        file_path (str): The path to the file to be deleted.

    Returns:
        None

    Raises:
        FileNotFoundError: If the specified file does not exist.
        Exception: If any other error occurs during file deletion.
    """
    try:
        os.remove(file_path)
        print(f"File '{file_path}' has been deleted.")
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred while deleting the file: {e}")

def get_files_to_process(scans_directory, supported_extensions):
    files_to_process = [f for f in os.listdir(scans_directory) if os.path.splitext(f)[1].lower() in supported_extensions]
    return files_to_process
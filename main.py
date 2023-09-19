#       .___   _______      _________  ____ ___  __________     _____     _______    _________   ___________             _____    .___ 
#       |   |  \      \    /   _____/ |    |   \ \______   \   /  _  \    \      \   \_   ___ \  \_   _____/            /  _  \   |   |
#       |   |  /   |   \   \_____  \  |    |   /  |       _/  /  /_\  \   /   |   \  /    \  \/   |    __)_    ______  /  /_\  \  |   |
#       |   | /    |    \  /        \ |    |  /   |    |   \ /    |    \ /    |    \ \     \____  |        \  /_____/ /    |    \ |   |
#       |___| \____|__  / /_______  / |______/    |____|_  / \____|__  / \____|__  /  \______  / /_______  /          \____|__  / |___|
#                     \/          \/                     \/          \/          \/          \/          \/                   \/       
#---------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------


#   Project         :   Insurance-AI                                                                                                                     
#   File            :   main.py                                                                                                                          
#   Programmers     :   Alonzo Gutierrez, Sebastian Posada                                                                                               
#   Description     :   Insurance-AI aims to automate the processing of incoming emails containing PDF attachments.                                      
#                       It involves reading these emails, downloading the attachments, utilizing Google's Document AI for content extraction,            
#                       determining the document's purpose, and performing validation checks before routing the document to its appropriate destination  
#                       This system helps streamline document handling by automating repetitive tasks and reducing manual intervention.                  
#   First Version   :   September 8, 2023                                                                                                                


# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from email_functions import *
from mysql_functions import *
from file_processing import *
from document_ai import *
import re
import uuid

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

bill_of_lading_search_terms = ["Bill of Lading","b/l","Manifest From","Consignee name and address",
                               "Description Of Goods","Container No.", "Point of origin", "Destination And Route",
                               "Transportation bill of lading", "Shipper Signature"]
invoice_search_terms = ["Invoice Number","Invoice Date","Payment Terms","Due Date","Invoice","Freight Subtotal","Total Due","Invoice #"]

maximum_pages = 1
# ---------------------------------------------------------------------
# Directory Setup and Database Connection
# ---------------------------------------------------------------------

# Get the current directory
current_directory = os.getcwd()

# Create PDF directory if it does not already exist
pdf_directory = create_PDF_directory(current_directory)

# # Log in to MySQL Database
connection = database_login()

# # Create cursor for MySQL
cursor = connection.cursor()

# Directory paths where files are stored
scans_directory = r'PDFs'  
testing_directory = r'Testing'


# ---------------------------------------------------------------------
# Email Setup and Subfolder Selection
# ---------------------------------------------------------------------

# Login to mail box
connect_to_email(email_user, email_pass, inbox)

# Define parent folder
#parentfolder_name = "Inbox"

# Define the name of the subfolder within "inbox" to select
#subfolder_name = "HEAD_OFFICE"  # Replace with the name of the subfolder you want to select

# Select the subfolder within "inbox"
#success = select_subfolder_in_inbox(mailbox, subfolder_name)

#if success:
#    print(f"Successfully selected subfolder: {subfolder_name}")
#else:
#    print(f"Failed to select subfolder: {subfolder_name}")


# ---------------------------------------------------------------------
# Email Retrieval and Processing
# ---------------------------------------------------------------------

    
# Retrieve the IDs of unread emails from the specified mailbox.
unread_email_list = get_unread_emails(mailbox)

# If there are no new emails, wait 5 seconds for emails to populate
if len(unread_email_list) == 0:
    print("No new unread emails")
    #time.sleep(180)

else:
    # Search for the oldest unread email
    oldest_email_id = unread_email_list[0].split()[0]
    oldest_email_id_value = str(oldest_email_id)

    # Fetch oldest unread email by id

    status, data = mailbox.fetch(oldest_email_id, "(RFC822)")
    try:
        email_data = email.message_from_bytes(data[0][1])    
    except email.errors.MessageError as e:
        print("Error trying to fetch email")

    # ---------------------------------------------------------------------
    # Email Data Extraction and Database Insertion
    # ---------------------------------------------------------------------

    # Store separate parts of the email
    sender = get_sender(email_data)
    receiver = extract_first_three_receivers_string(email_data)
    body = get_body(email_data)

    # Download attachment from the email if there are any

    if not get_attachments(email_data):
        print("No attachment downloaded")


    # Insert email into database
    insert_email_to_database(sender, receiver, body, cursor, connection)


# ---------------------------------------------------------------------
# File Processing With Document AI OCR Processor
# ---------------------------------------------------------------------

files_to_process = get_files_to_process(pdf_directory, supported_extensions)

if len(files_to_process) > 0:
    for file in files_to_process:
        try:
            # Combine the 'pdf_directory' and 'file' to create the full file path.
            file_path = os.path.join(pdf_directory, file)

            # Extract the file name without the extension.
            file_name = get_file_name_without_extension(file)

            # Create and store directory paths for the files to be sorted into
            new_directory_path, BOL_directory_path, invoice_directory_path = create_directories(current_directory, file_name)

            # Open the PDF file using PyPDF2.
            pdf = PyPDF2.PdfReader(file_path)

            # Get the total number of pages in the PDF.
            total_pages = len(pdf.pages)

            # Check if there is at least one page in the PDF.
            if total_pages >= 1:
                # Split the PDF into groups (e.g., individual pages) starting from page 1.
                split_pdf_into_groups(file_name,pdf, new_directory_path, maximum_pages)

                # Delete the original PDF file.
                delete_file(file_path)

                # Get a list of files to process in the 'new_directory_path' with supported extensions.
                split_files_to_process = get_files_to_process(new_directory_path, supported_extensions)

                for file in split_files_to_process:

                    # Construct the full file path by joining the file name with the scans_directory
                    file_path = os.path.join(new_directory_path, file)

                    # Get the mime type of the file
                    mime_type = get_mime_type(file)

                    try:
                        # API call to Document AI for processing the document
                        response = quickstart(project_id, location, processor_id, file_path, mime_type)

                        # Extract the content from the response
                        text = response.document.text
                        document = response.document
                        pages = document.pages
                        page_num = 1

                        bill_of_lading_count_total = 0
                        invoice_count_total = 0

                        print(f"Scanning {file}...")
                        block_list = []

                        # ---------------------------------------------------------------------
                        # Extract text blocks from each document and store in a list
                        # ---------------------------------------------------------------------

                        try:

                            # Iterate over the text blocks in the page
                            for block in pages[0].blocks:
                                # Extract the text from the layout of the block and append it to the block_list
                                block_text = layout_to_text(block.layout, text)
                                block_list.append(repr(block_text))

                                bill_of_lading_count = 0
                                invoice_count = 0

                            # ---------------------------------------------------------------------
                            # Enter data into database using mysql
                            # ---------------------------------------------------------------------

                            # Generate a unique ID for the document
                            unique_id = str(uuid.uuid4())

                            # POD / BL              
                            for item in block_list:
                                item_lower = item.lower()
                                for term in bill_of_lading_search_terms:
                                    if term.lower() in item_lower:
                                        bill_of_lading_count += 1

                            # Invoice
                            for item in block_list:
                                item_lower = item.lower()
                                for term in invoice_search_terms:
                                    if term.lower() in item_lower:
                                        invoice_count += 1

                            bill_of_lading_count_total += bill_of_lading_count
                            invoice_count_total += invoice_count

                        except Exception as e:
                            print("error ")       
                        
                        table_name = ""
                        # Determine where the file should be placed
                        if bill_of_lading_count_total >=5:
                            print("moving file to bill of lading directory")
                            move_file(file_path, BOL_directory_path)
                            table_name = "bol"
                            insert_to_database(unique_id,file_name,block_list,cursor,connection, table_name)

                        elif invoice_count_total >= 5:
                            print("moving file to invoice directory")
                            move_file(file_path, invoice_directory_path)
                            table_name = "documents"
                            insert_to_database(unique_id,file_name,block_list,cursor,connection, table_name)

                        else:
                            print("Unable to determine document type..")
                            print("Sending file for human intervention")


                    except Exception as e:
                        print("Error trying to parse document using OCR: ", e)

            else:
                print("No pages found to process")

        except Exception as e:
            print(f"Error processing file: {file}. ", e)


else:
    for num_dots in range(4):
        message = "Waiting for email to come in" + "." * num_dots
        print(message, end='\r')  # Use '\r' to overwrite the same line
        time.sleep(1)  # Wait for 1 second
        print(" " * len(message), end='\r')  # Clear the line
        



# ---------------------------------------------------------------------
# Determine document type
# ---------------------------------------------------------------------


# ---------------------------------------------------------------------
# Logout from Email
# ---------------------------------------------------------------------

# Logout from mail box
mailbox.logout()

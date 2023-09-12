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

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

maximum_pages = 15
# ---------------------------------------------------------------------
# Directory Setup and Database Connection
# ---------------------------------------------------------------------

# Get the current directory
current_directory = os.getcwd()

# Create PDF directory if it does not already exist
pdf_directory = create_PDF_directory(current_directory)

# Log in to MySQL Database
connection = database_login()

# Create cursor for MySQL
cursor = connection.cursor()

# Define the directory path where your files are located
scans_directory = r'PDFs'  


# ---------------------------------------------------------------------
# Email Setup and Subfolder Selection
# ---------------------------------------------------------------------

# Login to mail box
connect_to_email(email_user, email_pass, inbox)

# Define parent folder
parentfolder_name = "Inbox"

# Define the name of the subfolder within "inbox" to select
subfolder_name = "HEAD_OFFICE"  # Replace with the name of the subfolder you want to select

# Select the subfolder within "inbox"
success = select_subfolder_in_inbox(mailbox, subfolder_name)

if success:
    print(f"Successfully selected subfolder: {subfolder_name}")
else:
    print(f"Failed to select subfolder: {subfolder_name}")


# ---------------------------------------------------------------------
# Email Retrieval and Processing
# ---------------------------------------------------------------------

# Retrieve the IDs of unread emails from the specified mailbox.
unread_email_list = get_unread_emails(mailbox)

# If there are no new emails, wait 5 seconds for emails to populate
if len(unread_email_list) == 0:
    print("No new unread emails")
    time.sleep(5)

# Search for the oldest unread email
oldest_email_id = unread_email_list[0].split()[0]
oldest_email_id_value = str(oldest_email_id)
print("Oldest unread email id: " + oldest_email_id_value)

# Fetch oldest unread email by id

status, data = mailbox.fetch(oldest_email_id, "(RFC822)")
email_data = email.message_from_bytes(data[0][1])



# ---------------------------------------------------------------------
# Email Data Extraction and Database Insertion
# ---------------------------------------------------------------------

# Store separate parts of the email
#sender = email_data["From"]
#receiver = extract_first_three_receivers_string(email_data)
#body = get_body(email_data)

# Download attachment from the email if there are any

#if not get_attachments(email_data):
#    print("No attachment downloaded")


# Insert email into database
#insert_to_database(sender, receiver, body, cursor, connection)


# ---------------------------------------------------------------------
# If greater than 15 pages, Split the PDF
# ---------------------------------------------------------------------

files_to_process = get_files_to_process(scans_directory, supported_extensions)

for file in files_to_process:
    try:
        file_path = os.path.join(scans_directory, file)
        file_name = get_file_name_without_extension(file)
        mime_type = get_mime_type(file)

        pdf = PyPDF2.PdfReader(file_path)
        total_pages = len(pdf.pages)

        if total_pages > maximum_pages:
            split_pdf_into_groups(file_name,pdf, scans_directory)
            delete_file(file_path)
            files_to_process = get_files_to_process(scans_directory, supported_extensions)

    except Exception as e:
        print(f"Error processing file: {file}. ", e)



for file in files_to_process:
    # Construct the full file path by joining the file name with the scans_directory
    file_path = os.path.join(scans_directory, file)
    try:
        # Create an empty list to store text blocks
        block_list = []

        # Process the PDF file using the quickstart function
        response = quickstart(project_id, location, processor_id, file_path, mime_type)

        # Extract the text content from the response
        text = response.document.text
        document = response.document
        pages = document.pages

        # Iterate over the pages in the document
        for page in pages:
            # Iterate over the text blocks in the page
            for block in page.blocks:
                # Extract the text from the layout of the block and append it to the block_list
                block_text = layout_to_text(block.layout, text)
                block_list.append(repr(block_text))
            # 

        # Print the list of text blocks for the current file
        print(block_list)

        # Pause execution for 3 seconds (optional, for demonstration purposes)
        time.sleep(3)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # In case of an error, send the file to an email for processing
        print(f"Sending file to {email_user} for human intervention")
        




# ---------------------------------------------------------------------
# Extract text blocks from each document
# ---------------------------------------------------------------------


# ---------------------------------------------------------------------
# Determine document type
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
# Logout from Email
# ---------------------------------------------------------------------

# Logout from mail box
mailbox.logout()

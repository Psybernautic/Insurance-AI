#                            .___     _____       _____    __________ 
#                            |   |   /     \     /  _  \   \______   \
#                            |   |  /  \ /  \   /  /_\  \   |     ___/
#                            |   | /    Y    \ /    |    \  |    |    
#                            |___| \____|__  / \____|__  /  |____|    
#                                          \/          \/             
#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------


#   Project         :   Insurance-AI
#   File            :   email_functions.py
#   Programmers     :   Alonzo Gutierrez, Sebastian Posada
#   Description     :   This module provides functions for interacting with an email server using IMAP4_SSL.
#                       It includes functions for connecting to the email server, selecting subfolders, retrieving unread emails,
#                       and extracting email body content. User credentials and server settings are configured at the beginning.

#   First Version   :   September 8, 2023


# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import imaplib
import glob
import os
import time
import email
import subprocess
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.header import decode_header

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

#email_user = "pods@rometransportation.com"
#email_pass = "p01V6$RC$IM5hhMCY09w"
imap_server = "imap.rometransportation.com"
mailbox = imaplib.IMAP4_SSL(imap_server)
inbox = "inbox"
supported_extensions = ['.pdf', '.jpg', '.png', '.tiff']

email_user = "document-ai@loadaccess.com"
email_pass = "crbQ#8xGTM"

def connect_to_email(email_user, email_pass, inbox):
    """
    Connects to an email server using IMAP4_SSL, logs in with the provided credentials, and selects the specified inbox.

    Args:
        imap_server (str): The IMAP server address.
        email_user (str): The email address of the user.
        email_pass (str): The password of the email user.
        inbox (str): The name of the inbox to select.

    Returns:
        imaplib.IMAP4_SSL: An IMAP4_SSL object representing the established connection.
    """
    try:
        mailbox.login(email_user, email_pass)
        mailbox.select(inbox)
        print("Logged in successfully")
        print(f"Current folder: {inbox}")

    except imaplib.IMAP4.error as imap_error:
        print(imap_error)
    except Exception as e:
        print("An error occurred logging into email server:", e)


def select_subfolder_in_inbox(mailbox, subfolder_name):
    """
    Select a subfolder within the "inbox" folder on an IMAP email server.

    Args:
        mailbox (imaplib.IMAP4_SSL): An IMAP4_SSL object representing the mailbox.
        subfolder_name (str): The name of the subfolder you want to select.

    Returns:
        bool: True if the subfolder was successfully selected, False otherwise.
    """
    # Construct the full mailbox name
    full_mailbox_name = f'INBOX/{subfolder_name}'

    # Select the subfolder
    try:
        mailbox.select(full_mailbox_name, readonly=False)
        return True
    except imaplib.IMAP4.error:
        return False


def get_unread_emails(mailbox):
    """
    Retrieve the IDs of unread emails from the specified mailbox.

    Args:
        mailbox (imaplib.IMAP4_SSL): An IMAP4_SSL object representing the mailbox.

    Returns:
        list: A list of email IDs of unread emails, or an empty list if no unread emails are found.
    """
    try:
        status, email_ids = mailbox.search(None, 'UNSEEN')  # Search for unread emails
        return email_ids[0].split() if status == 'OK' else []
    except Exception as e:
        print(f"Error trying to get unread emails: ", e)




def extract_first_three_receivers_string(email_message):
    """
    Extracts the first three receiving addresses from an email message and returns them as a single string.

    Args:
        email_message (email.message.Message): The email message.

    Returns:
        str: A string containing the first three receiving addresses, separated by commas.
    """
    try:

        # Get the "To" field from the email message
        to_field = email_message["To"]

        # Split the "To" field into individual addresses
        to_addresses = to_field.split(',')

        # Initialize a list to store the first three receiving addresses
        first_three_receivers = []

        # Extract the first three receiving addresses (if available)
        for i in range(3):
            if i < len(to_addresses):
                first_three_receivers.append(to_addresses[i].strip())

        # Combine the first three receiving addresses into a single string
        receivers_string = ', '.join(first_three_receivers)

        return receivers_string
    
    except Exception as e:
        print("Error trying to parse receiver's email: ", e)

def get_sender(data):
    sender = data["From"]
    return sender

def get_dateTime(data):
    date_str = data["Date"]
    return date_str


def get_body(data):
    """
    Extracts the email body from an email message.

    Args:
        data (email.message.Message): An email message object.

    Returns:
        str: The email body content as a string.
    """
    try:
        if data.is_multipart():
            return get_body(data.get_payload(0))
        else:
            return data.get_payload(None, True)
    except Exception as e:
        print(f"Error trying to get body content: ", e)



def create_PDF_directory(current_directory):
    """
    Creates a directory named 'PDFs' within the given 'current_directory' if it doesn't exist,
    and returns the path to the created directory.

    Args:
        current_directory (str): The path to the current directory where the 'PDFs' directory will be stored.

    Returns:
        str: The path to the created 'PDFs' directory.
    """
    pdf_directory = os.path.join(current_directory, "PDFs")
    if not os.path.exists(pdf_directory):
        os.mkdir(pdf_directory)
    return pdf_directory

def create_split_pdf_directory(current_directory):
    """
    Creates a directory with the name of the pdf processed within the given 'current_directory' if it doesn't exist,
    and returns the path to the created directory.

    Args:
        current_directory (str): The path to the current directory where the 'PDFs' directory will be stored.

    Returns:
        str: The path to the created 'PDFs' directory.
    """
    pdf_directory = os.path.join(current_directory, "Split-PDFs")
    if not os.path.exists(pdf_directory):
        os.mkdir(pdf_directory)

    return pdf_directory



def get_attachments(msg):
    """
    Extracts email attachments of supported formats from an email message and saves them to the 'PDFs' directory
    within the current working directory, handling the conversion of 'winmail.dat' files if present.

    Args:
        msg (email.message.Message): An email message containing attachments.

    Returns:
        bool: True if supported attachments were successfully extracted and saved, False otherwise.
    """
    attachments_saved = False  # Initialize a flag to track if any supported attachments were saved
    
    try:

        for part in msg.walk():
            # Check if the part is a multipart message, and if so, skip it
            if part.get_content_maintype() == 'multipart':
                continue

            # Check if the part has a 'Content-Disposition' header, and if not, skip it
            if part.get('Content-Disposition') is None:
                continue
            
            # Get the filename of the attachment
            fileName = part.get_filename()

            # Check if a valid filename is found, and if it has a supported extension
            if bool(fileName) and is_supported_extension(fileName, supported_extensions):
                current_directory = os.getcwd()  # Get the current directory

                # Check if "PDFs" directory exists, create it if not
                pdf_directory = os.path.join(current_directory, "PDFs")
                if not os.path.exists(pdf_directory):
                    os.mkdir(pdf_directory)

                # Sanitize the filename to remove invalid characters
                sanitized_filename = sanitize_filename(fileName)

                # Create the full filepath to save the attachment inside the "PDFs" directory
                filepath = os.path.join(pdf_directory, sanitized_filename)

                # Write the attachment content to the file
                with open(filepath, 'wb') as f:
                    f.write(part.get_payload(decode=True))

                # Check if the attachment is a 'winmail.dat' file and handle it
                if sanitized_filename.lower() == "winmail.dat":
                    winmail_filepath = os.path.join(pdf_directory, sanitized_filename)

                    print("Winmail.dat file found..")
                    # Use 'tnefparse' to convert 'winmail.dat' to its correct format
                    command = ['tnefparse', '-p', pdf_directory, '-a', winmail_filepath]
                    print("File Downloaded: " + get_most_recent_file(current_directory))
                    subprocess.run(command)
                    time.sleep(2)
                    os.remove(winmail_filepath)  # Remove the original 'winmail.dat' file

                attachments_saved = True  # Set the flag to True if any supported attachment is saved

        return attachments_saved
    
    except Exception as e:
        print("Error trying to download attachment from email: ", e)
        
def is_supported_extension(filename, supported_extensions):
    """
    Check if the file extension of a given filename is in the list of supported extensions.

    Args:
        filename (str): The name of the file.
        supported_extensions (list): List of supported file extensions (e.g., ['.pdf', '.jpg']).

    Returns:
        bool: True if the file extension is supported, False otherwise.
    """
    file_extension = os.path.splitext(filename)[-1].lower()
    return file_extension in supported_extensions


def sanitize_filename(filename):
    """
    Sanitize a filename to remove or replace invalid characters for Windows.

    Args:
        filename (str): The original filename.

    Returns:
        str: The sanitized filename.
    """
    # Replace invalid characters with underscores
    invalid_characters = r'\/:*?"<>| '
    for char in invalid_characters:
        filename = filename.replace(char, '_')
    
    return filename



def get_most_recent_file(directory):
    pdf_directory = os.path.join(directory, "PDFs")

    # List all PDF files in the PDF's folder
    files = glob.glob(os.path.join(pdf_directory, '*'))

    if files:
        # Sort PDF files by modification time (most recent first)
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        most_recent_file = files[0]
        
        # Extract the root name (remove extension)
        most_recent_file_name, _ = os.path.splitext(os.path.basename(most_recent_file))
        
        return most_recent_file_name
    else:
        return None  # No PDF files found
    
def send_error_email(file_path, file_name):
    # Email configuration

    msg = MIMEMultipart()
    sender_email = email_user
    recipient_email = "sposada@rometransportation.com"
    smtp_server = "smtp.rometransportation.com"
    smtp_port = 587
    smtp_username = email_user
    smtp_password = email_pass

    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "Document Processing Error"

    # Email body
    body = f"The following file could not be processed: {file_name}"
    msg.attach(MIMEText(body, 'plain'))

    # Attach the problematic file
    with open(file_path, 'rb') as file:
        attachment = MIMEApplication(file.read(), _subtype="pdf")
        attachment.add_header('Content-Disposition', f'attachment; filename="{file_name}"')
        msg.attach(attachment)

    # Connect to the SMTP server and send the email
    try:
        print("Connecting to SMTP server...")
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        print("Connected to SMTP server.")
        server.starttls()
        print("Logged in to SMTP server...")
        server.login(smtp_username, smtp_password)
        print("Sending email...")
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {str(e)}")


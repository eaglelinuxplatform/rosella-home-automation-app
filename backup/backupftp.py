from ftplib import FTP
from security.encryption import *
import os
import zipfile
from firmware_mgnt.log_management import *


def create_directory_on_ftp(ftp_host, ftp_username, ftp_password, directory_path):
    """
    The function `create_directory_on_ftp` connects to an FTP server, checks if a directory exists, and
    creates the directory if it doesn't already exist.
    
    :param ftp_host: The FTP server host address or IP address
    :param ftp_username: The `ftp_username` parameter is the username used to authenticate with the FTP
    server. It is typically provided by the FTP server administrator or service provider
    :param ftp_password: The `ftp_password` parameter is the password used to authenticate the FTP user
    when connecting to the FTP server
    :param directory_path: The directory_path parameter is the path of the directory that you want to
    create on the FTP server. It should be a string representing the desired directory path, such as
    "/path/to/directory"
    """
    try:
        # Connect to the FTP server
        ftp = FTP(ftp_host)
        ftp.login(user=ftp_username, passwd=ftp_password)

        # Check if the directory already exists
        directory_exists = False
        try:
            ftp.cwd(directory_path)
            directory_exists = True
        except Exception as e:
            pass

        # Create the directory if it doesn't exist
        if not directory_exists:
            ftp.mkd(directory_path)
            log_debug(f"Directory '{directory_path}' created successfully on the FTP server.")
            log_event(f"Directory '{directory_path}' created successfully on the FTP server.")
            
        else:
            log_debug(f"Directory '{directory_path}' already exists on the FTP server.")
            log_event(f"Directory '{directory_path}' already exists on the FTP server.")
        # Close the FTP connection
        ftp.quit()

    except Exception as e:
        log_debug(f"An error occurred:{e}")
        log_event(e)

# # Example usage:
# ftp_host = "your_ftp_server.com"
# ftp_username = "your_ftp_username"
# ftp_password = "your_ftp_password"
# directory_path = "/path/to/new_directory"

# create_directory_on_ftp(ftp_host, ftp_username, ftp_password, directory_path)



def upload_file_to_cloud(host, username, password, local_file_path, remote_file_path,key,encrypted_file_path,filename):
    """
    The function `upload_file_to_cloud` uploads a file to a cloud server using FTP, encrypts the file,
    and logs any errors or exceptions that occur.
    
    :param host: The host parameter is the FTP server address or hostname where you want to upload the
    file. It could be an IP address or a domain name
    :param username: The username is the username used to authenticate with the FTP server. It is
    typically provided by the hosting provider or system administrator
    :param password: The password parameter is the password used to authenticate the FTP connection to
    the cloud server
    :param local_file_path: The local file path is the path to the file on your local machine that you
    want to upload to the cloud server. It should be a string that specifies the file's location,
    including the file name and extension. For example, "C:/Documents/myfile.txt" or
    "/home/user/files/image
    :param remote_file_path: The `remote_file_path` parameter is the path to the directory on the cloud
    server where you want to upload the file. For example, if you want to upload the file to a directory
    called "documents" on the cloud server, the `remote_file_path` would be "/documents"
    :param key: The "key" parameter is used for encryption. It is a cryptographic key that is used to
    encrypt the file before uploading it to the cloud server
    :param encrypted_file_path: The `encrypted_file_path` parameter is the path to the encrypted file
    that you want to upload to the cloud server. This file should be in binary format
    :param filename: The `filename` parameter is the name of the file that will be used when uploading
    the file to the cloud server
    """
    try:
        # Connect to the FTP server
        ftp = FTP(host)
        ftp.login(username, password)

        
        create_directory_on_ftp(host,username,password,remote_file_path)

        # Change to the desired directory on the cloud server
        ftp.cwd(remote_file_path)

        encrypt_file(local_file_path,key)
        log_debug("starting upload")
        # Open the local .db file in binary mode
        with open(encrypted_file_path, 'rb') as file:
            log_debug("uploading file")
            # Upload the file to the cloud server, overwriting if it already exists
            ftp.storbinary(f'STOR {filename}', file)
            os.remove(encrypted_file_path)
            log_debug("uploading done")

        # Close the FTP connection
        ftp.quit()
        log_debug(f"File '{local_file_path}' uploaded successfully to '{remote_file_path}' on the cloud server.")
        log_event(f"File '{local_file_path}' uploaded successfully to '{remote_file_path}' on the cloud server.")
    except Exception as e:
        log_debug(f"Error: {e}")
        log_exception(e)

# # Example usage:
# host = 'cloud.example.com'   # Replace with your cloud server's hostname or IP address
# username = 'your_username'   # Replace with your FTP username
# password = 'your_password'   # Replace with your FTP password
# local_file_path = 'local_file.db'   # Replace with the path to the local .db file you want to upload
# remote_file_path = 'remote_file.db' # Replace with the desired path on the cloud server

# upload_file_to_cloud(host, username, password, local_file_path, remote_file_path)


def download_ftp_file(ftp_server, ftp_username, ftp_password, ftp_directory, filename, local_file_path,key):
    """
    The function `download_ftp_file` connects to an FTP server, navigates to a specified directory,
    downloads a file, decrypts it using a provided key, and then deletes the downloaded file.
    
    :param ftp_server: The FTP server address or hostname
    :param ftp_username: The `ftp_username` parameter is the username used to authenticate with the FTP
    server. It is typically provided by the FTP server administrator or service provider
    :param ftp_password: The `ftp_password` parameter is the password used to authenticate and log in to
    the FTP server. It is required to establish a connection and access the files on the server
    :param ftp_directory: The `ftp_directory` parameter is the directory on the FTP server where the
    file is located. It specifies the path to the directory where the file is stored. For example, if
    the file is located in the "documents" directory on the FTP server, you would pass "/documents" as
    the value
    :param filename: The filename parameter is the name of the file that you want to download from the
    FTP server
    :param local_file_path: The local_file_path parameter is the path where you want to save the
    downloaded file on your local machine. It should be a string representing the file path, including
    the file name and extension. For example, "C:/Downloads/file.txt" or "/home/user/downloads/file.txt"
    :param key: The "key" parameter is used for decrypting the downloaded file. It is a cryptographic
    key that is required to decrypt the file after it has been downloaded from the FTP server
    """
    try:
        # Connect to the FTP server
        ftp = FTP(ftp_server)
        ftp.login(user=ftp_username, passwd=ftp_password)

        # Navigate to the specified directory (optional)

        ftp.cwd(ftp_directory)

        # Download the file
        # Download the file from the FTP server to a local file
        log_event("downloading..")
        with open(local_file_path, 'wb') as local_file:
            ftp.retrbinary('RETR ' + filename, local_file.write)
        log_event("done downloading.")
        decrypt_file(local_file_path,key)
        os.remove(local_file_path)
        

    except Exception as e:
        log_debug(f"An exception occurred:{e}")
        log_exception(e)

    finally:
        # Close the FTP connection
        ftp.quit()





# Usage example:
# ftp_server = 'ftp.example.com'
# ftp_username = 'your_ftp_username'
# ftp_password = 'your_ftp_password'
# ftp_directory = '/path/to/ftp/directory'
# filename = 'example_file.txt'
# local_filename = 'local_file.txt'

# download_ftp_file(ftp_server, ftp_username, ftp_password, ftp_directory, filename, local_filename,key)


def unzip_file(source_zip_path, destination_dir):
    """
    The `unzip_file` function extracts the contents of a ZIP file to a specified destination directory.
    
    :param source_zip_path: The path to the ZIP file that you want to unzip
    :param destination_dir: The destination directory is the directory where the contents of the ZIP
    file will be extracted to
    """
    try:
        
        # Ensure the destination directory exists
        os.makedirs(destination_dir, exist_ok=True)

        # Open the source ZIP file
        with zipfile.ZipFile(source_zip_path, 'r') as zip_file:
            # Extract all the contents of the ZIP file to the destination directory
            zip_file.extractall(destination_dir)
        
        log_debug(f"File '{source_zip_path}' was successfully extracted to '{destination_dir}'.")
        log_event(f"File '{source_zip_path}' was successfully extracted to '{destination_dir}'.")
    except Exception as e:
        log_debug(f"Error: {e}")
        log_exception(e)

# Example usage
# source_zip_path = '/path/to/source/file.zip'
# destination_dir = '/path/to/destination/'

# unzip_file(source_zip_path, destination_dir)


import base64
from firmware_mgnt.log_management import *
def save_base64_as_zip(base64_data, output_file_path):
    """
    The function `save_base64_as_zip` decodes a base64 string and saves it as a ZIP file.
    
    :param base64_data: The `base64_data` parameter is a string that represents the data encoded in
    Base64 format. This data can be any type of file, such as an image, a text file, or a ZIP file
    :param output_file_path: The output_file_path is the path where you want to save the backup ZIP
    file. It should be a string representing the file path, including the file name and extension. For
    example, "C:/backup.zip" or "/home/user/backup.zip"
    :return: a boolean value. It returns True if the base64 data is successfully decoded and saved as a
    ZIP file, and False if there is an error during the process.
    """
    try:
        # Decode Base64 data
        decoded_data = base64.b64decode(base64_data)

        # Save the decoded data to the output file
        with open(output_file_path, "wb") as file:
            file.write(decoded_data)

        log_debug(f"Backup ZIP file saved as {output_file_path}")
        log_event(f"Backup ZIP file saved as {output_file_path}")
        return True
    except Exception as e:
        log_debug(f"Error: {e}")
        log_exception(e)
        return False

# # Example usage:
# base64_data = "WklHQkVFMk1RVFQuUk9DS1M="
# output_file_path = "backup.zip"
# save_base64_as_zip(base64_data, output_file_path)



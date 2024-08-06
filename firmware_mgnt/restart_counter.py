from constant.databaseconstant import counter_file
from firmware_mgnt.log_management import *

def get_counter_value(file_path):
    """
    Get the current value of the counter from the file.

    Parameters:
        file_path (str): The path to the file containing the counter value.

    Returns:
        int: The current value of the counter.
    """
    try:
        with open(file_path, 'r') as file:
            return int(file.read())
    except FileNotFoundError:
        return 0

def increment_counter(file_path):
    """
    Increment the counter value and save it to the file.

    Parameters:
        file_path (str): The path to the file containing the counter value.

    Returns:
        None
    """
    try:
        current_value = get_counter_value(file_path)
        with open(file_path, 'w') as file:
            file.write(str(current_value + 1))
    except Exception as e:
        log_debug(f"An exception occurred:{e}")

# # Usage example
# if __name__ == "__main__":
#     counter_file = "counter.txt"
#     increment_counter(counter_file)
#     log_debug("Counter incremented.")


def start_count():
    try:
        
        increment_counter(counter_file)
        log_debug("Counter incremented.")
    except Exception as e:
        log_debug(f"An exception occurred:{e}")
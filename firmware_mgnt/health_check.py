import subprocess
import time
from firmware_mgnt.log_management import *

def is_service_running(service_name):
    """
    Check if a service with the given name is currently running.

    Parameters:
        service_name (str): The name of the service to check.

    Returns:
        bool: True if the service is running, False otherwise.
    """
    try:
        status = subprocess.check_output(["systemctl", "is-active", service_name]).decode().strip()
        return status == "active"
    except subprocess.CalledProcessError:
        return False

def check_services(services):
    """
    Monitor the specified services and set a flag if any service is not running.

    Parameters:
        services (list): List of service names to monitor.

    Returns:
        dict: A dictionary with service names as keys and corresponding flags (True or False) as values.
    """
    try:
        service_flags = {service: False for service in services}


        for service in services:
            if is_service_running(service):
                service_flags[service] = True
            else:
                service_flags[service] = False

            time.sleep(2)  # Adjust the sleep duration as needed

            # You can add any action here when a service is not running, such as sending an alert
            for service, is_running in service_flags.items():
                if not service:
                    log_debug(f"Service '{service}' is not running!")

            # You can also add logic here to break out of the loop under certain conditions

        return service_flags
    except Exception as e:
        log_debug(f"An exception occurred:{e}")

# Usage example
# if __name__ == "__main__":
#     services_to_monitor = ["mosquitto", "networking", "zigbee2mqtt"]
#     service_flags = check_services(services_to_monitor)
#     log_debug(service_flags)


def health_ok():
    services_to_monitor = ["mosquitto", "networking", "zigbee2mqtt"]
    service_flags = check_services(services_to_monitor)
    for services in services_to_monitor:
        # log_debug(f"{services}: {service_flags[services]}")
        if(service_flags[services] == True):
            return True
        else:
            return False




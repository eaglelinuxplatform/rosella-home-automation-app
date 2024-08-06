file_path= "/home/calixto_admin/glowfy_hub_app/dependencies/config/MAC_address/mac_address.txt"

try:
    # Read the content of the file
    with open(file_path, "r") as file:
        mac_address = file.read().strip()
        print("Read MAC Address:", mac_address)
except FileNotFoundError:
    print("MAC address file not found.")
except PermissionError:
    print("You do not have permission to read the MAC address file.")
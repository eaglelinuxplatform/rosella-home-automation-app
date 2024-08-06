import psutil

def get_network_connection_type():
    interfaces = psutil.net_if_stats()
    connection_type = None

    if 'eth0' in interfaces:
        eth0_stats = interfaces['eth0']
        if eth0_stats.isup:
            connection_type = 'Ethernet'

    elif 'wlan0' in interfaces:
        wlan0_stats = interfaces['wlan0']
        if wlan0_stats.isup:
            connection_type = 'Wi-Fi'

    return connection_type

# Example usage:
connection_type = get_network_connection_type()


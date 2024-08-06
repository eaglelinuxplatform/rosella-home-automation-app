from constant.mac_id import mac_address

#ftp server credentials
ftp_server = '142.93.210.213'
ftp_username = 'ftpuser'
ftp_password = 'Glowfy2023'

#FTP server folder paths for saving backup files
remote_gwy_folder = '/home/ftpuser/USER_BACKUP/{}'.format(mac_address)
remote_file_path_for_glowfydb ='/home/ftpuser/USER_BACKUP/{}/glowfy'.format(mac_address)
remote_file_path_for_devicedb = '/home/ftpuser/USER_BACKUP/{}/devices'.format(mac_address)
remote_file_path_for_zigbee2mqtt = '/home/ftpuser/USER_BACKUP/{}/zigbee2mqtt'.format(mac_address)

#Local file path for backup files
local_file_path_for_glowfydb_encrypted = '/home/calixto_admin/glowfy_hub_app/dependencies/data/glowfy_hub/glowfy.db.encrypted'
local_file_path_for_devicedb_encrypted ='/home/calixto_admin/glowfy_hub_app/dependencies/data/devices/device.db.encrypted'
local_file_path_for_z2mzip_encrypted ='/home/calixto_admin/glowfy_hub_app/dependencies/backup_with_timestamp/data.zip.encrypted'

#file path for device database(all devices types are stored in this database)
devicedb ='/home/calixto_admin/glowfy_hub_app/dependencies/data/devices/device.db' 

#Encryption key
key = b'CCSXrS6l4IAjo7wxBPMjXOSPPtNaGJa6HcGytl6Supo='

# local path for zigbee2mqtt
z2mzip = '/home/calixto_admin/glowfy_hub_app/dependencies/backup_with_timestamp/data.zip'
local_path_z2m_encrypted = '/home/calixto_admin/glowfy_hub_app/dependencies/backup_with_timestamp/data.zip.encrypted'




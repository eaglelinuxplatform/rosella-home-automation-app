import uuid
import os



def push_interval(min):

    #The function push_interval converts minutes to seconds.
    return min*60 
# specific time interval variables
cntl_dat_invl_sec = 30
cloud_push_interval = push_interval(360)
cloud_push_retry = int(6)


# control data variables
mac_address = ''.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                      for ele in range(0, 8 * 6, 8)][::-1])

old_fvr_store_var = ''
# glowfy_dev_id = mac_address
glowfy_dev_id = mac_address
glowfy_dev_typ = 'RSLLA000'
glowfy_hub_fvr = '02'
cntl_pln_urls = ['https://cloudapi.glowfy.in/controls/sync',
                 'https://cloudapi.glowfy.in/controls/auth']
https_headers = {'Content-type': 'application/json',
                 'Authorization': 'Bearer n8sKEFeJlYUFcioBWT6CHvX_WunfWbDyfw0kWPs'}
cntl_pln_auth_usr = "username"
cntl_pln_auth_pas = "password"
t_data = {"MTP": "03", "DTP": "RSLLA000", "DID": mac_address,
          "TSP": "1111111", "USR":cntl_pln_auth_usr , "PAS": cntl_pln_auth_pas, "FVR": glowfy_hub_fvr}
c_data = {"MTP": "01", "DTP": "RSLLA000", "DID": mac_address,
          "TSP": "45678888", "CDH": "00", "FVR": glowfy_hub_fvr}

# paths of partitions and marker files
partitions = ["partition_def", "partition_1", "partition_2"]
marker_file_paths = ('home/calixto_admin/glowfy_hub_app/partition_1/marker.txt',
                     'home/calixto_admin/glowfy_hub_app/partition_2/marker.txt')

#database filename and database file path
database_path = ''
database_filename = 'device.db'

# ftp server credentials and path
ftp_host = '142.93.210.213'
ftp_user = 'ftpuser'
ftp_pass = 'Glowfy2023'
ftp_file = glowfy_dev_typ + glowfy_hub_fvr + ".zip"
# should be like this './GlowFY/DMac/(DTP+FVR)'
# ftp_file_path = './GlowFY/RSLLA000/{}'.format(ftp_file)
ftp_file_path = './GlowFY/RSLLA000/'  #you can check this if there is an error in changing the directory
file_name, file_extension = os.path.splitext(ftp_file)
fvr_dir_name = file_name
upd_fvr_file = glowfy_dev_typ + glowfy_hub_fvr
cntl_pln_url_sel = [0]

cur_fvr_file = "gwymain"
new_marker_file = "./marker.txt"
checksum_sender_file = "./check_sum_value_sender.txt"
old_partition_index = ""
old_process_marker_file = ""

# latest added variables
#c_data_first_bit = c_data["CDH"][0]
#c_data_sec_bit = c_data["CDH"][1]

error_attempts = 3
retry_attempts = int(3)
retry_delay = int(6)
counter_file_path = "/home/calixto_admin/glowfy_hub_app/dependencies/config/counter/counter.txt"
firmware_version = "/home/calixto_admin/glowfy_hub_app/dependencies/config/version"

old_fvr_version = "01"
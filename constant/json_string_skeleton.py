from constant.mac_id import mac_address


json_string_ble = '{"MTP":"XXX","BLE":"XXX","NME":"XXXXXXXXXX"}'#json packet for start/stop ble advertising
json_string_reporting = '{"MTP":"XXX","STS":"XXX"}'#json packet for reporting gateway status
ready_json_string='{"MTP":"XXX"}'#message type packet to send stauscheck/poweroff/restart
wifi_sts_json = '{"status":"XXXX"}'#wifi status packet

z2m_rm_packet ='{"id": "XXXXX","force":true}' #zigbee2mqtt dev remove command
gwy_app_dev_info = '{"device_type":"XXXX","device_id":"XXXXXXX"}'#device type response packet to app
z2m_rename_packet = '{"from": "XXXXXX", "to": "XXXXX"}'#zigbee2mqtt device rename command
z2m_create_grp_packet ='{"friendly_name":"XXXXX", "id":"XXXXXX"}'#zigbee2mqtt create group command
create_grp_pkt ='{"data":{"type":"XXXXXX","group_name":"XXXXX"},"status":"XXX"}'#response packet for create group request
z2m_dev_grp_pkt ='{"group":"XXXXX","device":"XXXXXX"}' #packet format to add devices to a particular group
add_dev_to_grp_res_packet = '{"data":{"type":"XXXXXX","group_name":"XXXXXX","devices":["XXXXX","XXXX"]},"status":"XXX"}'# response for adding devices to group 
move_dev_to_grp_res_packet ='{"data":{"type":"XXXXXX","old_group":"XXXXXXX","new_group":"XXXXXX","devices":["XXXXX"]},"status":"XXX"}'#response for moving devices from onr group to other
control_pkt = '{"state":"XXXXXX"}'# state of group to set the state as ON/OFF
rename_grp_response_packet = '{"data":{"type":"XXXXXXX","old_name":"XXXXXXX","new_name":"XXXXXXX"},"status":"XXX"}'#device rename response packet to be send to app
save_dev_res_pkt='{"data":{"device_count":"XX","data":["XXXXXXX","YYYYYYYY"]},"status":"XXX"}'#response to be send to app for save_dev request
remove_rsponse_pkt ='{"data":{"device_id":"XXXXXXXX"},"status":"XXX"}'# response to be send to app after remove request
master_control_res_pkt = '{"data":{"group_name":"XXXXXXX","state":"XX"},"status":"XXX"}'# response to be send to app after master control request
replace_gateway_pkt ='{"data":{"type":"replace_gateway","user_name":"XXXXX","old_gateway_mac":"XXXXXXX"},"status":"XXX"}'
device_config_pkt = '{"id":"XXXXXX","options":"xxxxxxxx"}'
creat_flow_pkt = '{"type": "create_flow","name": "flow_name","conditions": "all_condition","source_count":1,"source": [ {"type":"manual_scene"} ] , "target_count": 1,"targets":[ {"type" : "smart_devices", "id" : "xxxxxxxxxxxx", "state_l1" : "on"} ] }'
dummy_response_pkt = '{"data":"XXXXX" ,"status":"ok"}'
gateway_info_pkt = '{"type":"gateway_info","connection_type":"XXX","new_fw_available":"true/false","current_fw_version":"XXXXXXX","new_fw_version":"YYYYYYYY"}'
push_notification_pkt = '{"type":"push_notification","message":""}'
#key
messagetype_key = "MTP"
Bluetooth_key = "BLE"
status_key = "STS"
SSID_key = "SID"
password_key = "PWD"
server_key ="SER"
port_key = "PRT"
mqtt_username_key = "USN"
mqtt_password = "UPD"
dev_name_key ="NME"
connection_type = "CTP"
#Key value
start_or_stop = "00"
status_pkt ="01"
config_param = "02"
status_check = "03"
restart_gwy = "04"
poweroff_gwy = "05"
report_pkt = "06"
dev_connected = "07"
gwy_ready = "08"
BLE_start ="START"
BLE_stop ="STOP"
working_fine ="00"
recived_config_pkt ="01"
error_in_config = "02"
Gateway_name = "GLOWFY-GWY-{}".format(mac_address)
recieved_ok ="00"
recived_error ="01"

#common key
okay ="ok"
error ="error"
connected ="connected"
not_connected ="not connected"


#mqtt json
type_key = "type"
check_online = "check_online"
status_key_mqtt ="status"
ok ="ok"
data_key ="data"
fail ="fail"
value_key ="value"
true ="true"
time_key ="time"
false ="false"

#zigbee2mqtt keys

device_interview = "device_interview"
successful="successful"
supported_key ="supported"
definiton_key ="definition"
model_key ="model"
vendor_key="vendor"
ieee_address_key ="ieee_address"
force_key ="force"
device_type_key = "device_type"
device_id_key ="device_id"

device_count_key ="device_count"
id_key ="id"
group_name_key ="group_name"
create_group ="create_group"
add_devices_key ="add_devices"
remove_devices_key ="remove_devices"
devices_key ="devices"
from_key ="from"
to_key ="to"
group_key ="group"
friendly_name_key ="friendly_name"
delete_group ="delete_group"
move_devices_key="move_devices"
old_group_key ="old_group"
new_group_key ="new_group"
state_key ="state"
rename_group_key ="rename_group"
old_name_key ="old_name"
new_name_key ="new_name"
replace_gateway = "replace_gateway"
user_name_key = "user_name"
old_gateway_mac_key = "old_gateway_mac"
zip_key = "zip"

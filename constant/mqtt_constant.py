from constant.mac_id import mac_address

# LOCAL_NAME = 'GlowFY/GWY-' + local_name


# Mqtt cloud broker credentials
username = "amazedoe"
password = "nice1234"


# MQTT topics


# Glowfy app topic
# Topic for requesting gateway status
sts_Req_Topic = "GlowFY/{}/request/gateway/status".format(mac_address)
# response topic for status response
sts_Res_Topic = "GlowFY/{}/response/gateway/status".format(mac_address)
# Topic for allowing new zigbee devices
permit_join_Req_Topic = "GlowFY/{}/request/permit_join".format(mac_address)
# response for permit_join
permit_join_Res_Topic = "GlowFY/{}/response/permit_join".format(mac_address)
# topic to publish device type and device_id
dev_join_Req_Topic = "GlowFY/{}/request/joined_devices".format(mac_address)
# response topic from the app for joined_devices
dev_join_Res_Topic = "GlowFY/{}/response/joined_devices".format(mac_address)
# request topic to save the devices
save_dev_Req_Topic = "GlowFY/{}/request/save_devices".format(mac_address)
# response topic for save device request
save_dev_Res_Topic = "GlowFY/{}/response/save_devices".format(mac_address)
# request topic to remove devices from zigbee network
remove_dev_Req_Topic = "GlowFY/{}/request/remove_devices".format(mac_address)
# response topic for remove devices
remove_dev_Res_Topic = "GlowFY/{}/response/remove_devices".format(mac_address)
# group operation request topic
create_grp_Req_Topic = "GlowFY/{}/request/group".format(mac_address)
# group operation response topic
create_grp_Res_Topic = "GlowFY/{}/response/group".format(mac_address)
# group master control topic
grp_master_control_Req_Topic = "GlowFY/{}/request/group/cmd".format(
    mac_address)
# group master control response topic
grp_master_control_Res_Topic = "GlowFY/{}/response/group/cmd".format(
    mac_address)
# replace gateway request topic
replace_Gwy_Req_Topic = "GlowFY/{}/request/gateway/cfg".format(mac_address)
# replace gateway response topic
replace_Gwy_Res_Topic = "GlowFY/{}/response/gateway/cfg".format(mac_address)
create_or_modify_flow_Topic = "GlowFY/{}/request/flow".format(mac_address)
gateway_info_Topic = "GlowFY/{}/request/gateway/get".format(mac_address)
gateway_fw_update_Topic = "GlowFY/{}/request/gateway/fw_update".format(
    mac_address)
gateway_push_notification_Topic = "GlowFY/{}/request/pushnotification".format(
    mac_address)
create_or_modify_flow_res_Topic = "GlowFY/{}/response/flow".format(mac_address)
gateway_info_res_Topic = "GlowFY/{}/response/gateway/info".format(mac_address)
gateway_fw_update_res_Topic = "GlowFY/{}/response/gateway/fw_update".format(
    mac_address)
gateway_push_notification_res_Topic = "GlowFY/{}/response/pushnotification".format(
    mac_address)


# zigbee2mqtt topic
# response for permit_join
permit_join_res_z2m = "GlowFY/{}/bridge/response/permit_join".format(
    mac_address)
# Topic for allowing new zigbee devices
permit_join_req_z2m = "GlowFY/{}/bridge/request/permit_join".format(
    mac_address)
# Topic to get information of joining device
z2m_dev_discovery = "GlowFY/{}/bridge/event".format(mac_address)
# topic to remove device from the network
z2m_dev_remove_req = "GlowFY/{}/bridge/request/device/remove".format(
    mac_address)
# response topic for remove request
z2m_dev_remove_res = "GlowFY/{}/bridge/response/device/remove".format(
    mac_address)
# create group topic
z2m_create_grp_req = "GlowFY/{}/bridge/request/group/add".format(mac_address)
# create group response topic
z2m_create_grp_res = "GlowFY/{}/bridge/response/group/add".format(mac_address)
# remove group topic
z2m_rm_grp_req = "GlowFY/{}/bridge/request/group/remove".format(mac_address)
# remove group response topic
z2m_rm_grp_res = "GlowFY/{}/bridge/response/group/remove".format(mac_address)
# add device to group topic
z2m_add_dev_to_grp_req = "GlowFY/{}/bridge/request/group/members/add".format(
    mac_address)
# add device to group response topic
z2m_add_dev_to_grp_res = "GlowFY/{}/bridge/response/group/members/add".format(
    mac_address)
# remove device from group topic
z2m_rm_dev_from_grp_req = "GlowFY/{}/bridge/request/group/members/remove".format(
    mac_address)
# remove device from group response topic
z2m_rm_dev_from_grp_res = "GlowFY/{}/bridge/response/group/members/remove".format(
    mac_address)
# device rename request topic
z2m_dev_rename_req = "GlowFY/{}/bridge/request/device/rename".format(
    mac_address)
# device rename response topic
z2m_dev_rename_res = "GlowFY/{}/bridge/response/device/rename".format(
    mac_address)
z2m_group_control = "GlowFY/{}/{}/set"  # group control topic
# group rename request topic
z2m_grp_rename_req = "GlowFY/{}/bridge/request/group/rename".format(
    mac_address)
# group rename response topic
z2m_grp_rename_res = "GlowFY/{}/bridge/response/group/rename".format(
    mac_address)
# topic to get the group status
group_sts_req = "GlowFY/{}/group/get".format(mac_address)
# zigbee2mqtt backup request topic
z2m_backup_req_topic = "GlowFY/{}/bridge/request/backup".format(mac_address)
# zigbee2mqtt backup response topic
z2m_backup_res_topic = "GlowFY/{}/bridge/response/backup".format(mac_address)
z2m_restart_service_topic = "GlowFY/{}/bridge/request/restart".format(
    mac_address)
z2m_device_conifig_topic = "GlowFY/{}/bridge/request/device/options".format(
    mac_address)
z2m_group_config_topic = "GlowFY/{}/bridge/request/group/options".format(
    mac_address)
z2m_info_topic = "GlowFY/{}/bridge/info".format(mac_address)





# MQTT local broker
broker_url = 'localhost'
broker_port = 1883

DEFAULT_MQTTSERVER = "3.7.206.26"
DEFAULT_MQTTPORT = "1883"


time_join = 180

group_id = 0
max_grp_value = 25

old_grp = ''
new_grp = ''
error_counter = 0
ok_counter = 0
rm_count = 0
dev_dict = {}

import json
import os
import socket
import subprocess
import time
import yaml
import shutil
import re
from constant.mqtt_constant import *
from constant.json_string_skeleton import *
from device_database.databsearch import db_search
from device_database.group_database import *
from constant.mac_id import mac_address
from peripherals.led import *
from backup.backupftp import *
from constant.ftpconstant import *
from constant.databaseconstant import glowfydb, devicedb, sensor_model_list, config_path_zigbee, multi_endpoint_list
from constant.ftpconstant import *
from backup.backupftp import *
from backup.decodebkp import save_base64_as_zip
from firmware_mgnt.factory_reset import update_mac
from protocols.network_check import connection_type
from scenes.scenes import create_or_modify_scenes,manual_scene_function,rename_scene,flow_info,scene_function
from constant.databaseconstant import *
from firmware_mgnt.gateway_management import *
from concurrent.futures import ThreadPoolExecutor
from threading import Thread


# from protocols.mqttcom import Q,client

dev_list = []
dev_temp_list = []
flag = False
save_rm = False
device_count = 0
save_dev = []
error_counter = 0
ok_counter = 0
rm_count = 0
dev_dict = {}
remove_dev_list = []
group_count = 0
master_grp_ctrl = False
grp_ctrl = False
join_list = []
interview_list = []
sensor_dev = []
counter = 0
dev_num = 0
old_grp = ''
new_grp = ''

node_normal_working()


# list comparison
def find_unmatching_elements(list1, list2):
    # Find elements in list1 that are not in list2
    unmatching_list1 = [x for x in list1 if x not in list2]

    # Find elements in list2 that are not in list1
    unmatching_list2 = [x for x in list2 if x not in list1]

    # Combine the unmatching elements from both lists
    unmatching_elements = unmatching_list1 + unmatching_list2

    return unmatching_elements


def dev_rename_with_state(input_string):
    # Find the index of "state_l" in the input string
    index = input_string.find("state_l")

    # If "state_l" is found, remove it and return the modified string
    if index != -1:
        modified_string = input_string[:index] + input_string[index + 7:]
        return modified_string
    else:
        return input_string


def add_state_l(input_string):
    # Find the index of the first "/" in the input string
    index = input_string.find("/")

    # If "/" is found, insert "state_l" after it and return the modified string
    if index != -1:
        modified_string = input_string[:index +
                                       1] + "state_l" + input_string[index + 1:]
        return modified_string
    else:
        return input_string  # If "/" is not found, return the original string


def is_connected():

    # The function checks if the device is connected to the internet by attempting to connect to a known host.

    try:
        # Attempt to connect to a known host
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False


def on_status(client, message):

    # The `on_status` function receives a message from a client, checks the status of the message, and publishes an updated JSON response based on the status.

    log_event("status check")
    status_check = message.payload.decode()
    log_debug(status_check)
    try:
        log_debug("packet identified")
        sts_pkt = json.loads(wifi_sts_json)
        data = json.loads(status_check)
        log_debug(data)
        type = data[type_key]
        if (type == check_online):
            try:
                sts_pkt.update({data_key: data})
                sts_pkt[status_key_mqtt] = ok
                updated_json = json.dumps(sts_pkt)
                client.publish(sts_Res_Topic, updated_json)
                log_event("Status Operational")
            except Exception as e:
                # handle the exception
                log_debug(f"1 An exception occurred:{e}")
                log_exception(e)

                # if(is_connected()):
                #     try:
                #         sts_pkt.update({data_key:data})
                #         sts_pkt [status_key_mqtt] = ok
                #         updated_json = json.dumps(sts_pkt)
                #         client.publish(sts_Res_Topic,updated_json)
                #         log_event("Status Online")
                #     except Exception as e:
                #         # handle the exception
                #         log_debug(f"1 An exception occurred:{e}")
                #         log_exception(e)
                # else:
                #     try:
                #         sts_pkt.update({data_key:data})
                #         sts_pkt [status_key_mqtt] = fail
                #         updated_json = json.dumps(sts_pkt)
                #         client.publish(sts_Res_Topic,updated_json)
                #         log_event("Status Offline")
                #     except Exception as e:
                #         # handle the exception
                #         log_debug(f"2 An exception occurred:{e}")
                #         log_exception(e)
    except Exception as e:
        # handle the exception
        log_debug("3 An exception occurred:", e)
        log_exception(e)


def on_permit_to_join_req(client, message):

    # The function `on_permit_to_join_req` handles a zigbee permit to join request by decoding the message payload, checking the value, and publishing a command based on the value to zigbee2mqtt service.

    global join_list
    global interview_list
    global dev_temp_list
    command = message.payload.decode()
    log_debug("join req")
    log_event("permit_join request")
    try:
        try:
            read_data = json.loads(command)
            log_debug(read_data)
            value = read_data[value_key]
            log_debug(value)
            if (value == True):
                log_debug("Zigbee network is getting ready to add devices")
                log_event("Zigbee network is getting ready to add devices")
                # read_data["time"]=180
                updated = json.dumps(read_data)
                # payload = json.dumps(command)
                client.publish(permit_join_req_z2m, updated)
            elif (value == False):

                client.publish(permit_join_req_z2m, command)
                log_debug("zigbee network is closing")
                log_event("zigbee network is closing")
                remove_list = find_unmatching_elements(
                    join_list, interview_list)
                log_debug(f"remove_list:{remove_list}")
                send_data = json.loads(z2m_rm_packet)
                for dev in remove_list:
                    print(f"devices to remove1:{remove_list}")
                    send_data[id_key] = dev
                    updated_json = json.dumps(send_data)
                    client.publish(z2m_dev_remove_req, updated_json)
                for dev in dev_temp_list:
                    print(f"devices to remove2:{dev_temp_list}")
                    send_data[id_key] = dev
                    updated_json = json.dumps(send_data)
                    client.publish(z2m_dev_remove_req, updated_json)

                join_list = []
                interview_list = []
                dev_temp_list = []
        except Exception as e:
            # handle the exception
            log_debug(f"7 An exception occurred:{e}")
            log_exception(e)
    except Exception as e:
        # handle the exception
        log_debug(f"8 An exception occurred:{e}")
        log_exception(e)


def on_permit_to_join_res(client, message):

    # The function `on_permit_to_join_res` receives a message from a client, decodes the payload,
    # it reads the response from zigbee2mqtt service and send custom response for the app.

    log_event("permit_join response")
    command = message.payload.decode()
    try:
        read_data = json.loads(command)
        log_debug(read_data)

        status = read_data[status_key_mqtt]
        try:
            if (status == ok):

                data = read_data[data_key]
                log_debug(data)

                # log_debug(inside_packet)
                inside_value = data[value_key]

                if (inside_value == True):
                    log_debug("success")
                    try:
                        node_pairing_mode()
                        log_event("network is open")
                        client.publish(permit_join_Res_Topic, command)
                    except Exception as e:
                        # handle the exception
                        log_debug(f"9 An exception occurred:{e}")
                        log_exception(e)
                elif (inside_value == False):
                    try:
                        node_normal_working()
                        log_event("permit join closed")
                        client.publish(permit_join_Res_Topic, command)
                    except Exception as e:
                        # handle the exception
                        log_debug(f"10 An exception occurred:{e}")
                        log_exception(e)
            else:
                log_debug("failed")
        except Exception as e:
            # handle the exception
            log_debug(f"11 An exception occurred:{e}")
            log_exception(e)

    except Exception as e:
        # handle the exception
        log_debug(f"12 An exception occurred:{e}")
        log_exception(e)


def on_dev_rm_req(client, message):

    # The function `on_dev_rm_req` receives a message, extracts a device ID from the message payload, and
    # publishes a new message with the device ID to a device remove zigbee2mqtt topic.

    log_event("removing devices")
    command = message.payload.decode()
    log_debug(command)
    try:
        read_data = json.loads(command)
        device_id = read_data[device_id_key]
        with open(config_path_zigbee, 'r') as f:
            data = yaml.safe_load(f)
        # Print the values as a dictionary

        for group_id, group_data in data.get('groups', {}).items():
            friendly_name = group_data.get('friendly_name', '')
            devices = group_data.get('devices', [])
            for dev in devices:
                log_debug(friendly_name)
                log_debug(devices)
                condition_1 = "/" in dev
                if condition_1 is True:
                    new_dev = dev[2:-2]

                else:
                    new_dev = dev[2:]

                print(f"new_dev: {new_dev}")

                if device_id == new_dev:
                    grp_rm = json.loads(z2m_dev_grp_pkt)
                    grp_rm[group_key] = friendly_name
                    grp_rm["device"] = dev
                    grp_rm_update = json.dumps(grp_rm)
                    log_debug(f"remove_from_group:{grp_rm_update}")
                    client.publish(z2m_rm_dev_from_grp_req, grp_rm_update)
                    device_to_remove = new_dev
                else:
                    device_to_remove = device_id

        send_data = json.loads(z2m_rm_packet)
        send_data[id_key] = device_to_remove
        updated_json = json.dumps(send_data)
        client.publish(z2m_dev_remove_req, updated_json)

    except Exception as e:
        # handle the exception
        log_debug(f"12 An exception occurred:{e}")
        log_exception(e)


def on_joined_dev_req(client, message):

    # The function `on_joined_dev_req` handles incoming messages related to device joining and device
    # interviews in a home automation system.

    global dev_temp_list
    global dev_dict
    global join_list
    global interview_list

    command = message.payload.decode()
    log_debug(command)

    try:
        read_data = json.loads(command)
        log_debug(read_data)
        type = read_data[type_key]
        data = read_data[data_key]

        if (type == "device_joined"):
            ieee_address = data[ieee_address_key]
            join_list.append(ieee_address)

        elif (type == device_interview):
            status = data[status_key_mqtt]
            if (status == successful):
                supported = data[supported_key]
                definition = data[definiton_key]
                ieee_address = data[ieee_address_key]
                interview_list.append(ieee_address)
                model = definition[model_key]
                vendor = definition[vendor_key]
                if (supported == True):
                    new_name = ieee_address.replace("0x", "")
                    dev_temp_list.append(new_name)
                    log_event(f"{new_name} joined")
                    try:
                        send_cmd = json.loads(z2m_rename_packet)
                        send_cmd[from_key] = ieee_address
                        send_cmd[to_key] = new_name
                        updated_json_1 = json.dumps(send_cmd)
                        log_debug(updated_json_1)
                        client.publish(z2m_dev_rename_req, updated_json_1)
                    except Exception as e:
                        # handle the exception
                        log_debug(f"14 An exception occurred:{e}")
                        log_exception(e)

                    try:

                        device_type, vendorname = db_search(model, devicedb)
                        filename = "device.db.encrypted"
                        # remote_path = remote_file_path_for_devicedb.format(mac_address)
                        upload_file_to_cloud(ftp_server, ftp_username, ftp_password, devicedb,
                                             remote_file_path_for_devicedb, key, local_file_path_for_devicedb_encrypted, filename)

                        dev_dict[new_name] = device_type
                        option_2_endpoint = '{"filtered_cache":["state_l1","state_l2"]}'
                        option_3_endpoint = '{"filtered_cache":["state_l1","state_l2",,"state_l3"]}'
                        option_4_endpoint = '{"filtered_cache":["state_l1","state_l2","state_l3","state_l4"]}'
                        option_5_endpoint = '{"filtered_cache":["state_l1","state_l2","state_l3","state_l4","state_l5"]}'

                        if device_type in multi_endpoint_list:
                            config_data = json.loads(device_config_pkt)
                            if device_type.startswith("2"):
                                option_json = json.loads(option_2_endpoint)
                            elif device_type.startswith("3"):
                                option_json = json.loads(option_3_endpoint)
                            elif device_type.startswith("4"):
                                option_json = json.loads(option_4_endpoint) 
                            elif device_type.startswith("5"):
                                option_json = json.loads(option_5_endpoint)
                            config_data[id_key] = new_name
                            config_data["options"] = option_json
                            updated_conf = json.dumps(config_data)
                            log_debug(f"config:{updated_conf}")
                            client.publish(
                                z2m_device_conifig_topic, updated_conf)
                        else:
                            pass

                        # if len(device_type)!= 0:
                        #     pass
                        # else:
                        #     send_data = json.loads(z2m_rm_packet)
                        #     send_data[id_key]= ieee_address
                        #     send_data[force_key]= False
                        #     updated_json = json.dumps(send_data)
                        #     log_debug(updated_json)
                        #     client.publish(z2m_dev_remove_req,updated_json)

                    except Exception as e:
                        # handle the exception
                        log_debug(f"15 An exception occurred:{e}")
                        log_exception(e)
                        try:
                            rm_cmd = json.loads(z2m_rm_packet)
                            rm_cmd[id_key] = ieee_address
                            updated_cmd = json.dumps(rm_cmd)
                            client.publish(z2m_dev_remove_req, updated_cmd)
                        except Exception as e:
                            # handle the exception
                            log_debug(f" An exception occurred:{e}")
                            log_exception(e)

                    try:
                        send_data = json.loads(gwy_app_dev_info)
                        send_data[device_type_key] = device_type
                        send_data[device_id_key] = new_name
                        updated_json = json.dumps(send_data)
                        log_debug(updated_json)
                        client.publish(dev_join_Req_Topic, updated_json)
                    except Exception as e:
                        # handle the exception
                        log_debug(f"16 An exception occurred:{e}")
                        log_exception(e)
                elif (supported == False):
                    send_data = json.loads(z2m_rm_packet)
                    send_data[id_key] = ieee_address
                    send_data[force_key] = True
                    updated_json = json.dumps(send_data)
                    log_debug(updated_json)
                    client.publish(z2m_dev_remove_req, updated_json)
    except Exception as e:
        # handle the exception
        log_debug(f"17 An exception occurred:{e}")
        log_exception(e)


def on_join_dev_res(client, message):

    # The function `on_join_dev_res` handles the event when a device joins a network and log_debugs the joined
    # device's data if the status is "ok".
    log_event("joined device response")
    command = message.payload.decode()
    try:
        read_data = json.loads(command)
        data = read_data[data_key]
        log_debug(data)
        status = read_data[status_key_mqtt]
        if status == ok:
            log_debug("device joined successfully")
    except Exception as e:
        # handle the exception
        log_debug(f"18 An exception occurred:{e}")
        log_exception(e)


def on_dev_save_req(client, message):

    # The function `on_dev_save_req` handles the saving and removal of devices in a home automation
    # system, including updating the device list, publishing MQTT messages, and storing data in a
    # database.

    global save_rm
    global rm_count
    global save_dev
    global dev_dict
    global dev_temp_list
    command = message.payload.decode()

    try:
        read_data = json.loads(command)
        device_count = read_data[device_count_key]
        data = read_data[data_key]
        save_dev = data
        log_debug("dev_data :{}".format(data))
        send_data1 = json.loads(z2m_rm_packet)
        log_debug("device_list:{}".format(dev_temp_list))
        values_to_remove = data
        updated_list = [x for x in dev_temp_list if x not in data]
        rm_count = len(updated_list)
        log_debug("updated_list:{}".format(updated_list))
        log_debug("dev_dict:{}".format(dev_dict))
        if (rm_count != 0):
            for value in updated_list:
                send_data1[id_key] = value
                updated_json = json.dumps(send_data1)
                log_debug(updated_json)
                client.publish(z2m_dev_remove_req, updated_json)
                save_rm = True

        send_data = json.loads(save_dev_res_pkt)
        res_data = send_data[data_key]
        res_data[device_count_key] = device_count
        res_data[data_key] = save_dev
        log_debug(save_dev)
        send_data[status_key_mqtt] = ok
        updated_json = json.dumps(send_data)
        log_debug(updated_json)
        client.publish(save_dev_Res_Topic, updated_json)
        log_event(f"{save_dev} saved")
        table_name = "devices"
        columns = ["device_id", "device_type"]
        database_name = glowfydb
        for dev in save_dev:
            log_debug("inside the for loop")
            data_db = [(dev, dev_dict[dev])]
            log_debug("data_db:{}".format(data_db))
            create_table_and_insert_data(
                database_name, table_name, columns, data_db)


        dev_dict = {}
        print("above dev temp list savedev")
        dev_temp_list = []
        save_rm = False
        node_normal_working()
        client.publish(z2m_backup_req_topic, '{""}')
        filename = "glowfy.db.encrypted"
        # remote_path = remote_file_path_for_glowfydb.format(mac_address)
        upload_file_to_cloud(ftp_server, ftp_username, ftp_password, glowfydb,
                             remote_file_path_for_glowfydb, key, local_file_path_for_glowfydb_encrypted, filename)

    except Exception as e:
        # handle the exception
        log_debug(f"An exception occurred:{e}")
        log_exception(e)


def on_dev_rm_res(client, message):

    # The function `on_dev_rm_res` handles the response received after removing a device, updates the
    # database accordingly, and performs additional actions based on the status of the removal process.

    global counter
    global dev_list
    global save_rm
    global error_counter
    global ok_counter

    global remove_dev_list
    command = message.payload.decode()
    log_debug(command)
    try:
        read_data = json.loads(command)
        status = read_data[status_key_mqtt]
        data = read_data[data_key]
        if (status == ok and save_rm == False):
            log_debug("inside normal remove")
            device_id = data[id_key]
            send_data = json.loads(remove_rsponse_pkt)
            data_res = send_data[data_key]
            data_res[device_id_key] = device_id
            send_data[status_key_mqtt] = status
            updated_json = json.dumps(send_data)
            log_debug(updated_json)
            client.publish(remove_dev_Res_Topic, updated_json)
            log_event(f"{device_id} removed")
            table_name = 'devices'
            column_name = 'device_id'
            value = device_id
            database_name = glowfydb
            remove_row_by_value(table_name, column_name, value, database_name)
            filename = "glowfy.db.encrypted"
            # remote_path = remote_file_path_for_glowfydb.format(mac_address)
            upload_file_to_cloud(ftp_server, ftp_username, ftp_password, glowfydb,
                                 remote_file_path_for_glowfydb, key, local_file_path_for_glowfydb_encrypted, filename)

            client.publish(z2m_backup_req_topic, '{""}')

        elif (status == ok and save_rm == True):
            log_debug("inside the save loop")
            ok_counter += 1
            

            device = data[id_key]
            remove_dev_list.append(device)

        elif (status == error and save_rm == True):
            log_debug("save error loop")
            try:
                error_counter += 1
                device = data[id_key]
                dev_list.append(device)


            except Exception as e:
                # handle the exception
                log_debug(f"An exception occurred:{e}")
                log_exception(e)

        elif (status == "error" and save_rm == False):
            log_debug("error loop")
            pattern = pattern = r"Device '([^']+)' does not exist"
            if "does not exist" in read_data[error]:
                match = re.search(pattern, read_data[error])
                if match:
                    device_name = match.group(1)
                    send_data = json.loads(remove_rsponse_pkt)
                    data_res = send_data[data_key]
                    data_res[device_id_key] = device_name
                    send_data[status_key_mqtt] = 'ok'
                    updated_json = json.dumps(send_data)
                    log_debug(updated_json)
                    client.publish(remove_dev_Res_Topic, updated_json)

        if ((ok_counter + error_counter) == rm_count):
            if (ok_counter > 0):
                log_debug("inside db create function")
                dev_list = []

            

    except Exception as e:
        # handle the exception
        log_debug(f"An exception occurred:{e}")
        log_exception(e)


def dev_status(client, message):
    command = message.payload.decode()
    try:
        read_data = json.loads(command)
        log_debug(read_data)
    except Exception as e:
        # handle the exception
        log_debug(f"An exception occurred:{e}")
        log_exception(e)


def on_grp_req(client, message):

    # The function `on_grp_req` handles different types of group requests, such as creating a group,
    # deleting a group, adding devices to a group, removing devices from a group, moving devices between
    # groups, and renaming a group.

    global counter
    global dev_num
    global flag
    global old_grp
    global new_grp
    global sensor_dev
    global end_dev
    command = message.payload.decode()

    try:
        try:
            read_data = json.loads(command)
            log_debug(read_data)
            type = read_data[type_key]
            log_debug(type)
            if (type == create_group):
                grp_name = read_data[group_name_key]
                group_id = 0
                column_name = "id"
                table_name = "group_table"
                database_name = glowfydb
                try:
                    group_id = find_highest_value(
                        table_name, database_name, column_name)
                    log_debug("groupid:{}".format(group_id))

                    log_debug("inside try")
                    group_id += 1
                    log_debug(group_id)
                    if (group_id > max_grp_value):
                        log_debug("maxvalue reached")
                        log_event("maxvalue reached")
                        group_id = 1
                except Exception as e:
                    # handle the exception
                    log_debug(f"An exception occurred:{e}")
                    log_exception(e)
                    group_id = 1

                if (group_id > max_grp_value):
                    log_debug("inside id and value compare")
                    index_column = "id"
                    index_values = search_index_column(
                        table_name, index_column, database_name)
                    random = 0
                    for values in index_values:
                        log_debug("inside for")
                        random += 1
                        log_debug(random)
                        if (random != values):
                            log_debug("inside if inside for")
                            group_id = random
                            log_debug(group_id)
                            break
                        else:
                            continue

                grp_data = json.loads(z2m_create_grp_packet)
                grp_data[friendly_name_key] = grp_name
                grp_data[id_key] = group_id
                updated_json = json.dumps(grp_data)
                client.publish(z2m_create_grp_req, updated_json)

            elif (type == delete_group):
                dev_num = 0
                grp_name = read_data[group_name_key]
                grp_data = json.loads(z2m_rm_packet)
                grp_data[id_key] = grp_name
                updated_json = json.dumps(grp_data)
                client.publish(z2m_rm_grp_req, updated_json)
            elif (type == add_devices_key):
                dev_num = 0

                grp_name = read_data[group_name_key]
                devices = read_data[devices_key]
                log_debug(devices)
                dev_num = len(devices)
                log_debug("dev_num:{}".format(dev_num))
                grp_data = json.loads(z2m_dev_grp_pkt)
                database_path = glowfydb
                tablename = "devices"
                col_1 = "device_id"
                col_2 = "device_type"

                end_dev = []
                sensor_dev = []
                for device in devices:
                    col_1_value = device
                    dev_model = retrieve_value(
                        database_path, tablename, col_1, col_2, col_1_value)
                    if dev_model in sensor_model_list:
                        log_debug("sensor")
                        sensor_dev.append(device)
                    else:
                        end_dev.append(device)
                if end_dev:
                    log_debug("end dev is not empty")
                    log_debug(f"end_device:{end_dev}")
                    log_debug(f"sensor_device:{sensor_dev}")
                    grp_data[group_key] = grp_name
                    for dev in end_dev:
                        modified_dev = dev_rename_with_state(dev)
                        grp_data["device"] = modified_dev
                        updated_json = json.dumps(grp_data)
                        log_debug(updated_json)
                        client.publish(z2m_add_dev_to_grp_req, updated_json)
                elif sensor_dev:
                    log_debug("in elif")
                    res = json.loads(add_dev_to_grp_res_packet)
                    data = res[data_key]
                    data[type_key] = type
                    data[group_name_key] = grp_name
                    data[devices_key] = sensor_dev
                    res[status_key_mqtt] = okay
                    updated = json.dumps(res)
                    log_debug(updated)
                    client.publish(create_grp_Res_Topic, updated)
                    sensor_dev = []
                    counter = 0
            elif (type == remove_devices_key):

                grp_name = read_data[group_name_key]
                devices = read_data[devices_key]
                grp_data = json.loads(z2m_dev_grp_pkt)
                grp_data[group_key] = grp_name
                dev_num = len(devices)
                database_path = glowfydb
                tablename = "devices"
                col_1 = "device_id"
                col_2 = "device_type"

                end_dev = []
                sensor_dev = []
                for device in devices:
                    col_1_value = device
                    dev_model = retrieve_value(
                        database_path, tablename, col_1, col_2, col_1_value)
                    if dev_model in sensor_model_list:
                        log_debug("sensor")
                        sensor_dev.append(device)
                    else:
                        end_dev.append(device)
                if sensor_dev:
                    log_debug("in elif")
                    res = json.loads(add_dev_to_grp_res_packet)
                    data = res[data_key]
                    data[type_key] = type
                    data[group_name_key] = grp_name
                    data[devices_key] = sensor_dev
                    res[status_key_mqtt] = okay
                    updated = json.dumps(res)
                    log_debug(updated)
                    client.publish(create_grp_Res_Topic, updated)
                    sensor_dev = []
                log_debug(dev_num)
                for device in end_dev:
                    modified_dev = dev_rename_with_state(device)
                    grp_data["device"] = modified_dev
                    updated_json = json.dumps(grp_data)
                    client.publish(z2m_rm_dev_from_grp_req, updated_json)
                counter = 0
                end_dev = []
            elif (type == move_devices_key):
                old_grp = read_data[old_group_key]
                new_grp = read_data[new_group_key]
                # removing from old group
                grp_name = read_data[old_group_key]
                devices = read_data[devices_key]
                grp_data = json.loads(z2m_dev_grp_pkt)
                grp_data[group_key] = grp_name
                dev_num = len(devices)
                database_path = glowfydb
                tablename = "devices"
                col_1 = "device_id"
                col_2 = "device_type"

                end_dev = []
                sensor_dev = []
                for device in devices:
                    col_1_value = device
                    dev_model = retrieve_value(
                        database_path, tablename, col_1, col_2, col_1_value)
                    if dev_model in sensor_model_list:
                        log_debug("sensor")
                        sensor_dev.append(device)
                    else:
                        end_dev.append(device)
                if sensor_dev:
                    log_debug("in elif")
                    res = json.loads(move_dev_to_grp_res_packet)
                    data = res[data_key]
                    data[type_key] = type
                    data[old_group_key] = old_grp
                    data[new_group_key] = new_grp
                    data[devices_key] = sensor_dev
                    res[status_key_mqtt] = okay
                    updated = json.dumps(res)
                    log_debug(updated)
                    client.publish(create_grp_Res_Topic, updated)
                    sensor_dev = []

                for device in end_dev:
                    modified_dev = dev_rename_with_state(device)
                    grp_data["device"] = modified_dev
                    updated_json = json.dumps(grp_data)
                    log_debug("remove command")
                    log_debug(updated_json)
                    client.publish(z2m_rm_dev_from_grp_req, updated_json)
                if end_dev:
                    flag = True
                    end_dev = []
                log_debug(f"move device flag:{flag}")
            elif (type == rename_group_key):
                old_name = read_data[old_name_key]
                new_name = read_data[new_name_key]
                grp_data = json.loads(z2m_rename_packet)
                grp_data[from_key] = old_name
                grp_data[to_key] = new_name
                updated_json = json.dumps(grp_data)
                client.publish(z2m_grp_rename_req, updated_json)
        except Exception as e:
            # handle the exception
            log_debug(f"An exception occurred:{e}")
            log_exception(e)
    except Exception as e:
        # handle the exception
        log_debug(f"An exception occurred:{e}")
        log_exception(e)


def on_create_grp_res(client, message):

    # The above code defines two functions, `on_create_grp_res` and `on_rm_grp_res`, which handle MQTT
    # messages related to creating and removing groups respectively.

    command = message.payload.decode()
    try:

        read_data = json.loads(command)
        log_debug(read_data)
        status = read_data[status_key_mqtt]

        if (status == ok):
            data = read_data[data_key]
            grp_id = data[id_key]
            grp_name = data[friendly_name_key]
            database_name = glowfydb
            table_name = "group_table"
            columns = ["id", "friendly_name", "status"]
            data = [(grp_id, grp_name, 'active')]
            create_table_and_insert_data(
                database_name, table_name, columns, data)
            filename = "glowfy.db.encrypted"
            send_data = json.loads(create_grp_pkt)
            data_res = send_data[data_key]
            data_res[type_key] = create_group
            data_res[group_name_key] = grp_name
            send_data[status_key_mqtt] = status
            updated_json = json.dumps(send_data)
            client.publish(create_grp_Res_Topic, updated_json)
            option = '{"optimistic":false}'
            option_json = json.loads(option)
            grp_config = json.loads(device_config_pkt)
            grp_config[id_key] = grp_name
            grp_config["options"] = option_json
            updated = json.dumps(grp_config)
            log_debug(updated)
            client.publish(z2m_group_config_topic, updated)

            grp_config[id_key] = grp_name

            upload_file_to_cloud(ftp_server, ftp_username, ftp_password, glowfydb,
                                 remote_file_path_for_glowfydb, key, local_file_path_for_glowfydb_encrypted, filename)
            client.publish(z2m_backup_req_topic, '{""}')
            log_event(f"{grp_name} is created")
        elif (status == error):
            data = read_data[data_key]
            if read_data['error'].endswith("is already in use"):
                pattern = r"'(.*?)'"

                # Search for the pattern in the message
                match = re.search(pattern, read_data['error'])

                # Extract the text if found
                if match:
                    extracted_text = match.group(1)
                
                send_data = json.loads(create_grp_pkt)
                data_res = send_data[data_key]
                data_res[type_key] = create_group
                data_res[group_name_key] = extracted_text
                send_data[status_key_mqtt] = 'ok'
                updated_json = json.dumps(send_data)
                client.publish(create_grp_Res_Topic, updated_json)
            try:
                grp_id = data[id_key]

                grp_name = data[friendly_name_key]

                send_data = json.loads(create_grp_pkt)
                data_res = send_data[data_key]
                data_res[type_key] = create_group
                data_res[group_name_key] = grp_name
                send_data[status_key_mqtt] = status
                updated_json = json.dumps(send_data)
                log_event(f"{grp_name} creation failed")
                client.publish(create_grp_Res_Topic, updated_json)
            except Exception as e:
                # handle the exception

                log_debug(f"An exception occurred:{e}")
                log_exception(e)
            pass
    except Exception as e:
        # handle the exception
        log_debug(f"An exception occurred:{e}")
        log_exception(e)


def on_rm_grp_res(client, message):

    # The function `on_rm_grp_res` handles the response received after removing a group and performs
    # various operations based on the status of the response.

    command = message.payload.decode()
    try:
        read_data = json.loads(command)
        log_debug(read_data)
        status = read_data[status_key_mqtt]
        data = read_data[data_key]
        if (status == ok):
            try:
                id = data[id_key]
                database_name = glowfydb
                table_name = "group_table"
                coloumn_name = "friendly_name"
                remove_row_by_value(
                    table_name, coloumn_name, id, database_name)
                filename = "glowfy.db.encrypted"
                # remote_path = remote_file_path_for_glowfydb.format(mac_address)
                send_data = json.loads(create_grp_pkt)
                data_res = send_data[data_key]
                data_res[type_key] = delete_group
                data_res[group_name_key] = id
                send_data[status_key_mqtt] = status
                updated_json = json.dumps(send_data)
                client.publish(create_grp_Res_Topic, updated_json)
                upload_file_to_cloud(ftp_server, ftp_username, ftp_password, glowfydb,
                                     remote_file_path_for_glowfydb, key, local_file_path_for_glowfydb_encrypted, filename)
                client.publish(z2m_backup_req_topic, '{""}')
                log_event(f"{id} removed")
            except Exception as e:
                # handle the exception
                log_debug(f"An exception occurred:{e}")
                log_exception(e)
        elif(status == error):
            pattern = pattern = r"Group '([^']+)' does not exist"
            if "does not exist" in read_data[error]:
                match = re.search(pattern, read_data[error])
                if match:
                    group_name = match.group(1)
                    send_data = json.loads(create_grp_pkt)
                    data_res = send_data[data_key]
                    data_res[type_key] = delete_group
                    data_res[group_name_key] = group_name
                    send_data[status_key_mqtt] = 'ok'
                    updated_json = json.dumps(send_data)
                    client.publish(create_grp_Res_Topic, updated_json)
                
                 

        else:
            try:
                id = data[id_key]
                send_data = json.loads(create_grp_pkt)
                data_res = send_data[data_key]
                data_res[type_key] = delete_group
                data_res[group_name_key] = id
                send_data[status_key_mqtt] = status
                updated_json = json.dumps(send_data)
                client.publish(create_grp_Res_Topic, updated_json)
                log_event(f"failed to remove {id}")
            except Exception as e:
                # handle the exception
                log_debug(f"An exception occurred:{e}")
                log_exception(e)

    except Exception as e:
        # handle the exception
        log_debug(f"An exception occurred:{e}")
        log_exception(e)


def on_add_dev_to_grp_res(client, message):

    # The function `on_add_dev_to_grp_res` handles the response received after adding devices to a group
    # in an MQTT client.

    global counter
    global dev_list
    global flag  # move_device_flag
    global sensor_dev
    global dev_num
    global end_dev
    command = message.payload.decode()
    try:

        read_data = json.loads(command)
        log_debug(read_data)

        data = read_data[data_key]
        group = data[group_key]

        status = read_data[status_key_mqtt]
        if (status == ok and flag == False):

            # send_data = json.loads(add_dev_to_grp_req_packet)
            # data_res=send_data[data_key]
            # data_res[type_key]= add_devices_key
            # data_res[group_name_key] = group
            # counter += 1
            counter = 1
            device = data["device"]
            log_debug(f"device_list:{dev_list}")
            device_mod = add_state_l(device)
            log_debug(device_mod)
            dev_list.append(device_mod)
            log_debug(dev_list)
            log_debug("counter{}".format(counter))
            log_debug("dev_num ={}".format(dev_num))

            if (counter == dev_num):
                log_debug("inside normal")
                if end_dev:
                    send_data = json.loads(add_dev_to_grp_res_packet)
                    data_res = send_data[data_key]
                    data_res[type_key] = add_devices_key
                    data_res[group_name_key] = group
                    data_res[devices_key] = dev_list
                    send_data[status_key_mqtt] = status
                    log_debug(send_data)
                    updated_json = json.dumps(send_data)
                    client.publish(create_grp_Res_Topic, updated_json)
                    log_event(f"{dev_list} added to group {group}")
                    counter = 0
                    log_debug(counter)
                    dev_list = []
                    end_dev = []
                elif sensor_dev:
                    send_data = json.loads(add_dev_to_grp_res_packet)
                    data_res = send_data[data_key]
                    data_res[type_key] = add_devices_key
                    data_res[group_name_key] = group
                    new_list = dev_list+end_dev
                    data_res[devices_key] = new_list

                    send_data[status_key_mqtt] = status
                    log_debug(send_data)
                    updated_json = json.dumps(send_data)
                    client.publish(create_grp_Res_Topic, updated_json)
                    log_event(f"{new_list} added to group {group}")
                    counter = 0
                    dev_list = []
                    sensor_dev = []
                    end_dev = []
        elif (status == error and flag == False):

            # counter +=1
            counter = 1
            device = data["device"]
            device_mod = add_state_l(device)
            dev_list.append(device_mod)
            log_debug(dev_list)
            if (counter == dev_num):
                send_data = json.loads(add_dev_to_grp_res_packet)
                data_res = send_data[data_key]
                data_res[type_key] = add_devices_key
                data_res[group_name_key] = group
                data_res[devices_key] = dev_list
                send_data[status_key_mqtt] = status
                log_debug(send_data)
                while True:
                    try:
                        updated_json = json.dumps(send_data)
                        break
                    except Exception as e:
                        # handle the exception
                        log_debug(f"An exception occurred:{e}")
                        continue

                client.publish(create_grp_Res_Topic, updated_json)
                log_event(f"failed to add {dev_list} to group{group}")
                counter = 0
                dev_list = []
        if (status == ok and flag == True):
            log_debug("inside second if")
            log_debug(counter)
            # counter +=1
            counter = 1
            device = data["device"]
            log_debug(device)
            device_mod = add_state_l(device)
            dev_list.append(device_mod)
            log_debug(dev_list)
            log_debug("counter ={}".format(counter))
            log_debug("dev_num ={}".format(dev_num))
            if (counter == dev_num):
                log_debug("about to publish")
                send_data = json.loads(move_dev_to_grp_res_packet)
                data_res = send_data[data_key]
                data_res[type_key] = move_devices_key
                data_res[new_group_key] = group
                data_res[old_group_key] = old_grp
                data_res[devices_key] = dev_list
                send_data[status_key_mqtt] = status
                updated_json_new = json.dumps(send_data)
                log_debug(updated_json_new)
                client.publish(create_grp_Res_Topic, updated_json_new)
                log_event(f"moved {dev_list} to {group}")
                flag = False
                counter = 0
                dev_list = []
        elif (status == error and flag == True):
            log_debug("inside elif")
            counter += 1
            device = data["device"]
            device_mod = add_state_l(device)
            dev_list.append(device_mod)
            if (counter == dev_num):
                send_data = json.loads(move_dev_to_grp_res_packet)
                data_res = send_data[data_key]
                data_res[type_key] = move_devices_key
                data_res[new_group_key] = group
                data_res[old_group_key] = old_grp
                data_res[devices_key] = dev_list
                send_data[status_key_mqtt] = status
                updated_json = json.dumps(send_data)
                client.publish(create_grp_Res_Topic, updated_json)
                log_event(f"failed to move {dev_list} to {group}")
                flag = False
                counter = 0
                dev_list = []
    except Exception as e:
        # handle the exception
        log_debug(f"An exception occurred:{e}")
        log_exception(e)


def on_dev_rm_from_group_res(client, message):

    # The function `on_dev_rm_from_group_res` handles the response received when removing a device from a
    # group in a home automation system.

    global counter
    global dev_list
    log_debug("inside device remove group response")
    log_debug(f"flag:{flag}")
    command = message.payload.decode()
    try:

        read_data = json.loads(command)
        data = read_data[data_key]
        log_debug(data)
        group_name = data[group_key]
        status = read_data[status_key_mqtt]
        if (status == ok and flag == False):

            counter += 1
            device = data["device"]
            device_mod = add_state_l(device)
            log_debug(device_mod)
            dev_list.append(device_mod)
            log_debug("counter{}".format(counter))
            log_debug("dev_num ={}".format(dev_num))
            if counter == dev_num:
                log_debug("inside rm res1")
                send_data = json.loads(add_dev_to_grp_res_packet)
                data_res = send_data[data_key]
                data_res[type_key] = remove_devices_key
                data_res[group_name_key] = group_name
                data_res[devices_key] = dev_list
                send_data[status_key_mqtt] = status
                updated_json = json.dumps(send_data)
                log_debug(updated_json)
                client.publish(create_grp_Res_Topic, updated_json)
                log_event(f"{dev_list} removed from {group_name}")
                log_debug(f"{dev_list} removed from {group_name}")
                dev_list = []
                counter = 0
        elif (status == error and flag == False):
            counter += 1
            log_debug("inside remove elif")
            device = data["device"]
            device_mod = add_state_l(device)
            dev_list.append(device_mod)
            if (counter == dev_num):
                send_data = json.loads(add_dev_to_grp_res_packet)
                data_res = send_data[data_key]
                data_res[type_key] = remove_devices_key
                data_res[group_name_key] = group_name
                data_res[devices_key] = dev_list
                send_data[status_key_mqtt] = status
                updated_json = json.dumps(send_data)
                log_debug(updated_json)
                client.publish(create_grp_Res_Topic, updated_json)
                log_event(f"failed to {dev_list} from {group_name}")
                counter = 0
                dev_list = []
        if status == ok and flag == True:
            counter += 1
            log_debug("moving to newgroup")
            device = data["device"]
            grp_data = json.loads(z2m_dev_grp_pkt)
            grp_data[group_key] = new_grp

            grp_data["device"] = device
            updated_json = json.dumps(grp_data)
            log_debug("adding the devices to new group")
            log_debug(updated_json)
            client.publish(z2m_add_dev_to_grp_req, updated_json)
            log_debug("counter={}".format(counter))
            dev_list = []  # newly added
    except Exception as e:
        # handle the exception
        log_debug(f"An exception occurred:{e}")
        log_exception(e)


def on_grp_rename_response(client, message):

    # The function `on_grp_rename_response` handles the response received after renaming a group, updates
    # the database with the new group name, uploads the encrypted database file to the cloud, and
    # publishes a backup request message.

    command = message.payload.decode()
    try:
        read_data = json.loads(command)
        data = read_data[data_key]
        old_name = data[from_key]
        new_name = data[to_key]
        status = read_data[status_key_mqtt]
        send_data = json.loads(rename_grp_response_packet)
        res_data = send_data[data_key]
        res_data[type_key] = rename_group_key
        res_data[old_name_key] = old_name
        res_data[new_name_key] = new_name
        send_data[status_key_mqtt] = status
        updated_json = json.dumps(send_data)
        client.publish(create_grp_Res_Topic, updated_json)
        log_event(f"group renamed from {old_name} to {new_name}")
        table_name = "group_table"
        database_name = glowfydb
        column_name = "friendly_name"
        column_value = old_name
        replace_value = new_name
        update_column_value(table_name, database_name,
                            column_name, column_value, replace_value)
        filename = "glowfy.db.encrypted"
        # remote_path = remote_file_path_for_glowfydb.format(mac_address)
        upload_file_to_cloud(ftp_server, ftp_username, ftp_password, glowfydb,
                             remote_file_path_for_glowfydb, key, local_file_path_for_glowfydb_encrypted, filename)
        client.publish(z2m_backup_req_topic, '{""}')
    except Exception as e:
        # handle the exception
        log_debug(f"An exception occurred:{e}")
        log_exception(e)


def on_grp_master_control(client, message):

    # The function `on_grp_master_control` is a callback function that handles messages received on a
    # specific topic and performs actions to control all groups.

    global grp_ctrl
    global master_grp_ctrl
    command = message.payload.decode()
    try:
        read_data = json.loads(command)
        group_name = read_data[group_name_key]
        state = read_data[state_key]
        if (group_name != "GlowFY/MASTER"):
            topic = z2m_group_control.format(mac_address, group_name)
            send_data = json.loads(control_pkt)
            send_data[state_key] = state
            updated_json = json.dumps(send_data)
            client.publish(topic, updated_json)
            grp_ctrl = True

        else:
            log_debug("inside else")
            database_name = glowfydb
            table_name = "group_table"
            coloumn_name = "friendly_name"
            values = search_column(table_name, database_name, coloumn_name)
            log_debug(values)
            for groups in values:
                topic = z2m_group_control.format(mac_address, groups)
                send_data = json.loads(control_pkt)
                send_data[state_key] = state
                updated_json = json.dumps(send_data)
                client.publish(topic, updated_json)
            master_grp_ctrl = True
    except Exception as e:
        # handle the exception
        log_debug(f"An exception occurred:{e}")
        log_exception(e)


def group_master_control_res(client, message):

    # The function `group_master_control_res` handles the logic for responding to messages received on a
    # specific topic in a Python program.

    global group_count
    global master_grp_ctrl
    global grp_ctrl
    Topic = message.topic
    log_debug(Topic)

    try:
        freindly_name = Topic.split("/")[2]
        print(freindly_name)
        log_debug(f"freindlyname:{freindly_name}")
        if (master_grp_ctrl is True and grp_ctrl is False):
            database_name = glowfydb
            table_name = "group_table"
            coloumn_name = "friendly_name"
            values = search_column(table_name, database_name, coloumn_name)
            count = count_elements_in_column(
                table_name, database_name, coloumn_name)
            command = message.payload.decode()
            received_msg = json.loads(command)
            log_debug(received_msg)
            try:
                state = received_msg[state_key]
            except Exception as e:
                log_debug(e)
            log_debug(values)
            for groups in values:
                if (groups == freindly_name):
                    group_count += 1

            if (group_count == count):
                send_data = json.loads(master_control_res_pkt)
                data = send_data[data_key]
                data[group_name_key] = "GlowFY/MASTER"
                data[state_key] = state
                send_data[status_key_mqtt] = ok
                updated_json = json.dumps(send_data)
                client.publish(grp_master_control_Res_Topic, updated_json)
                log_event(f"Master control is set to {state}")
                group_count = 0
                master_grp_ctrl = False
        elif (grp_ctrl is True and master_grp_ctrl is False):
            command = message.payload.decode()
            received_msg = json.loads(command)
            state = received_msg[state_key]

            send_data = json.loads(master_control_res_pkt)
            data = send_data[data_key]
            data[group_name_key] = freindly_name
            data[state_key] = state
            send_data[status_key_mqtt] = ok
            updated_json = json.dumps(send_data)
            client.publish(grp_master_control_Res_Topic, updated_json)
            log_event(f"{freindly_name} is set to {state}")
            group_count = 0
            grp_ctrl = False
    except Exception as e:
        # handle the exception
        log_debug(f"An exception occurred:{e}")
        log_exception(e)


def on_replace_gwy(client, message):

    # The function `on_replace_gwy` is a Python function that handles a message received by a client,
    # checks the type of the message, and performs downloading backup from the cloud .

    command = message.payload.decode()
    log_event("Replace gateway initiated")
    try:
        read_data = json.loads(command)
        type = read_data[type_key]

        if (type == replace_gateway):
            username = read_data[user_name_key]
            old_mac = read_data[old_gateway_mac_key]
            log_debug("searching for backup")

            remote_file_path_glowfydb = '/home/ftpuser/USER_BACKUP/{}/glowfy'.format(
                old_mac)
            remote_file_path_devicedb = '/home/ftpuser/USER_BACKUP/{}/devices'.format(
                old_mac)
            remote_file_path_zigbee2mqtt = '/home/ftpuser/USER_BACKUP/{}/zigbee2mqtt'.format(
                old_mac)
            filename_glowfydb = "glowfy.db.encrypted"
            filename_z2m = "data.zip.encrypted"
            # filename_devdb = "device.db.encrypted"

            # download_ftp_file(ftp_server, ftp_username, ftp_password,remote_file_path_devicedb,filename_devdb,local_file_path_for_devicedb_encrypted,key)

            download_ftp_file(ftp_server, ftp_username, ftp_password, remote_file_path_glowfydb,
                              filename_glowfydb, local_file_path_for_glowfydb_encrypted, key)

            download_ftp_file(ftp_server, ftp_username, ftp_password, remote_file_path_zigbee2mqtt,
                              filename_z2m, local_file_path_for_z2mzip_encrypted, key)

            stop_command = "sudo systemctl stop zigbee2mqtt"
            os.system(stop_command)
            shutil.rmtree("/opt/zigbee2mqtt/data")
            destination_zip = "/opt/zigbee2mqtt/data"
            unzip_file(z2mzip, destination_zip)
            time.sleep(2)
            subprocess.run(
                ["sudo", "chown", "-R", "calixto_admin", destination_zip], check=True)
            client.publish(z2m_restart_service_topic, '{""}')
            replace_gateway_res = json.loads(replace_gateway_pkt)
            replace_gateway_res[data_key] = command
            replace_gateway_res[status_key_mqtt] = "ok"
            updated_response = json.dumps(replace_gateway_res)
            client.publish(replace_Gwy_Res_Topic, updated_response)
            topic = f"GlowFY/{mac_address}"
            update_mac(topic)
            restart_command = "sudo systemctl restart zigbee2mqtt"
            os.system(restart_command)
            os.system("sudo reboot")

    except Exception as e:
        log_debug(f"An exception occurred:{e}")
        log_exception(e)


def on_grp_sts(client, message):

    # The function `on_grp_sts` receives a message payload, tries to parse it as JSON, and extracts the
    # value of the `group_name_key` from the parsed data.

    command = message.payload.decode()
    try:
        read_data = json.loads(command)
        group = read_data[group_name_key]

    except Exception as e:
        log_debug(f"An exception occurred:{e}")
        log_exception(e)


def on_backup_response(client, userdata, message):

    # The function `on_backup_response` handles the response received from a client and
    # parse the backup message into a zipfile and uploads it to the cloud.

    command = message.payload.decode()

    try:
        read_data = json.loads(command)
        data = read_data[data_key]
        zip = data[zip_key]
        status = read_data[status_key_mqtt]

        if (status == ok):
            # z2m_path = '/home/debian/glowfy_hub_app/dependencies/backup_with_timestamp/z2m.zip'
            save_base64_as_zip(zip, z2mzip)
            filename = 'data.zip.encrypted'
            # remote_path = remote_file_path_for_zigbee2mqtt.format(mac_address)
            upload_file_to_cloud(ftp_server, ftp_username, ftp_password, z2mzip,
                                 remote_file_path_for_zigbee2mqtt, key, local_file_path_for_z2mzip_encrypted, filename)
    except Exception as e:
        log_debug(f"An exception occurred:{e}")
        log_exception(e)


def on_info(client, message):

    # The `on_info` function processes a message received by a client and keep track of joined device

    global dev_temp_list
    global join_list
    global interview_list
    command = message.payload.decode()

    try:
        read_data = json.loads(command)
        permit_join = read_data["permit_join"]
        if (permit_join == False):
            remove_list = find_unmatching_elements(join_list, interview_list)
            send_data = json.loads(z2m_rm_packet)
            for dev in remove_list:
                send_data[id_key] = dev
                updated_json = json.dumps(send_data)
                client.publish(z2m_dev_remove_req, updated_json)
            if (len(dev_temp_list) != 0):
                for dev in dev_temp_list:
                    print("in on_info")
                    send_data[id_key] = dev
                    updated_json = json.dumps(send_data)
                    client.publish(z2m_dev_remove_req, updated_json)

            join_list = []
            interview_list = []
            dev_temp_list = []

    except Exception as e:
        log_debug(f"An exception occurred:{e}")
        log_exception(e)

def fvr_info(client,info_data):
    old_fvr,new_fvr = version_from_file()

    if new_fvr != None and old_fvr != new_fvr:
        info_data['new_fw_available'] = True
    else:
        info_data['new_fw_available'] = False
    info_data['current_fw_version'] = old_fvr
    info_data['new_fw_version'] = new_fvr

    updated = json.dumps(info_data)
    print(updated)
    client.publish(gateway_info_res_Topic,updated)

def on_firmware_info(client, message):
    try:
        command = message.payload.decode()
        data = json.loads(command)

        if data["type"] == "gateway_info":
            info_data = json.loads(gateway_info_pkt)
            info_data["connection_type"] = connection_type
            new_thread = Thread(target=fvr_info,args=(client,info_data,))
            new_thread.start()

        

    except Exception as e:
        log_debug(f"error getting firmware info {e}")


def on_scene_create_or_modify(client, message):
    command = message.payload.decode()
    data = json.loads(command)
    response = json.loads(dummy_response_pkt)
    response['data'] = data
    name = data['name']
    print("inside_create or modify")
    if (data['type'] == 'create_flow' or data['type'] == 'modify_flow' 
        or data['type'] == 'enable_flow' or data['type'] == 'disable_flow' or data['type'] == 'delete_flow' ):
        ret,dev_topic = create_or_modify_scenes(scene_file, command, client)
        print(ret)
        if ret == 0:
            response['status'] = 'ok'
        else:
            response['status'] = 'failed'
        if dev_topic is not None:
            client.message_callback_add(dev_topic,on_scene_trigger)
        print(ret,dev_topic)
        


        updated = json.dumps(response)
        client.publish(create_or_modify_flow_res_Topic, updated)

    elif data['type'] == 'trigger_flow':
        
        if manual_scene_function(scene_file, client,name) == 0:
            response['status'] = 'ok'
        else:
            response['status'] = 'failed'

        updated = json.dumps(response)
        client.publish(create_or_modify_flow_res_Topic, updated)
    elif data['type'] == 'flow_info':
        name = data['name']
        status = flow_info(name, scene_file)
        data['status'] = status
        updated = json.dumps(data)
        client.publish(create_or_modify_flow_res_Topic, updated)
    elif data['type'] == 'rename_flow':
        json_data = json.loads(dummy_response_pkt)
        json_data['data'] = data
        json_data['status'] = 'ok'
        old_name = data['old_name']
        new_name = data['new_name']
        rename_scene(scene_file, old_name, new_name)
        upadated_json = json.dumps(json_data)
        client.publish(create_or_modify_flow_res_Topic, upadated_json)


def on_scene_trigger(client,userdata,message):
    try:
        Topic = message.topic
        command = message.payload.decode()
        try:
            data = json.loads(command)
        except:
            print(command)
            return 1
        

        trigger_list = ["contact", "occupancy",
                "vibration", "smoke", "gas"]
 
        friendly_name = Topic.split("/")[2]
        print(friendly_name)
        
        if os.path.exists(state_json):
            with open (state_json, 'r') as json_file:
                json_data = json.load(json_file)

            if friendly_name in json_data:
            # Iterate through the keys of the nested dictionary
                for key_1 in json_data[friendly_name].keys():
                    # Check if the key exists in the 'data' dictionary and the values are different
                    for j_key in data.keys():
                        if j_key in trigger_list and j_key == key_1:
                            if key_1 in data and json_data[friendly_name][key_1] != data[key_1]:
                                json_data[friendly_name][key_1] = data[key_1]
            else:
                # If friendly_name doesn't exist, create a new entry for it
                for key in data.keys():
                    if key in trigger_list:
                        json_data[friendly_name] = {key:data[key]}

            with open(state_json, 'w') as file:
                json.dump(json_data, file)

        else:
            for key in data.keys():
                if key in trigger_list:
                    json_data = {friendly_name:{key:data[key]}}
                    json_content = json.dumps(json_data)
                    with open (state_json, 'w') as json_file:
                        json_file.write(json_content)


        try:
            scene_function(scene_file, friendly_name, command, client,state_json)
        except Exception as e:
            log_exception(f"no scenes created {e}")




    except Exception as e:
        log_exception(f"exception in scene trigger function{e}")


def on_fwr_update(client,message):
    command = message.payload.decode()
    data=json.loads(command)

    if data["type"] == "start_fw_update":
        firmware_management()
        send_res = json.loads(dummy_response_pkt)
        send_res["data"] == data["type"]
        send_res["status"] == "ok"
        updated = json.dumps(send_res)
        client.publish(gateway_fw_update_res_Topic,updated)



import os
import shutil
from firmware_mgnt.log_management import *
from time import sleep
import yaml
import paho.mqtt.client as mqtt
from constant.mqtt_constant import broker_port,broker_url
import socket
from device_database.group_database import search_column
from constant.databaseconstant import glowfydb
from constant.json_string_skeleton import z2m_rm_packet
from constant.mqtt_constant import z2m_dev_remove_req
import json
import subprocess
client = mqtt.Client(clean_session=True,userdata=False)

def reset_zigbee2mqtt():
    try:
        
        try:
            client.connect(broker_url, broker_port)
        except socket.gaierror as e:
            log_debug("Not Connected") 
        
        # try:
        #     devlist = search_column("devices",glowfydb,"device_id")
        #     for devices in devlist:
        #         rm = json.loads(z2m_rm_packet)
        #         rm["id"]= devices
        #         updated = json.dumps(rm) 
        #         log_debug(updated)
        #         client.publish(z2m_dev_remove_req,updated)
        # except Exception as e:
        #     log_debug(f"error:{e}")
            
        # Stop Zigbee2MQTT service (replace 'stop_command' with the actual command to stop Zigbee2MQTT)
        stop_command = "sudo systemctl stop zigbee2mqtt"  # Replace with the appropriate command for your system
        os.system(stop_command)
        
        # Reset configuration.yaml (replace 'config_file_path' with the actual path to your configuration.yaml file)
        config_file_path = "/opt/zigbee2mqtt/data/configuration.yaml"
        if os.path.exists(config_file_path):
            os.remove(config_file_path)
            log_event(f"{config_file_path} removed")
        default_config_path = "/home/calixto_admin/glowfy_hub_app/dependencies/config/configuration.yaml"  # Replace with the path to the default configuration.yaml
        
        shutil.copy(default_config_path, config_file_path)
        subprocess.run(["sudo","chown","-v","calixto_admin",config_file_path], check=True)
        # Delete database.db (replace 'database_path' with the actual path to your database.db file)
        database_path = "/opt/zigbee2mqtt/data/database.db"
        if os.path.exists(database_path):
            os.remove(database_path)
            log_event(f"{database_path} removed")
        databasebackup_path = "/opt/zigbee2mqtt/data/database.db.backup"
        if os.path.exists(databasebackup_path):
            os.remove(databasebackup_path)
            log_event(f"{databasebackup_path} removed")
        coordinator_backup = "/opt/zigbee2mqtt/data/coordinator_backup.json"

        if os.path.exists(coordinator_backup):
            os.remove(coordinator_backup)
            log_event(f"{coordinator_backup} removed")
        log_path = "/opt/zigbee2mqtt/data/log"
        if os.path.exists(log_path):
            shutil.rmtree(log_path)
            log_event(f"{log_path} removed")

        
        # Start Zigbee2MQTT service (replace 'start_command' with the actual command to start Zigbee2MQTT)
        start_command = "sudo systemctl restart zigbee2mqtt"  # Replace with the appropriate command for your system
        os.system(start_command)
        sleep(1)
    except Exception as e:
        log_debug(f"1 An Exception Occured:{e}")
        log_exception(e)
        

# Call the function to reset Zigbee2MQTT
# reset_zigbee2mqtt()

def remove_created_files():
    try:
        glowfydb="/home/calixto_admin/glowfy_hub_app/dependencies/data/glowfy_hub/glowfy.db"
        if os.path.exists(glowfydb):
            os.remove(glowfydb)
            log_event(f"{glowfydb} removed")
        log ="/home/calixto_admin/glowfy_hub_app/dependencies/config/log/glowfy_log.log"
        if os.path.exists(log):
            os.remove(log)
            log_event(f"{log} removed")
        counter ="/home/calixto_admin/glowfy_hub_app/dependencies/config/counter/counter.txt"
        if os.path.exists(counter):
            os.remove(counter)
            log_event(f"{counter} removed")
        state_file_path ="/home/calixto_admin/glowfy_hub_app/dependencies/data/devices/state.json"
        if os.path.exists(state_file_path):
            os.remove(state_file_path)
            log_event(f"{state_file_path} removed")
        jobsdb="/home/calixto_admin/glowfy_hub_app/dependencies/data/glowfy_hub/jobs.db"
        if os.path.exists(jobsdb):
            os.remove(jobsdb)
            log_event(f"{jobsdb} removed")
        scene_yamls = "/home/calixto_admin/glowfy_hub_app/dependencies/data/glowfy_hub/scene.yaml"
        if os.path.exists(scene_yamls):
            os.remove(scene_yamls)
            log_event(f"{scene_yamls} removed")
        return 0
    except Exception as e:
        log_debug(f"Error{e}")


def update_mac(base_topic):

    # Load the configuration.yaml file
    config_file_path = "/opt/zigbee2mqtt/data/configuration.yaml"
    with open(config_file_path, "r") as config_file:
        config_data = yaml.safe_load(config_file)

    # Modify the values

    config_data["mqtt"]["base_topic"] = f"{base_topic}"

    # Save the modified configuration back to the file
    with open(config_file_path, "w") as config_file:
        yaml.dump(config_data, config_file)

    log_debug("Configuration updated successfully.")


def factory_reset():

    reset_zigbee2mqtt()
    remove_created_files()
    return 0 
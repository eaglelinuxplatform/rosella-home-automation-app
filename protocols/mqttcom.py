import paho.mqtt.client as mqtt
from constant.mqtt_constant import *
from firmware_mgnt.log_management import *
from peripherals.led import *
import socket
import time
from queue import Queue,Empty
from protocols.callback_mqtt import *
from concurrent import futures
# counter=0
# dev_num =0
# dev_list=[]
# flag = False
# save_rm =False
# old_grp = ''
# new_grp = ''

Q=Queue()
client = mqtt.Client(client_id=mac_address, clean_session=False,userdata=False)

def on_publish(client,userdata,result):
    
    # The function "on_publish" is a callback function that is triggered when data is successfully published by a client.
    
 
    log_debug("data published \n")
    pass

def on_disconnect(client, userdata, rc):
  
    # The function "on_disconnect" is used to handle unexpected disconnections from an MQTT client andlog_debug a message if the disconnection is not expected.
    

    if rc != 0:
        log_debug("Unexpected MQTT disconnection. Will auto-reconnect")
        client.username_pw_set(username,password)
        try:
            Trying_to_con_server()
            client.connect(broker_url, broker_port)
        except socket.gaierror as e:
            log_debug("Not Connected")


def on_connect(client, userdata, flags, rc):
 
    # The function log_debugs the result code when the client connects.
    

    log_debug("Connected With Result Code ")
    log_debug("Resultcode="+ str(rc))
    log_event("Mqtt connected Resultcode="+ str(rc))

def on_message(client, userdata, message):

    # The function `on_message` receives a message, checks if the message payload is "gatewaystatus", and publishes a response.
    try:
        Q.put(message)
        # log_debug("q_put")
        print("q_put")
    except UnicodeDecodeError as e:
        log_debug(f"Error decoding message payload: {e}")
def on_subscribe(client, userdata, mid, granted_qos):
    log_debug("subscribed to newtopic")

def subscribe_on_start(scene_path,client):
    try:
        if os.path.exists(scene_path):
            with open(scene_path, 'r') as yaml_file:
                yaml_data = yaml.safe_load(yaml_file)

            for scene, attributes in yaml_data.items():
                    for i in range(attributes['source_count']):
                        try:
                            topic = f"GlowFY/{mac_address}/{attributes['source'][i]['id']}"
                            client.subscribe(topic,qos=0)
                            client.message_callback_add(topic,on_scene_trigger)
                        except KeyError:
                            print("skip")
    except Exception as e:
        print(e)

def mqttmain():
    

  # client = mqtt.Client(client_id=mac_address, clean_session=False,userdata=False)
  client.on_connect = on_connect
  client.on_disconnect = on_disconnect
  client.on_publish = on_publish
  client.on_message = on_message
  client.on_subscribe = on_subscribe
 

  #client.on_message = on_message
  client.username_pw_set(username,password)
  try:
    client.connect(broker_url, broker_port)
  except socket.gaierror as e:
    log_debug("Not Connected")


  client.subscribe("ledreq", qos=0)
  client.subscribe(sts_Req_Topic, qos=0)
  client.subscribe(permit_join_Req_Topic,qos=0)
  client.subscribe(permit_join_res_z2m,qos=0)
  client.subscribe(z2m_dev_discovery,qos=0)
  client.subscribe(dev_join_Res_Topic,qos=0)
  client.subscribe(save_dev_Req_Topic,qos=0)
  client.subscribe(z2m_dev_remove_res,qos=0)
  client.subscribe(create_grp_Req_Topic,qos=0)
  client.subscribe(z2m_create_grp_res,qos=0)
  client.subscribe(z2m_rm_grp_res,qos=0)
  client.subscribe(z2m_add_dev_to_grp_res,qos=0)
  client.subscribe(z2m_rm_dev_from_grp_res,qos=0)
  client.subscribe(grp_master_control_Req_Topic,qos=0)
  client.subscribe(z2m_rm_dev_from_grp_req,qos=0)
  client.subscribe(z2m_grp_rename_res,qos=0)
  client.subscribe(remove_dev_Req_Topic,qos=0)
  client.subscribe(replace_Gwy_Req_Topic,qos=0)
  client.subscribe(group_sts_req,qos=0)
  client.subscribe(z2m_backup_res_topic,qos=0)
  client.subscribe(z2m_info_topic,qos=0)
  client.subscribe(create_or_modify_flow_Topic,qos=0)
  client.subscribe(gateway_info_Topic,qos=0)
  client.subscribe(gateway_fw_update_Topic,qos=0)
  client.subscribe(gateway_push_notification_Topic,qos=0)

  
  # client.message_callback_add(sts_Req_Topic,on_status)
  # client.message_callback_add(permit_join_Req_Topic,on_permit_to_join_req)
  # client.message_callback_add(permit_join_res_z2m,on_permit_to_join_res)
  # client.message_callback_add(z2m_dev_discovery,on_joined_dev_req)
  # client.message_callback_add(dev_join_Res_Topic,on_join_dev_res)
#   client.message_callback_add(dev_topic,on_scene_trigger)
  # client.message_callback_add(save_dev_Req_Topic,on_dev_save_req)
  # client.message_callback_add(z2m_dev_remove_res,on_dev_rm_res)
  # client.message_callback_add(create_grp_Req_Topic,on_grp_req)
  # client.message_callback_add(z2m_create_grp_res,on_create_grp_res)
  # client.message_callback_add(z2m_rm_grp_res,on_rm_grp_res)
  # client.message_callback_add(z2m_add_dev_to_grp_res,on_add_dev_to_grp_res)
  # client.message_callback_add(z2m_rm_dev_from_grp_res,on_dev_rm_from_group_res)
  # client.message_callback_add(grp_master_control_Req_Topic,on_grp_master_control)
  # client.message_callback_add(z2m_grp_rename_res,on_grp_rename_response)
  # client.message_callback_add(remove_dev_Req_Topic,on_dev_rm_req)
  # client.message_callback_add(replace_Gwy_Req_Topic,on_replace_gwy)
  # client.message_callback_add(group_sts_req,on_grp_sts)
  client.message_callback_add(z2m_backup_res_topic,on_backup_response)
  # client.message_callback_add(z2m_info_topic,on_info)


 

  log_debug("Starting MQTT Client")



  
  while True:
        client.loop()
        time.sleep(0.1)
        


#asyncio.run(mqttmain())
        
def handle_message(client,msg):
    # log_debug("listener thread started.....")
    # while True:
    try:
    #         print("q_rel")
    #         msg = Q.get()
            
            # log_debug(f"que:{Q.qsize()}")
            # print(f"message:{msg}")
        topic = msg.topic
        # print(f"topic :{topic}")
        if(topic == sts_Req_Topic):
            on_status(client,msg)
        elif(topic == permit_join_Req_Topic):
            on_permit_to_join_req(client,msg)
        elif(topic == permit_join_res_z2m):
            on_permit_to_join_res(client,msg)
        elif(topic == z2m_dev_discovery):
            on_joined_dev_req(client,msg)
        elif(topic == dev_join_Res_Topic):
            on_join_dev_res(client,msg)
        elif(topic == save_dev_Req_Topic):
            on_dev_save_req(client,msg)
        elif(topic == z2m_dev_remove_res):
            on_dev_rm_res(client,msg)
        elif(topic == create_grp_Req_Topic):
            on_grp_req(client,msg)
        elif(topic == z2m_create_grp_res):
            on_create_grp_res(client,msg)
        elif(topic == z2m_rm_grp_res):
            on_rm_grp_res(client,msg)
        elif(topic == z2m_add_dev_to_grp_res):
            on_add_dev_to_grp_res(client,msg)
        elif(topic == z2m_rm_dev_from_grp_res):
            on_dev_rm_from_group_res(client,msg)
        elif(topic == grp_master_control_Req_Topic):
            on_grp_master_control(client,msg)
        elif(topic == z2m_grp_rename_res):
            on_grp_rename_response(client,msg)
        elif(topic == remove_dev_Req_Topic):
            on_dev_rm_req(client,msg)
        elif(topic == replace_Gwy_Req_Topic):
            on_replace_gwy(client,msg)
        elif(topic == group_sts_req):
            on_grp_sts(client,msg)
        elif(topic == z2m_info_topic):
            on_info(client,msg)
        # elif(topic == create_or_modify_flow_Topic or topic == gateway_info_Topic or topic == gateway_fw_update_Topic or topic == gateway_push_notification_Topic):
        #     dummy_function(client,msg,topic)
        elif(topic == create_or_modify_flow_Topic):
            on_scene_create_or_modify(client,msg)
        elif(topic == gateway_info_Topic):
            on_firmware_info(client,msg)
        elif(topic == gateway_fw_update_Topic):
            on_fwr_update(client,msg)

    except Empty:
        time.sleep(0.2)



def mqtt_listener():
    log_debug("listener thread started.....")
    executor = futures.ThreadPoolExecutor(max_workers=50)
    while True:
        try:
            print("q_rel")
            msg = Q.get()
            executor.submit(handle_message, client, msg)
        except Empty:
            time.sleep(0.2)
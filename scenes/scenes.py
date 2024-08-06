import yaml
import json
import os
import atexit
from pytz import utc
from scenes.schedules_test import create_scheduled_job, delete_scheduled_job
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from time import sleep
from datetime import date,datetime
from firmware_mgnt.log_management import log_exception
from constant.mac_id import mac_address
from constant.databaseconstant import trigger_list


# data = json.loads(shedule_json)
# print(data["source"][0]["time"])
# timess = data["source"][0]["time"]
# x=timess.split(":")
# for i in x:
#     print(int(i))

# name =data["name"]


jobstores_1 = {'default': SQLAlchemyJobStore(
    url='sqlite:////home/calixto_admin/glowfy_hub_app/dependencies/data/glowfy_hub/jobs.db')}
executors_1 = {'default': ThreadPoolExecutor(20)}
job_defaults_1 = {'coalesce': False, 'max_instances': 20}

scheduler_1 = BlockingScheduler(
    jobstores=jobstores_1, executors=executors_1, job_defaults=job_defaults_1, timezone=utc)



def find_missing_number(arr):
    """Finds the missing number in an array.

    Args:
      arr: A list of integers.

    Returns:
      The missing number.
    """
    try:
        # Create a set of the elements in the array.
        elements = set(arr)
        print(elements)

        # Find the smallest element in the set.

        smallest_element = int(min(elements))

        print(f"min:{smallest_element}")
        largest_element = max(elements)
        largest_num = int(largest_element)
        print(f"max:{largest_num}")

        # Iterate over the numbers from the smallest element to the largest element,
        # and return the first number that is not in the set.
        for i in range(smallest_element, largest_num + 1):
            if i not in elements:
                print(f"missing:{i}")
                return i
    except ValueError:
        return 1


def scene_number_check(data):
    if isinstance(data, dict):
        # print(yml_data.items())
        scene_count_list = []
        for key, value in data.items():
            full_key = f"{key}"
            scene_count_list.append(int(full_key.strip("scene_")))
        print(scene_count_list)
        num = find_missing_number(scene_count_list)
        if num == None:
            return max(scene_count_list)+1
        else:
            return num


def check_for_duplication(yaml_data, data):
    if isinstance(yaml_data, dict):
        name_key = "name"
        j_name = data["name"]
        name_list = []
        for key, value in yaml_data.items():
            name_value = f"{name_key}:{key}"
            name = yaml_data[key]['name']
            print(name_value)
            print(name)
            name_list.append(name)

        if j_name in name_list:
            print("exists")
            print(name_list)
            return 1
        else:
            return 0

def get_section_name(file_path, entry_key, entry_value):
    with open(file_path, 'r') as file:
        yaml_data = yaml.safe_load(file)  # Load the YAML data

    # Iterate through the sections in the YAML data
    for section_name, section_data in yaml_data.items():
        if entry_key in section_data and section_data[entry_key] == entry_value:
            return section_name  # Return the section name if entry is found in the section

    return None


def check_if_schedule(file_path, json_name):
    with open(file_path, 'r') as file:
        yaml_data = yaml.safe_load(file)  # Load the YAML data

    # Iterate through the sections in the YAML data
    for section_name, section_data in yaml_data.items():
        if "source" in section_data and section_data["source"][0]["type"] == "schedule":
            if section_data["name"] == json_name:
                return True

    return None


def schedule_check(file_path):
    with open(file_path, 'r') as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)

    for scene, attributes in yaml_data.items():
        if attributes['status'] == "Enable":
            for source in attributes['source']:
                if source.get('type') == 'schedule':
                    if is_current_time(source.get('time', '')) and (is_today_in_days(source.get('repeat', '')) or source.get('repeat')=='once'):
 
                        return scene,attributes['name']



def publish_state(target):
    from protocols.mqttcom import client
    target_id = target.get('id')
    state = None
    for key, value in target.items():
        if key.startswith("state_l") or key.startswith("state") or key.startswith("brightness") or key.startswith("fan_mode"):
            state = value
            break

    # print(f"ID: {target_id}, State: {state}")
    topic = f"GlowFY/{mac_address}/{target.get('id')}/set"
    payload = {f"{key}": f"{target.get(key)}"}
    formated = json.dumps(payload)
    client.publish(topic, formated)


def send_push_notification(message):
    # Implement the logic to send push notifications
    print(f"Sending push notification: {message}")

def activate_manual_scene(scene_name):
    # Implement the logic to activate manual scene
    print(f"Activating manual scene: {scene_name}")

def handle_target(target):
    from protocols.mqttcom import client
    if target.get('type') == 'push_notification':
        topic = f"GlowFY/{mac_address}/request/pushnotification"           
        payload={"type":f"{target.get('type')}","message":f"{target.get('message')}"}
        formated = json.dumps(payload)
        client.publish(topic, formated)

    elif target.get('type') == 'manual_scene':
        topic = f"GlowFY/{mac_address}/request/flow" 
        payload={"type":"trigger_flow","name":f"{target.get('scene_name')}"}
        formated = json.dumps(payload)
        client.publish(topic, formated)
    else:
        publish_state(target)


# Function to handle targets with delay
def process_targets(targets,start_count):
    for i in range(start_count, len(targets)):
        target = targets[i]
        if target.get('type') == 'delay':
            # delay_seconds = target['hours'] * 3600 + target['minutes'] * 60 + target['seconds']
            hours = target['hours']
            minutes = target['minutes']
            seconds = target['seconds']
            now = datetime.now()
            print('delay')
            create_scheduled_job(
                                process_targets,
                                day_of_week=['once'],  
                                args=(targets,i+1,),
                                hour=now.hour+hours,
                                minute=now.minute+minutes,
                                second=now.second+seconds,
                                scheduler=scheduler_1,
                                job_id='delay_job',
                                date=date.today(),

                        )
            # scheduler.add_job(process_targets, args=(targets[targets.index(target)+1:], scheduler), trigger='interval', seconds=delay_seconds, max_instances=1)

            break
        else:
            handle_target(target)

# create_yaml(output_file_path)
def job(file_path):
    # from protocols.mqttcom import client
    with open(file_path, 'r') as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)
    
    scene,name = schedule_check(file_path)
    print(scene,name)
    targets = yaml_data[scene]['targets']
    
    process_targets(targets,0)



def subscribe_to_source(json_data,client):
    j_data = json.loads(json_data)
    print(j_data)
    for i in range(j_data["source_count"]):
        print(i)
        if j_data["source"][i]["type"] == "smart_devices":
            str_id = j_data["source"][i]["id"]
    
            dev_topic = f"GlowFY/{mac_address}/{str_id}"
            print(f"dev_topic{dev_topic}")
            client.subscribe(dev_topic,qos=0)
            # client.message_callback_add(dev_topic,)
            return dev_topic


def create_or_modify_scenes(file_path, json_data, client):
    print("inside_function")
    try:
        data = json.loads(json_data)
        type_data = data["type"]
        dev_topic = None
        if (type_data == "create_flow"):

            if os.path.exists(file_path):
                with open(file_path, 'r') as yaml_file:
                    yml_data = yaml.safe_load(yaml_file)
                num = scene_number_check(yml_data)

                name = data["name"]
                if check_for_duplication(yml_data, data) == 0:
                    if data["source"][0]["type"] == "schedule":

                        repeat = data["source"][0]["repeat"]
                        days = repeat.split(",")
                        time = data["source"][0]["time"]
                        hour_str, min_str = time.split(":")
                        hour_in = int(hour_str)
                        minute_in = int(min_str)
                        create_scheduled_job(
                            job,
                            day_of_week=days,  
                            args=(file_path,),
                            hour=hour_in,
                            minute=minute_in,
                            second=0,
                            scheduler=scheduler_1,
                            job_id=name,
                            date=date.today(),

                        )
                        if  not scheduler_1.running:
                            scheduler_1.start()
                            print("scheduler started")
                    else:
                        dev_topic = subscribe_to_source(json_data,client)   
                        

                    yml_data[f"scene_{num}"] = {"name": name,
                                                "conditions": data["conditions"],"source_count":data["source_count"],
                                                "source": data["source"],"target_count":data["target_count"], "targets": data["targets"], "status": "Enable"}

                    yaml_content = yaml.dump(
                        yml_data, default_flow_style=False)
                    with open(file_path, 'w') as yaml_file:
                        yaml_file.write(yaml_content)
                       
                    return 0,dev_topic 
                else:
                    print("flow exists")
                    return 1

            else:

                name = data["name"]
                if data["source"][0]["type"] == "schedule":

                    repeat = data["source"][0]["repeat"]
                    days = repeat.split(",")
                    time = data["source"][0]["time"]
                    hour_str, min_str = time.split(":")
                    hour_in = int(hour_str)
                    minute_in = int(min_str)

                    create_scheduled_job(
                        job,
                        args=(file_path,),
                        day_of_week=days,  # Schedule for Monday, Wednesday, and Friday
                        hour=hour_in,
                        minute=minute_in,
                        second=0,
                        scheduler=scheduler_1,
                        job_id=name,
                        date=date.today(),

                    )
                    if  not scheduler_1.running:
                        scheduler_1.start()
                        print("scheduler started")
                else:
                    dev_topic = subscribe_to_source(json_data,client)   
 
               
                yml_data = {"scene_1": {"name": name,
                                                "conditions": data["conditions"],"source_count":data["source_count"],
                                                "source": data["source"],"target_count":data["target_count"], "targets": data["targets"], "status": "Enable"}}

            yaml_content = yaml.dump(yml_data, default_flow_style=False)
            with open(file_path, 'w') as yaml_file:
                yaml_file.write(yaml_content)

            return 0,dev_topic
        elif (type_data == "delete_flow"):
            print("delete")
            name = data["name"]
            if check_if_schedule(file_path, json_name=name) is True:
                delete_scheduled_job(name, scheduler_1)

            with open(file_path, 'r') as file:
                yaml_data = yaml.safe_load(file)  # Load the YAML data

            section_name = get_section_name(file_path, "name", name)
            # Remove the desired section from the YAML data
            if section_name in yaml_data:
                del yaml_data[section_name]

            # Write the modified YAML data back to the file
            with open(file_path, 'w') as file:
                yaml.dump(yaml_data, file)
            
            return 0,None

    
        elif (type_data == "modify_flow"):

            with open(file_path, 'r') as file:
                yaml_data = yaml.safe_load(file)
            name = data["name"]
            if check_if_schedule(file_path, json_name=name) is True:
                delete_scheduled_job(name, scheduler_1)
            section_name = get_section_name(file_path, "name", name)
            if section_name in yaml_data:
                del yaml_data[section_name]

            num = scene_number_check(yaml_data)
            if (num == None):
                num = 1

            if data["source"][0]["type"] == "schedule":

                repeat = data["source"][0]["repeat"]
                days = repeat.split(",")
                time = data["source"][0]["time"]
                hour_str, min_str = time.split(":")
                hour_in = int(hour_str)
                minute_in = int(min_str)
                create_scheduled_job(
                    job,
                    day_of_week=days,
                    args=(file_path,),
                    hour=hour_in,
                    minute=minute_in,
                    second=0,
                    scheduler=scheduler_1,
                    job_id=name,
                    date=date.today(),
                )
                if  not scheduler_1.running:
                    scheduler_1.start()
                    print("scheduler started")
            else:
                dev_topic = subscribe_to_source(json_data,client)   

            yaml_data[f"scene_{num}"] = {"name": name,
                                                "conditions": data["conditions"],"source_count":data["source_count"],
                                                "source": data["source"],"target_count":data["target_count"], "targets": data["targets"], "status": "Enable"}
            yaml_content = yaml.dump(yaml_data, default_flow_style=False)
            with open(file_path, 'w') as yaml_file:
                yaml_file.write(yaml_content)
            
            return 0,dev_topic
        elif (type_data == "enable_flow"):
            print("inside enable")
            name = data["name"]
            with open(file_path, 'r') as file:
                yaml_data = yaml.safe_load(file)
            for scene, attributes in yaml_data.items():
                if attributes['name'] == name:

                    attributes['status'] = "Enable"

            with open(file_path, 'w') as file:
                yaml.dump(yaml_data, file)
            return 0,None
        elif (type_data == "disable_flow"):
            print("inside disable")
            name = data["name"]
            with open(file_path, 'r') as file:
                yaml_data = yaml.safe_load(file)
            for scene, attributes in yaml_data.items():
                if attributes['name'] == name:

                    attributes['status'] = "Disable"

            with open(file_path, 'w') as file:
                yaml.dump(yaml_data, file)
            return 0,None

    except Exception as e:
        log_exception(f"error in creation of flow{e}")
        return 1,None
def is_current_time(time_str):
    current_time = datetime.now().strftime('%H:%M')
    return time_str == current_time


def is_today_in_days(days_str):
    today = datetime.now().strftime('%a').lower()
    return today in days_str.split(',')

def scene_check(device_id,file_path,command):
    trigger_list = ["contact", "occupancy",
                    "vibration", "smoke", "gas"]
    data = json.loads(command)
    with open(file_path, 'r') as yaml_file:
            yaml_data = yaml.safe_load(yaml_file)  
    for scene, attributes in yaml_data.items():
        if attributes['status'] == "Enable":
            for source in attributes['source']:
                if source.get('type') == 'smart_devices':
                    for key in data.keys():
                        if key in trigger_list: 
                            trigger_name = key
                            trigger_data = data[key]
                            for key_y in source:
                                if key_y in trigger_list:

                                    if (device_id == source.get('id') 
                                        and trigger_name == key_y and 
                                        trigger_data == source.get(key_y)):

                                        return attributes['name']


def scene_source(scene_name,scene_file_path,state_file_path):
    with open(scene_file_path, 'r') as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)
    id_list = []
    for scene, attributes in yaml_data.items():
        # attributes.get(scene)
        if attributes['status'] == "Enable":
            if attributes['name'] == scene_name:
                if attributes['conditions'] == "all_condition":
                    with open (state_file_path, 'r') as json_file:
                        json_data = json.load(json_file)
                        for i in range(attributes['source_count']):
                            
                            id_list.append(attributes['source'][i]['id'])
                            
                        
    return id_list,scene

def json_source(id,state_file_path):
    with open (state_file_path, 'r') as json_file:
        json_data = json.load(json_file)    

    return(json_data[id])


def source_check(scene_name,scene_file_path,state_file_path):
    condition_count = 0
    with open(scene_file_path, 'r') as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)
    id_list,current_scene = scene_source(scene_name,scene_file_path,state_file_path)
    for source_item in yaml_data[current_scene]['source']:
        print(source_item)
        # Get the id from the current source item
        source_id = source_item.get('id')
        # Check if the source_id exists in id_list
        if source_id in id_list:
            # Iterate over the keys of the current source item
            for key in source_item.keys():
                print(source_item.keys())
                if key in trigger_list:

                    # print(key,source_item[key], source_id)
                    yaml_dat = {key:source_item[key]}
                    
                    json_dat = json_source(source_id,state_file_path)
                    print(f"yaml_date:{yaml_dat}",f"json_dat:{json_dat}")
                    if yaml_dat == json_dat:
                        condition_count +=1
    if yaml_data[current_scene]['source_count'] == condition_count:
        condition_flag = True
    else:
        condition_flag = False
    return condition_flag
                    
                    



def scene_function(file_path, device_id, command, client,state_file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as yaml_file:
            yaml_data = yaml.safe_load(yaml_file)
        scene_name = scene_check(device_id,file_path,command)
        print(scene_name)
        trigger_list = ["contact", "occupancy",
                        "vibration", "smoke", "gas"]
        for scene, attributes in yaml_data.items():
            if attributes['name'] == scene_name:
                if attributes['status'] == "Enable":
                    if attributes['conditions'] == "any_condition":
                        print("any condition")
                        for target in attributes['targets']:
                            print(f"target:{target}")
                            if target.get('type') == 'smart_devices':
                                print('smart')
                                for key in target:
                                    print(f"keys in target:{key}")
                                    if key.startswith("state_l") or key.startswith("state") or key.startswith("brightness") or key.startswith("fan_mode"):
                                        topic = f"GlowFY/{mac_address}/{target.get('id')}/set"
                                        payload = {
                                            f"{key}": f"{target.get(key)}"}
                                        print(payload)
                                        formated = json.dumps(payload)
                                        client.publish(topic, formated)
                            if target.get('type') == 'push_notification':
                                topic = f"GlowFY/{mac_address}/request/pushnotification"
                                payload={"type":f"{target.get('type')}","message":f"{target.get('message')}"}
                                formated = json.dumps(payload)
                                client.publish(topic, formated)

                    elif attributes['conditions'] == "all_condition":
                        print("all condition")
                        if source_check(scene_name,file_path,state_file_path):
                            id_list,current_scene = scene_source(scene_name,file_path,state_file_path)
                            for target_item in yaml_data[current_scene]['targets']:

                                    target_id = target_item.get('id')

                                    # Check if the source_id exists in id_list
                                        # Iterate over the keys of the current source item
                                    for key in target_item.keys():
                                        print(f"key:{key}")
                                        print(target_item['type'])
                                        if target_item['type'] == 'smart_devices':
                                            if key.startswith("state_l") or key.startswith("state") or key.startswith("brightness") or key.startswith("fan_mode"):
                                                topic = f"GlowFY/{mac_address}/{target_id}/set"
                                                payload ={key:target_item[key]}
                                                formated = json.dumps(payload)
                                                print(f"formated:{formated}")
                                                client.publish(topic, formated)
                                        elif target_item['type'] == 'push_notification':
                                            topic = f"GlowFY/{mac_address}/request/pushnotification"
                                            payload = {"type":target_item['type'],"message":target_item['message']}
                                            formated = json.dumps(payload)
                                            print(f"formated:{formated}")
                                            client.publish(topic, formated)

                                        elif target_item['type'] == 'manual_scene':
                                            topic = f"GlowFY/{mac_address}/request/flow"
                                            payload = {"type":"trigger_flow","name":target_item['scene_name']}
                                            formated = json.dumps(payload)
                                            print(f"formated:{formated}")
                                            client.publish(topic, formated)
    else:
        pass


def manual_scene_function(file_path, client,name):
    try:
        manual_flag= False

        with open(file_path, 'r') as yaml_file:
            yaml_data = yaml.safe_load(yaml_file)

        for scene, attributes in yaml_data.items():
            if attributes['name'] == name:
                if attributes['status'] == "Enable":
                    for source in attributes['source']:
                        if source.get('type') == 'manual_scene':
                            for target in attributes['targets']:
                                
                                if target.get('type') == 'smart_devices':
                                    
                                    for key, value in target.items():
                                        print(f"key_manual:{key}")
                                        if key.startswith("state") or key.startswith("brightness") or key.startswith("fan_mode"):
                                            topic = f"GlowFY/{mac_address}/{target.get('id')}/set"
                                            payload = json.dumps({key: value})
                                            print(payload)
                                            client.publish(topic, payload)

                            return 0
    except Exception as e:
        print(f"failed triggering manual scene {e}")

        return 1


def rename_scene(file_path,old_name,new_name):
    try:

        with open(file_path, 'r') as yaml_file:
            yaml_data = yaml.safe_load(yaml_file)

        for scene, attributes in yaml_data.items():
            if attributes['name'] == old_name:
                attributes['name'] = new_name

        with open(file_path, 'w') as file:
            yaml.dump(yaml_data, file)   

    except Exception as e:
        print(f"failed renaming scene {e}")
        return 1
def flow_info(flow_name,file_path):
    try:

        with open(file_path, 'r') as yaml_file:
            yaml_data = yaml.safe_load(yaml_file)

        for scene, attributes in yaml_data.items():
            if attributes['name'] == flow_name:
                return attributes['status']

        with open(file_path, 'w') as file:
            yaml.dump(yaml_data, file)   

    except Exception as e:
        print(f"failed renaming scene {e}")
        return 1
    



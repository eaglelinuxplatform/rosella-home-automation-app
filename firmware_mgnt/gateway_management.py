#! /usr/bin/env python3.10
import json
from constant.gateway_mgnt_constant import *
from firmware_mgnt.health_check import *
import requests
import time
import os
import ftplib
import zipfile
import crcmod
import signal
import socket
import shutil
import re

from datetime import date
import multiprocessing
# from firmware_mgnt.log_management import *

#############################################  FIRMWARE MANAGEMENT   ####################################################
def is_connected():

    # The function checks if the device is connected to the internet by attempting to connect to a known host.
 
    try:
        # Attempt to connect to a known host
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False

# firmware updatation process
def firmware_management():
    print("In firmware management")
    cur_path()

# check for current path and navigate to the partition
def cur_path():
    try:
        global old_partition_index
        # check for the current firmware running path
        present_dire = os.getcwd()
        print("current dir = ", present_dire)

        # checking the current path of the firmware
        _, f = os.path.split(present_dire)
        old_partition_index = partitions.index(f)

        # check in which partition the application is running
        if old_partition_index == 1:
            print("firmware currently runs in partition_1 and switching to partitions_2")
            log_event("firmware currently runs in partition_1 and switching to partitions_2")
            fvr_dwnld(partitions[2])

        elif old_partition_index == 2:
            print("firmware currently runs in partions_2 and switching to partitions_1")
            log_event("firmware currently runs in partions_2 and switching to partitions_1")
            fvr_dwnld(partitions[1])

        else:
            print("firmware currently runs in default and switching to partitions_1")
            log_event("firmware currently runs in default and switching to partitions_1")
            fvr_dwnld(partitions[1])

    except Exception as e:
                print('Error:', str(e))
                log_exception(e)

# function to change the path and download the firmware
def fvr_dwnld(path):
    attempt = 0
    # switching to the particular location(partition)
    os.chdir("../" + path)
    chg_path = os.getcwd()
    print("Switched to direc =", chg_path)

    # delete the files that are not required
    delete_files(chg_path)
    for attempt in range(retry_attempts):
    #while attempt < retry_attempts:
        try:
            # Authenticating the given credentials
            ftp = ftplib.FTP(ftp_host, ftp_user, ftp_pass)

            # force UTF-8 encoding
            ftp.encoding = "utf-8"

            # the name of the file you want to download from the FTP server
            ftp.cwd(ftp_file_path)
            ftp.retrlines('LIST')
            with open(ftp_file, "wb") as file:
                # use FTP's RETR command to download the file
                ftp.retrbinary(f"RETR {ftp_file}", file.write)

            print("Successfully downloaded firmware")

        

            zip_file_path = "../" + path + "/" + ftp_file
            try:
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    for member in zip_ref.namelist():
                        filename = os.path.basename(member)
                        if filename:
                            extracted_path = zip_ref.extract(member)
                            os.rename(extracted_path, os.path.join(
                                os.getcwd(), filename))
                    print('Extraction successful.')

                print("current path =",os.getcwd())
                #shutil.rmtree(fvr_dir_name)
                #os.rmdir(fvr_dir_name)
                #res_path = "./"
                os.remove(zip_file_path)

            except Exception as e:
                print('Error:', str(e))
                log_exception(e)
                #return

            # file validation by CRC calculation
            try:
                with open(checksum_sender_file, "r") as f:
                    checksum_value = f.read()
                print("sender check sum value", checksum_value)
                checksum_value_rec = calculate_crc(cur_fvr_file)
                print("recevied check sum value", checksum_value_rec)
                if str(checksum_value_rec) == str(checksum_value):
                    print("file is in good condition")
            
                    database_file_check(database_filename,database_path)
                    
                    #  create the marker file in current partition and write as active
                    with open(new_marker_file, "w") as file:
                        file.write("ACTIVE")
                    print("ACTIVE status written to the marker file")

                    # if the old_partition is partition_def not required to check for the marker file, directly run the bootloader
                    if old_partition_index == 0:
                        print("Intiated to reboot the system to run the firmware file")
                        break
                        #init_bootloader()

                    # other than the partition_def we should clear the marker file status of old partition
                    else:
                        if old_partition_index == 1:
                            old_process_marker_file = "../" + \
                                partitions[1] + "/marker.txt"
                            with open(old_process_marker_file, "w") as file:
                                file.truncate(0)
                            print("old process marker file status erased successfully")
                            
                        elif old_partition_index == 2:
                            old_process_marker_file = "../" + \
                                partitions[2] + "/marker.txt"
                            with open(old_process_marker_file, "w") as file:
                                file.truncate(0)
                            
                        print("old process marker file status erased successfully")
                        break
                        #init_bootloader()
                else:
                    print("File corrupted,so returning to main")

            except Exception as e:
                print("Error :",str(e))
                log_exception(e)

        except Exception as e:
            print(f"FTP Error: {e}")
            attempt += 1
            print("Retrying left attempts are ",retry_attempts - attempt)
            log_exception(e)
            continue

        finally:
            # close the FTP server after downloading or in case of an exception
            ftp.quit()


# function is used to delete the files present in the folder to download the firmware
def delete_files(path):
    try:
        folder_path = str(path)

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"No file present for deleting")
        print("Deletion done")
    
    except Exception as e:
        print('Error:', str(e))
        log_exception(e)


def calculate_crc(cur_fvr_file):
    try:
        crc_func = crcmod.predefined.mkPredefinedCrcFun('crc-32')
        with open(cur_fvr_file, 'rb') as file:
            content = file.read()
            crc_value = crc_func(content)
            return crc_value
    
    except Exception as e:
        print('Error:', str(e))
        log_exception(e)

# check for the old database file then delete that and update the new database file which is unzipped during 
def database_file_check(database_filename,database_path):
    try:    
        if os.path.isdir("./" + database_filename)== True:
            print("database file is present in zip")
            log_event("database file is present in zip")
            # delete the old database file in the dependencies/database folder
            delete_files(database_path)
            # moved the new database file to the dependecies/database folder
            shutil.move(database_filename, database_path)

        else:
            print("database file not present in zip")
            log_event("database file not is present in zip")
    except Exception as e:
                print('Error:', str(e))
                log_exception(e)



def return_to_old_process():
    try:
        current_marker_path = os.getcwd()
        _, f = os.path.split(current_marker_path)
        cur_partition = partitions.index(f)

        # erasing the current partition marker file status
        with open("./marker.txt", "w") as file:
            file.truncate(0)

        if cur_partition == 1:
            # updating the status as "ACTIVE" in marker file for the old partition 
            with open("../" + partitions[2]+"/marker.txt", "w") as file:
                file.truncate(0)
                file.write("ACTIVE")
            
        elif cur_partition == 2:
            # updating the status as "ACTIVE" in marker file for the old partition
            with open("../" + partitions[1]+"/marker.txt", "w") as file:
                file.truncate(0)
                file.write("ACTIVE")

        # initiating the booatloader to run the active partition
        print("initiating the bootloader")
        log_event("initiating the bootloader")

    except Exception as e:
        print('Error:', str(e))
        log_exception(e)

def init_bootloader():
    try:
        n = os.getcwd()
        print(n)
        # adding the excutable permission for the gateway management firmware file
        os.chmod(upd_fvr_file, 0o755)
        print("Initating the bootloader to run the active partition firmware file")
        log_event("Initating the bootloader to run the active partition firmware file")

    except Exception as e:
        print("Error running firmware file", str(e))
        log_exception(e)
        # return to the old process after the getting the exception
        #return

############################################# CONTROL DATA COMMUNICATION ##############################################################################
# to check the gateway health status sent from the firware_management/health_check
# def gateway_health():
#     if health_ok() == True:
#         c_data["CDH"][1] = 1

#     else:
#         c_data["CDH"][1]= 0



def gateway_health():
    try:
        if health_ok() == False: 
            c_data["CDH"] = c_data["CDH"][0] + "1" + c_data["CDH"][2:]

        else:
            c_data["CDH"] = c_data["CDH"][0] + "0" + c_data["CDH"][2:]

    except Exception as e:
        print('Error:', str(e))
        log_exception(e)

def cntl_dat_resp_process(dat_resp_json):
    global glowfy_hub_fvr,ftp_file,old_fvr_store_var
    try:
        # Process the data received from the glowfy control plane
        #dat_resp_dict = json.loads(dat_resp_json)

        dat_resp_dict = json.loads(dat_resp_json)
        # these conditions is for disabling the service on request
        if c_data["CDH"][0] == "1" and dat_resp_dict["CCD"][0] == "0":
            print("in cond 1")
            c_data["CDH"] = "0" + c_data["CDH"][1:]
            print(c_data["CDH"],type(c_data["CDH"]))

        elif c_data["CDH"][0] == "0" and dat_resp_dict["CCD"][0] == "0":
            print("in cond 2")
            c_data["CDH"] = "0" + c_data["CDH"][1:]
            print(c_data["CDH"],type(c_data["CDH"]))

        elif c_data["CDH"][0] == "0" and dat_resp_dict["CCD"][0] == "1":
            print("in cond 3")
            c_data["CDH"] = "1" + c_data["CDH"][1:] 
            print(c_data["CDH"],type(c_data["CDH"]))

        if ((dat_resp_dict["DID"] == glowfy_dev_id) and (dat_resp_dict["DTP"] == glowfy_dev_typ) and (dat_resp_dict["MTP"] == "02")):
            if dat_resp_dict["CCD"][1] == "1":
                glowfy_hub_fvr = dat_resp_dict["FVR"]   
                ftp_file = glowfy_dev_typ + glowfy_hub_fvr + ".zip"
                new_fvr_version = dat_resp_dict['FVR']
                print(glowfy_hub_fvr)
                print(f"got firmware update & returning old_fvr_version = {old_fvr_version}, new_fvr_version={new_fvr_version}")

                # await firmware_management()
            else:
                # here updating the old firmware version value 
                old_fvr_store_var = dat_resp_dict['FVR'] 
                new_fvr_version = None
                print(f"no firmware update and returning old_fvr_version = {old_fvr_version}, new_fvr_version={new_fvr_version}")
                
        return old_fvr_store_var,new_fvr_version
    except Exception as e:
        print('Error:', str(e))
        log_exception(e)

        # these conditions is for disabling the service on request
        # if c_data["CDH"][0] == 1 and dat_resp_dict["CCD"][0] == 0:
        #     c_data["CDH"][0] = 0

        # elif  c_data["CDH"][0] == 0 and dat_resp_dict["CCD"][0] == 0:
        #     c_data["CDH"][0] = 0

        # elif c_data["CDH"][0] == 0 and dat_resp_dict["CCD"][0] == 1:
        #     c_data["CDH"][0] = 1 


def cntl_auth_resp_process(auth_resp_json):
    try:
        auth_resp_dict = json.loads(auth_resp_json)

        if ((auth_resp_dict["DID"] == glowfy_dev_id) and (auth_resp_dict["DTP"] == glowfy_dev_typ) and (auth_resp_dict["MTP"] == "04")):
            https_headers["Authorization"] = auth_resp_dict["TKN"]

        else:
            print("cntl_pln> DID or DTP unmatched")
    
    except Exception as e:
                print('Error:', str(e))
                log_exception(e)

def cntl_pln_commn():
    attempt = 0
    try:
        while True:
            if is_connected() is True:


                timestamp = int(time.time())
                if cntl_pln_url_sel[0] == 1:
                    t_data["TSP"] = str(timestamp)
                    data_json = json.dumps(t_data)
                else:
                    c_data["TSP"] = str(timestamp)
                    # to check the gateway health status sent from the
                    gateway_health()
                    data_json = json.dumps(c_data)

                try:
                    r = requests.post(
                        cntl_pln_urls[cntl_pln_url_sel[0]], headers=https_headers, data=data_json, timeout=30)
                    print(r.text)
                    print(r.status_code)
                    req_text = r.text
                    if r.status_code == 200:
                        if cntl_pln_url_sel[0] == 1:
                            cntl_auth_resp_process(r.text)
                            cntl_pln_url_sel[0] = 0
                        else:

                            old_ver,new_ver= cntl_dat_resp_process(r.text)
                            file_path = os.path.join(firmware_version, 'version.txt')
                            os.makedirs(firmware_version, exist_ok=True)

                            with open (file_path,'w') as file:
                                file.write(f"version:{old_ver}\nupdate:{new_ver}")

                            time.sleep(cloud_push_interval)

                    elif r.status_code == 401:
                        cntl_pln_url_sel[0] = 1
                        

                    else:
                            if attempt < 3:
                                cntl_pln_url_sel[0] = 0
                                attempt+=1
                                print(f"Retrying and attempts left =",attempt)

                            else:
                                print("Maximum retry attempts reached. return to old process...")
                                
                    # internetflag= True
                        # break
                except Exception as e:
                    log_exception("\nCloud Module> Send Error no internet")
                    internetflag= False
                    

                # break
            else:
                pass
                
    except Exception as e:
        print(" Send Error, Try:", str(e))
        log_exception(e)
        

############################################### Kill Process ###############################################################################
def kill_process(process_name):
    try:
        # iterating through each instance of the process
        for line in os.popen("ps ax | grep " + process_name + " | grep -v grep"):
            fields = line.split()
            print(fields)
            # extracting Process ID from the output
            pid = int(fields[0])
            # terminating process
            # changes made on 22-06-2023 for checking the kill process working
            try:
                os.kill(pid, signal.SIGTERM)
                # print("successfully terminated")
                cntl_pln_commn()
            except Exception as e:
                print("Error occurred while killing the process:")
                log_exception(e)
    except Exception as e:
        print("Error Encountered while running script")
        log_exception(e)
#########################################################################################################################################
def version_from_file():
    file_path = os.path.join(firmware_version, 'version.txt')
    with open (file_path , "r") as file:
        content = file.read()
    version_pattern = r"version:(\S+)"
    update_pattern = r"update:(\S+)"

    # Search for patterns in the text
    version_match = re.search(version_pattern, content)
    update_match = re.search(update_pattern, content)

    # Extract values if patterns are found
    version = version_match.group(1) if version_match else None
    update = update_match.group(1) if update_match else None

    return version,update
# def main():
#     kill_process("supervisor.py")
#     cntl_pln_commn()


# if __name__ == '__main__':
#   main()

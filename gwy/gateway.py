from protocols.uart_BLE import *
from constant.json_string_skeleton import BLE_start,okay,connected
from peripherals.led import *
from backup.backupftp import create_directory_on_ftp
from constant.ftpconstant import *
from firmware_mgnt.log_management import *
from device_database.group_database import update_or_insert_row
from constant.databaseconstant import glowfydb
from threading import Event
from constant.button_constant import config_timeout
import signal
import socket
# from constant.uart_constant import *

conf_flag= False


def timeout_handler(signum, frame):
    raise TimeoutError("Function execution timed out")


signal.signal(signal.SIGALRM, timeout_handler)



uart_mutex = threading.Lock()

# This code is establishing a connection to a SQLite database file located at


# The function `create_directory_on_ftp` is creating a directory on an FTP server.
try:
    create_directory_on_ftp(ftp_server,ftp_username,ftp_password,remote_gwy_folder)
except Exception as e:
    log_exception(e) 

def Gwy_function(bridge):
    """
    The function `Gwy_function` handles the process of pairing a device, receiving configuration
    packets, storing the data in a database, and performing normal working operations.
    """
    global conf_flag
    try_count = 0
    log_event("gateway configuration started")
    try:
        
        Gwy_Pairing_Mode()

        while True:
            time.sleep(0.1)
            
            BLE_advertisement(BLE_start)
            
            
           
            if(check_response_pkt(bridge) is okay):
                   
                
                if(device_connected(bridge) is connected):
                    
                    while True:
                        try:
                            
                            ssid,password,MQTT_server,MQTT_port,MQTT_username,MQTT_password,sts,connection = recieve_config_packet()
                            Wifi_Cred = "WIFI_CREDENTIALS"
                            columns_wifi = ["SSID","Password","flag"]
                            flag = "SET"
                            data_wifi = [ssid,password,flag]
                            update_or_insert_row(glowfydb,Wifi_Cred,columns_wifi,data_wifi)
                    
                            Mqtt_Cred ="MQTT_CREDENTIALS"
                            columns_mqtt = ["MQTT_Username","MQTT_Password","MQTT_Server","MQTT_Port"]
                            data_mqtt = [MQTT_username,MQTT_password,MQTT_server,MQTT_port]
                            update_or_insert_row(glowfydb,Mqtt_Cred,columns_mqtt,data_mqtt)
                            
                           
                        except Exception as e:
                            log_exception(e)
                            log_debug(f"error gat{e}")
                            return 1
                        if sts is okay:

                            config_response_pkt(recived_config_pkt)
                            time.sleep(1)
                            
                            BLE_advertisement(BLE_stop)
                            
                            time.sleep(.5)

                            if(check_response_pkt(bridge) is okay):
                                log_debug("advertising stopped")
                                log_event("avdertising stopped")
                                bridge.set()
                                conf_flag = False
                                normal_working()
                                bridge.clear() 
                                return 0
                        else:
                            config_response_pkt(error_in_config)
                           
                            
                            continue
                elif(device_connected(bridge) == 1 ):
                    
                    log_debug("function timed out1")
                    time.sleep(0.1)
                    BLE_advertisement(BLE_stop)
                    if(check_response_pkt(bridge) is okay):
                        log_debug("advertising stopped")
                        conf_flag = False
                        normal_working()
                        bridge.clear()
                        return 1 
                else:
                    
                    continue
            elif(check_response_pkt(bridge) == 1):
                    
                    log_debug("function timed out2")
                    normal_working()
                    time.sleep(0.1)   
                    BLE_advertisement(BLE_stop)
                    if(check_response_pkt(bridge) is okay):
                        log_debug("advertising stopped")
                        normal_working()
                        conf_flag=False
                        bridge.clear()
                        return 1
            else:
                continue
        

    except Exception as e:
        log_debug(f"An exception occurred:{e}")
        log_exception(e)


def is_connected():

    # The function checks if the device is connected to the internet by attempting to connect to a known host.
 
    try:
        # Attempt to connect to a known host
        socket.create_connection(("www.example.com", 80))
        return True
    except OSError:
        
        return False



def uart_read_function():
    """
    The function `uart_read_function` reads data from a UART connection and performs certain actions
    based on the received data.
    """
    network_flag = False

    log_debug("started uart scanning...")

    normal_working()
    while ble_uart.in_waiting ==0:

        time.sleep(0.1)
        pass
    while True:
        if is_connected() is True and network_flag is False:
            network_flag =True
            normal_working()
        if is_connected() is False and network_flag is True:
            Trying_to_con_wifi()
            network_flag = False
        time.sleep(0.1)
        try:
            if(conf_flag ==False):
                    
                if (ble_uart.in_waiting > 0):

                    data_val = ble_uart.read(ble_uart.in_waiting).decode('ascii')
                    # data_val = ble_uart.readline()
                    try:
                        read_data = json.loads(data_val)
                        msg = read_data[messagetype_key]


                        if (msg == status_check):
                            status()
                        if (msg == restart_gwy):
                            restart()
                        if (msg == poweroff_gwy):
                            poweroff()
                    except json.JSONDecodeError:
                        log_debug("json invalid uart read")
                        continue
                    ble_uart.reset_input_buffer()
                    time.sleep(0.1)
        except Exception as e:
            log_debug(f"An exception occurred:{e}")
            log_exception(e)
            continue
        time.sleep(0.1)


def config_initiator(queue):
        global conf_flag
        
        
        log_debug("conf thread...")
        while True:
            button = queue.get()
            try:
                if(button==0):
                    conf_flag= True
                    try:
                        bridge = Event()
                        t1 = threading.Thread(target=Gwy_function,args=(bridge,))
                        t1.start()
                        t1.join(config_timeout)
                        bridge.set()
                    except Exception as e:
                        log_debug(e)
                    log_debug(f"conf_flag:{conf_flag}")

                    
            except Exception as e:
                pass
            time.sleep(0.1)
            pass
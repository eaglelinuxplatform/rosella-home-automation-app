import serial
import serial.serialutil
import json
import time
from constant.uart_constant import serial_port,baud_rate
from constant.json_string_skeleton import * 
from peripherals.led import *
from firmware_mgnt.log_management import *
import threading


tries=0
mutex_lock = threading.Lock()
while True:
    try:
        ble_uart = serial.Serial(serial_port, baud_rate)
        break
    except Exception as e:
        log_debug(f"An exception occurred:{e}")
        continue
ble_pkt = json.loads(json_string_ble) 
ble_report_pkt = json.loads(json_string_reporting)

def BLE_advertisement(message):

    # The function `BLE_advertisement` sends a Bluetooth Low Energy (BLE) advertisement message using a
    # UART connection.
    
    try:
        
        ble_pkt[messagetype_key] = start_or_stop
        ble_pkt[Bluetooth_key] = message
        ble_pkt[dev_name_key] = Gateway_name
        
        time.sleep(0.1)
        log_debug("inside ble")
    
        updated_json = json.dumps(ble_pkt,separators=(',', ':'))
        log_debug(updated_json)
        try:
            # mutex_lock.acquire()
            ble_uart.write(updated_json.encode())
            log_debug("{} ble advertising".format(message))
            log_event("{} ble advertising".format(message))
            time.sleep(0.1)
            ble_uart.reset_output_buffer()
            # mutex_lock.release()
            return 0 
        except serial.SerialException as e:
            log_debug("Error in writing to uart")
            # mutex_lock.release()
            log_debug(e)
            
    except Exception as e:
        log_debug(f"An exception occurred:{e}")
        # mutex_lock.release()
        log_exception(e)

def check_response_pkt(bridge):

    # The function `check_response_pkt()` reads data from a Bluetooth Low Energy (BLE) device, parses it
    # as JSON, and checks the message type and status to determine if the response is valid or an error.
    # :return: either "okay" or "error" based on the conditions inside the try block.
    log_debug("response")
    try:
        
        # tries =+1
        while ble_uart.in_waiting == 0:
            time.sleep(0.1)
            # if(tries==1):
            #     if bridge.is_set():
            #         return 1
            # else:
            #     tries=0
            pass
        
        
        if(ble_uart.in_waiting>0):   
            log_debug("inside response")
            # mutex_lock.acquire()

            try:
                data = ble_uart.read(ble_uart.in_waiting)
            except UnicodeDecodeError as e:
                # Handle the error, e.g., by log_debuging a message or using a different encoding
                log_debug(f"UnicodeDecodeError: {e}")
            # mutex_lock.release()
            # mutex_lock.acquire()
            # data= ble_uart.readline()
            # mutex_lock.release()
            
            time.sleep(0.1)
            try:
                log_debug(data)
                read_data = json.loads(data)
                log_debug(read_data)
                time.sleep(0.1)
                ble_uart.reset_input_buffer()
                messagetype = read_data[messagetype_key]
                status = read_data[status_key]
                if(messagetype == status_pkt and status == recieved_ok):
                    log_debug("recieved okay")
                    # mutex_lock.release()
                    return okay
                elif(messagetype==poweroff_gwy):
                    poweroff()
                    log_debug("recieved error")
                    # mutex_lock.release()
                    return error
                elif(messagetype==restart_gwy):
                    restart()
                    log_debug("recieved error")
                    # mutex_lock.release()
                    return error
                elif(messagetype=='03'):
                    log_debug("recieved error")
                    # mutex_lock.release()
                    return error
                

            except Exception as e:
                log_debug("Invalid json")
                log_exception(e)
                # mutex_lock.release()
                return error

    except Exception as e:
        log_debug(f"An exception occurred:{e}")
        # mutex_lock.release()
        log_exception(e)
        return error


def check_json(p, attr):
 
    # The function `check_json` checks if a given attribute exists in a JSON object.
    

    doc = json.loads(json.dumps(p))
    try:
        # we don't care if the value exists. Only that 'get()' is accessible
        doc.get(attr)
        return True
    except AttributeError:
        return False

def recieve_config_packet():

    # The function `recieve_config_packet()` reads data from a Bluetooth Low Energy (BLE) UART and
    # processes it based on the message type.
  
    try:
        
        while True:
            # mutex_lock.acquire()
            while ble_uart.in_waiting == 0:
                time.sleep(0.1)
 
                pass
            if(ble_uart.in_waiting>0):
                # mutex_lock.acquire()
                data = ble_uart.read(ble_uart.in_waiting).decode('ascii')
                
                # mutex_lock.release()
                
                log_debug(data)
                try:
                    read_data = json.loads(data)
                    log_debug(read_data)
                    time.sleep(0.1)
                    ble_uart.reset_input_buffer()
                    messagetype = read_data[messagetype_key]
                    if(messagetype == config_param):
                        if (check_json(read_data, messagetype) &
                        check_json(read_data, SSID_key) &
                        check_json(read_data, password_key) &
                        check_json(read_data, server_key) &
                        check_json(read_data, port_key) &
                        check_json(read_data, mqtt_username_key) &
                        check_json(read_data, mqtt_password)&
                        check_json(read_data, connection_type)):
                            ssid = read_data[SSID_key]
                            Password = read_data[password_key]
                            MQTT_Server = read_data[server_key]
                            MQTT_Port = read_data[port_key]
                            MQTT_Username = read_data[mqtt_username_key]
                            MQTT_Password = read_data[mqtt_password]
                            CTP = read_data[connection_type]
                            # mutex_lock.release()
                            return ssid,Password,MQTT_Server,MQTT_Port,MQTT_Username,MQTT_Password,okay,CTP
                        
                        else:
                            # mutex_lock.release()
                            continue
                    elif(messagetype==poweroff_gwy):
                        # mutex_lock.release()
                        poweroff()
                        continue
                    elif(messagetype==restart_gwy):
                        # mutex_lock.release()
                        restart()
                        continue
                    else:
                        # mutex_lock.release()
                        continue

                except Exception as e:
                    # mutex_lock.release()
                    log_debug(f"An exception occurred:{e}")
                    log_exception(e)
                    
                
    except Exception as e:
        log_debug(f"An exception occurred:{e}")
        log_exception(e)
        

    
    
def config_response_pkt(status):

    # The function `config_response_pkt` sends a JSON-encoded packet over a BLE UART connection with a
    # specified status.
    

    ble_report_pkt[messagetype_key] = report_pkt
    ble_report_pkt[status_key] = status
    while True:
        try:
            updated_json = json.dumps(ble_report_pkt, separators=(',', ':'))
            try:
                # mutex_lock.acquire()
                ble_uart.write(updated_json.encode())
                # mutex_lock.release()
                break
            except serial.SerialException:
                log_debug("Serial Error")
                log_exception(serial.SerialException)
                continue
        except Exception as e:
            log_debug(f"An exception occurred:{e}")
            log_exception(e)

def device_connected(bridge):

    # The function `device_connected` checks if a device is connected by reading data from a Bluetooth Low
    # Energy (BLE) UART and parsing it to determine the message type.
   
    
    try:
        # mutex_lock.acquire()
        while ble_uart.in_waiting == 0:
            time.sleep(0.1)
            if bridge.is_set():
                log_debug("timed out")
                return 1
            pass
        # if(ble_uart.in_waiting>0):
            
            # data = ble_uart.read(size=12)
        data = ble_uart.read(ble_uart.in_waiting).decode('ascii')
        log_debug(data)
        try:
            read_data = json.loads(data)
            log_debug(read_data)
            messagetype = read_data[messagetype_key]
            if (messagetype == dev_connected):
                log_debug("device connected")
                # mutex_lock.release()
                return connected
            elif(messagetype==poweroff_gwy):
                poweroff()
                log_debug("device not connected")
                # mutex_lock.release()
                return not_connected
            elif(messagetype==restart_gwy):
                restart()
                log_debug("device not connected")
                # mutex_lock.release()
                return not_connected
            else:
                log_debug("device not connected")
                # mutex_lock.release()
                return not_connected                

        except Exception as e:
            log_debug(f"An exception occurred:{e}")
            log_exception(e)
            # mutex_lock.release()
            return error
    except Exception as e:
        log_debug(f"An exception occurred:{e}")
        log_exception(e)
        return error  
   

def status():
    """
    The function `status()` sends a JSON-encoded status report over a BLE UART connection.
    """
    try:
        ble_report_pkt[messagetype_key] = report_pkt
        ble_report_pkt[status_key] = working_fine
        updated_json = json.dumps(ble_report_pkt, separators=(',', ':'))
        log_debug(updated_json)

        try:
            ble_uart.write(updated_json.encode())
            time.sleep(0.1)
            log_debug("status")
        except serial.SerialException:
            log_debug("serial error")

    except Exception as e:
        log_debug(f"An exception occurred:{e}")
        log_exception(e)

def restart():
    """
    The function `restart()` sends a JSON-encoded packet over a UART connection and then restarts the
    gateway.
    """
    log_event("Restart initiated")
    try:
        ble_report_pkt[messagetype_key] = report_pkt
        ble_report_pkt[status_key] = working_fine
        updated_json = json.dumps(ble_report_pkt, separators=(',', ':'))
        log_debug(updated_json)

        try:
            ble_uart.write(updated_json.encode())
            time.sleep(0.1)
            #os.system("sudo reboot")
            log_debug("restart gateway")
        except serial.SerialException:
            log_debug("serial error")

    except Exception as e:
        log_debug(f"An exception occurred:{e}")
        log_exception(e)

def poweroff():
    """
    The function `poweroff()` sends a JSON-encoded report packet over BLE UART and then initiates a
    poweroff command.
    """
    log_event("poweroff initiated")
    try:
        ble_report_pkt[messagetype_key] = report_pkt
        ble_report_pkt[status_key] = working_fine
        updated_json = json.dumps(ble_report_pkt, separators=(',', ':'))
        log_debug(updated_json)

        try:
            ble_uart.write(updated_json.encode())
            time.sleep(0.1)
            #os.system("sudo poweroff")
            log_debug("poweroff")
        except serial.SerialException:
            log_debug("serial error")

    except Exception as e:
        log_debug(f"An exception occurred:{e}") 
        log_exception(e)


# def uart_read_function():
#     """
#     The function `uart_read_function` reads data from a UART connection and performs certain actions
#     based on the received data.
#     """
   

#     log_debug("started uart scanning...")

#     normal_working()
#     while ble_uart.in_waiting ==0:
#         time.sleep(0.1)
#         pass
#     while True:
#         time.sleep(0.1)
#         try:
#             if (ble_uart.in_waiting > 0):

#                 data_val = ble_uart.read(ble_uart.in_waiting).decode('ascii')
#                 # data_val = ble_uart.readline()
#                 try:
#                     read_data = json.loads(data_val)
#                     msg = read_data[messagetype_key]

#                     if (msg == status_check):
#                         status()
#                     if (msg == restart_gwy):
#                         restart()
#                     if (msg == poweroff_gwy):
#                         poweroff()
#                 except json.JSONDecodeError:
#                     log_debug("json invalid uart read")
#                     continue
#                 ble_uart.reset_input_buffer()
#                 time.sleep(0.1)
#         except Exception as e:
#             print(f"An exception occurred:{e}")
#             log_exception(e)
#             continue
#         time.sleep(0.1)
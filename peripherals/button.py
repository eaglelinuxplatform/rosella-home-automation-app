from evdev import InputDevice, categorize, ecodes
from constant.button_constant import button_path
from gwy.gateway import Gwy_function
from protocols.uart_BLE import BLE_advertisement,check_response_pkt
from constant.json_string_skeleton import BLE_stop,okay
from peripherals.led import *
import time
from firmware_mgnt.factory_reset import factory_reset
import paho.mqtt.client as mqtt
from constant.mac_id import mac_address
from constant.mqtt_constant import*
from firmware_mgnt.log_management import *
from constant.uart_constant import uart_lock

# lock = threading.Lock()


try:
    dev = InputDevice(button_path)
    LONG_PRESS_THRESHOLD = 5
    client = mqtt.Client(client_id=mac_address, clean_session=False,userdata=False)
    log_debug(dev)
except Exception as e:
     log_debug(e)






# Define time thresholds

def button(queue):
    """
    The above function is a Python function that handles button events, including
    detecting button presses, releases, long presses, and double presses, and performs certain actions
    based on these events.
    """
    
    button_pressed = False
    elapsed_time1 = 0
    count=0
    temp=0
    # mutex = threading.Lock()
    log_debug("button thread")
    try:
        for event in dev.async_read_loop():
                time.sleep(0.1)
                try:      
                    if event.type == ecodes.EV_KEY:
                        
                        
                        #log_debug(categorize(event))
                            if event.value == 0:
                                button_pressed=True
                                #log_debug("Button pressed")
                                log_debug(event.value)
                                press_time=event.timestamp()
                                #log_debug("press_time=""{}".format(press_time))
                                start_time = time.time()  # Start the timer


                            elif button_pressed & event.value == 1:
                                
                                elapsed_time1=temp
                                button_pressed=False
                                #log_debug("Button released")
                                release_time=event.timestamp()
                                #log_debug( "release_time=""{}".format(release_time))
                                temp = release_time
                                
                            
                                if(release_time-press_time>5):
                                    
                                    log_debug("long press detected")
                                    log_event("long press detected")
                                    if(factory_reset()==0):
                                        os.system("sudo reboot")
                                        pass
                                elif(release_time-press_time<1):
                                    log_debug("short press")
                                    
                                    try:
                                        queue.put(0)
                                        pass
                                    except Exception as e:
                                        log_debug(f"An exception occurred:{e}")
                                        log_exception(e)

                                if(release_time - press_time) <= 1 and press_time-elapsed_time1<1:
                                    count += 1
                                    if count >= 1:
                                         log_debug("double press")
                                
                except Exception as e:
                    log_debug(f"An exception occurred:{e}")
                    log_exception(e)
    except Exception as e:
        log_debug(f"An exception occurred:{e}")
        log_exception(e)    


            

                       
            

                



                    


                    

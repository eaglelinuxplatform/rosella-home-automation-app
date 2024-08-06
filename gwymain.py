from gwy.gateway import Gwy_function
from peripherals.button import button
from peripherals.led import *
from gwy.gateway import uart_read_function, config_initiator
from protocols.mqttcom import mqttmain, mqtt_listener, subscribe_on_start, client
from constant.gateway_mgnt_constant import counter_file_path
from firmware_mgnt.gateway_management import cntl_pln_commn
from firmware_mgnt.restart_counter import *
from firmware_mgnt.log_management import *
from constant.databaseconstant import scene_file
from threading import Event, Lock, Thread
from scenes.scenes import scheduler_1
import queue


queue_ = queue.Queue()

start_count()
subscribe_on_start(scene_file, client)
try:
    counter_value = get_counter_value(counter_file_path)
    log_event("Programme started with counter at {}".format(counter_value))
except Exception as e:
    log_exception(e)
    log_debug("An error occured:", e)


# The lines of code you mentioned are creating threads for different functions in the program.
try:
    uart_read_thread = Thread(target=uart_read_function)
    button_thread = Thread(target=button, args=(queue_,))
    mqtt_thread = Thread(target=mqttmain)
    ota_thread = Thread(target=cntl_pln_commn)
    config_thread = Thread(target=config_initiator, args=(queue_,))
    mqtt_listener_thread = Thread(target=mqtt_listener)
except Exception as e:
    log_debug(e)
# The `main()` function is the entry point of the program. It sets the value of the `config` variable
# to `'set'` and then executes a series of actions based on the value of `config`.


def main():
    config = 'set'
    try:
        # The code block you mentioned is checking the value of the `config` variable. If `config` is equal to
        # `'unset'`, it creates an `Event` object called `bridge`, calls the `Gwy_function` with `bridge` as
        # an argument, and then starts four threads: `uart_read_thread`, `button_thread`, `mqtt_thread`, and
        # `ota_thread`.
        if (config == 'unset'):
            bridge = Event()

            Gwy_function(bridge)
            normal_working()
        uart_read_thread.start()
        button_thread.start()
        mqtt_thread.start()
        ota_thread.start()
        config_thread.start()
        mqtt_listener_thread.start()
        print("scheduler about to start")
        scheduler_1.start()
        print("scheduler started")

    except Exception as e:
        log_debug("An Exception occured:", e)
        log_exception(e)


if __name__ == '__main__':

    main()

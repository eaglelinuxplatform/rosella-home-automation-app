import os

def LED_Blinking(on_delay,off_delay,led):
    """
    The function `LED_Blinking` sets the on and off delay for a specified LED and triggers it to start
    blinking.
    
    :param on_delay: The on_delay parameter specifies the duration in milliseconds for which the LED
    should be turned on during each cycle of blinking
    :param off_delay: The off_delay parameter is the duration in milliseconds for which the LED will
    remain off before turning on again
    :param led: The "led" parameter is the name of the LED device that you want to control. It should be
    a string representing the LED device's name, such as "led0" or "led1"
    """
    os.system('sudo echo "timer" > /sys/class/leds/{}/trigger'.format(led))
    os.system('sudo echo "{}" > /sys/class/leds/{}/delay_on'.format(on_delay,led))
    os.system('sudo echo "{}" > /sys/class/leds/{}/delay_off'.format(off_delay,led))


def LED_ON_OR_OFF(brightness,led):
    """
    The function `LED_ON_OR_OFF` sets the brightness of an LED to a specified value.
    
    :param brightness: The brightness parameter is the value that determines the intensity of the LED
    light. It can range from 0 (off) to 255 (full brightness)
    :param led: The "led" parameter is the name of the LED device that you want to control. It should be
    a string representing the LED device's name, such as "led0" or "led1"
    """
    '''255-ON ,0-OFF'''
    os.system('sudo echo "none" > /sys/class/leds/{}/trigger'.format(led))
    os.system('sudo echo "{}" > /sys/class/leds/{}/brightness'.format(brightness,led))    

def Gwy_Pairing_Mode():
    """
    The function Gwy_Pairing_Mode() blinks an LED with a frequency of 1 Hz.
    """
    LED_Blinking(1000,1000,'led1')


def Trying_to_con_wifi():
    """
    The function "Trying_to_con_wifi" attempts to connect to a WiFi network.
    """
    LED_Blinking(500,500,'led1')
def Trying_to_con_server():
    """
    The function "Trying_to_con_server" calls the "LED_Blinking" function with specific parameters.
    """
    LED_Blinking(2000,500,'led1')
def normal_working():
    """
    The function "normal_working" calls the "LED_ON_OR_OFF" function with the arguments 255 and 'led1'.
    """
    LED_ON_OR_OFF(255,'led1')

def node_pairing_mode():
    """
    The function `node_pairing_mode` blinks an LED connected to 'led2' with a 1 second on and 1 second
    off pattern.
    """
    LED_Blinking(1000,1000,'led3')
def node_normal_working():
    """
    The function `node_normal_working` turns on or off an LED with a brightness level of 255.
    """
    LED_ON_OR_OFF(255,'led3')
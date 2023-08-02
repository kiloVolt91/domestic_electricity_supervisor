from umodbus.serial import Serial as ModbusRTUMaster
from umqtt.simple import MQTTClient
from machine import Pin
import utime
import network
import urandom
from init import *

holding_registers = {    #REGISTER ADDRESS : REGISTER NAME [MEASURE UNIT]  
    0:'Voltage [0.1V]',  
    1:'Current [0.1A]',  
    2:'Frequency [0.1Hz]', 
    3:'Active Power [W]', 
    4:'Reactive Power [var]', 
    5:'Apparent Power [VA]', 
    6:'Power Factor [0.001]',
    7:'Active Energy [Wh]', # reg 7-8, Decimal Long - little endian
    9:'Reactive Energy [varh]' # reg 9-10, Decimal Long - little endian
    }

def mqtt_client_connection(mqtt_host, mqtt_username,mqtt_password):
    global mqtt_client
    while True:
        random_number = urandom.randint(0,10000)
        try:
            mqtt_client_id = "RaspPicoW_"+str(random_number)
            mqtt_client = MQTTClient(
                client_id=mqtt_client_id,
                server=mqtt_host,
                user=mqtt_username,
                password=mqtt_password)
            #print('trying to connect to the MQTT server') #DEBUG LINE
            mqtt_client.connect()
            #print('client connected') #DEBUG LINE
            break
        except Exception as error:
            #print(str(error)) #DEBUG LINE
            break
        utime.sleep(2)
    return

def inizialize_board():
    ##PIN SETUP - RASPBERRY PI PICO W BOARD
    global rtu_pins, uart_id
    rtu_pins = (Pin(0), Pin(1))     # (TX, RX)
    uart_id = 0
    return

def connect_to_wifi():
    global wlan
    wlan = network.WLAN(network.STA_IF)
    while wlan.isconnected() == False:
        wlan.active(True)
        wlan.connect(wifi_ssid, wifi_password)
        #print('Waiting for connection...') # DEBUG LINE
        utime.sleep(2)
        wlan.active(False)
        utime.sleep(2)
    #print("Connected to WiFi") #DEBUG LINE
    return

def get_modbus_data(rtu_pins, uart_id):
    host = ModbusRTUMaster(
        pins=rtu_pins,
        uart_id=uart_id       
    )
    hregs_values = []
    for i in range(0,7):
        # print(i) #DEBUG LINE
        try:
            value = host.read_holding_registers(slave_addr=1, starting_addr=i, register_qty= 1, signed= False)
            hregs_values.append(value[0])
        except Exception as error:
            hregs_values.append('nan')
    for i in range(7,11,2):
        #print(i) #DEBUG LINE
        try:
            value = host.read_holding_registers(slave_addr=1, starting_addr=i, register_qty= 2, signed= False) ## little-endian --> problem with umodbus.serial library converting the HEX value converting 2 WORDS?
                                                                                                    ## Does it need to read the HEX value and convert it? HEX within reg8 goes before HEX within reg7?
            hregs_values.append(value[0])
        except Exception as error:
            hregs_values.append('nan')          
    return hregs_values

def datalogger ():
    inizialize_board()
    connect_to_wifi()
    mqtt_client_connection(mqtt_host, mqtt_username,mqtt_password)
                
    while wlan.isconnected() == True:
        hregs_values = get_modbus_data(rtu_pins, uart_id)
        i=0
        #print(hregs_values) DEBUG LINE
        for value in hregs_values:
            val_name = holding_registers[i] 
            topic = mqtt_publish_topic+str(val_name)
            #print('publishing: ', value, topic) #DEBUG LINE
            mqtt_client.publish(topic, str(value))
            i+=1
            if i==8:
                i+=1
        utime.sleep(60)
    return

while True:
    try:
        datalogger()
    except Exception as error:
        #print(str(error)) #DEBUG LINE
        machine.reset()

from umodbus.serial import Serial as ModbusRTUMaster
from umqtt.simple import MQTTClient
from machine import Pin
import utime
import network
import urandom
from init import *

holding_registers = {    #REGISTER ADDRESS : REGISTER NAME [MEASURE UNIT]  
    0:'Voltage [V]',  #x10 multiplicative factor
    1:'Current [A]',  #x10 multiplicative factor
    2:'reg2', ##still investigating
    3:'reg3', ##still investigating
    4:'reg4', ##still investigating - probably Active Power [kW]
    5:'reg5', ##still investigating - probably Active Energy [kWh]
    6:'PowerFactor'   #x1000 multiplicative factor
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
            print('tentativo di connessione client')
            mqtt_client.connect()
            print('client connesso')
            break
        except Exception as error:
            print(str(error))
        utime.sleep(2)
    return

def inizialize_board():
    ##PIN SETUP - RASPBERRY PI PICO W BOARD
    global rtu_pins, uart_id
    rtu_pins = (Pin(0), Pin(1))     # (TX, RX)
    uart_id = 0
    return

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_ssid, wifi_password)
    c = 0
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        utime.sleep(1)
        c +=1
        if c == 10:
            wlan.connect(wifi_ssid, wifi_password)
            c = 0

    print("Connected to WiFi")
    return

def get_modbus_data(rtu_pins, uart_id):
    host = ModbusRTUMaster(
        pins=rtu_pins,
        uart_id=uart_id       
    )
    hregs_values = []
    for i in range(0,7): 
        try:
            value = host.read_holding_registers(slave_addr=1, starting_addr=i, register_qty= 1, signed= False)
            hregs_values.append(value[0])
        except Exception as error:
            hregs_values.append('nan')
    return hregs_values
            
inizialize_board()
connect_to_wifi()
mqtt_client_connection(mqtt_host, mqtt_username,mqtt_password)

            
while True:
    hregs_values = get_modbus_data(rtu_pins, uart_id)
    i=0
    print(hregs_values)
    for valore in hregs_values:
        val_name = holding_registers[i] 
        topic = mqtt_publish_topic+str(val_name)
        print('pubblico: ', valore, topic)
        mqtt_client.publish(topic, str(valore))
        i+=1
    utime.sleep(60)

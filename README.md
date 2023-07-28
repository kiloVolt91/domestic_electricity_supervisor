# home_electrical_parameters_monitor
 Datalogger based on "Raspberry PI Pico W" and on the energy meter Orno OR-WE-504 which also measures the main electrical parameters providing all these information through a RS485 serial port using the Modbus RTU protocol.
 
Project based on the microcontroller Raspberry PI Pico W and microPython.
The microcontroller uses "UART0" ports (Pin0 - TX and Pin1 -RX) for communicating, through a RS485 to TTL converter, with the serial port of the energy meter Orno OR-WE-504.
The energy meter Orno OR-WE-504 uses the Modbus RTU communication standard, making the data accessible through the holding registers, which are reachable by Raspberry PI Pico W using the "umodbus.serial" library.
The microcontroller acts as a "Master", querying reads from the energy meter which acts as a "Slave".
All the datas are uploaded to a MQTT server using the "umqtt.simple" library.
The interface between Master and Slave consist of a RS485 to TTL converter. It takes the A-B signals from the RS485 port of the energy meter and convert them into a TTL signal. The Output is linked to the TX and RX ports of the microcontroller. The raspberry also provides the energy supply needeed by the interface, linking the 3.3V and GND pins to the converter.
The Raspberry PI Pico needs 5V power supply provided by the micro-USB port. 

N.B. the energy meter OR-WE-504 is sized to read up to electric currents of 80A (with a base current of 5A). The choice fell on it due to its cheap cost (around 30€ on Amazon) and due to be one of the few with a Modbus RTU protocol on board. Due to the work-in-progress nature of the project, the possible lack of accuracy using the energy meter with much lower currents is still under monitoring. 
This repository is still a "pilot project" with the main purpose of better understand the tools and their limits.
Also the measure units are still under study (a x10 factor is actually active on Voltage and Current)
Instead of "investigate" the parameters is also possible set-up the modbus slave's holding registers using a RS485 to USB converter through the program provided by ORNO at the product link.

Orno OR-WE-504 product link: https://orno.pl/en/product/1082/1-phase-energy-meter-wtih-rs-485-80a

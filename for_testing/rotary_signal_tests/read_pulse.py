from gpiozero import DigitalInputDevice
import time

#Looking at the rotary board head on, the leftmost wire should be connected to GND, the middle one is pin_1, and the rightmot one is pin_2
pin_1 = 27
inp_1 = DigitalInputDevice(pin_1, pull_up=False)

pin_2=22
inp_2=DigitalInputDevice(pin_2,pull_up=False)

while True:
#       print("input 1:", inp_1.value, "inpu 2:", inp_2.value)
	do_print=0
	while inp_2.value:
		do_print=1
	if do_print==1:
		print("pulsed")

from gpio_speech_body import *
from gpiozero import DigitalInputDevice
import os
pin = 4
inp = DigitalInputDevice(pin, pull_up=False)

#Waits for phone put down
def close_listener():
    while True:
        if not inp.value:
            print("Pin done!")
            ws_close()
            break

#def terminate_listener():
 #   prompt=input("Type stop to exit: ")
  #  while prompt.lower()!='stop':
   #     prompt=input("Type stop to exit: ")
    #close_audiostreams()
    #os._exit(0)

thread_run = threading.Thread(target=run_ws)
input_thread = threading.Thread(target=input_listener)

thread_run.start()
input_thread.start()
ws_close()
thread_run.join()
input_thread.join()


while True:
    #thread_terminate=threading.Thread(target=terminate_listener)
    #thread_terminate.start()

    print("Pick up the phone!")

    #Listens for phone pick up
    while True:
        if inp.value:
            break

    #plays dial tone
    thread_dial=threading.Thread(target=play_dial)
    thread_dial.start()

    #Starts websocket but only after the dial tone is finished
    thread_run_two = threading.Thread(target=run_ws)
    thread_dial.join()
    thread_run_two.start()

    time.sleep(1)
    # Start the input handler in its own thread
    input_thread_two = threading.Thread(target=input_listener)
    input_thread_two.start()

    #Listens for phone put down
    thread_close=threading.Thread(target=close_listener)
    thread_close.start()
 

    # Wait for all threads to finish before exiting
    thread_close.join()
    thread_run.join()
    input_thread.join()
    print("Program finished")

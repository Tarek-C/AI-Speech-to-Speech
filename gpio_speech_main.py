from gpio_speech_body import *
from gpiozero import DigitalInputDevice
pin = 4
inp = DigitalInputDevice(pin, pull_up=False)

#Waits for phone put down
def close_listener():
    while True:
        if not inp.value:
            print("Pin done!")
            ws_close()
            break

#Simulates phone pickup & putdown to resolve blank input bug on first pickup
thread_run_pre=threading.Thread(target=run_ws)
thread_run_pre.start()

input_thread_pre = threading.Thread(target=input_listener)
input_thread_pre.start()

ws_close()

thread_run_pre.join()
input_thread_pre.join()

while True:

    print("Pick up the phone!")

    #Listens for phone pick up
    while True:
        if inp.value:
            break

    #plays dial tone
    thread_dial=threading.Thread(target=play_dial)
    thread_dial.start()

    #Starts websocket but only after the dial tone is finished
    thread_run = threading.Thread(target=run_ws)
    thread_dial.join()
    thread_run.start()

    time.sleep(1)
    # Start the input handler in its own thread
    input_thread = threading.Thread(target=input_listener)
    input_thread.start()

    #Listens for phone put down
    thread_close=threading.Thread(target=close_listener)
    thread_close.start()
 

    # Wait for all threads to finish before exiting
    thread_close.join()
    thread_run.join()
    input_thread.join()
    print("Conversation finished")
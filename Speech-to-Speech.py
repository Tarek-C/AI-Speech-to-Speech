import json
import websocket
import time
import threading
import base64
import pyaudio

#Input openAI realtime API key
OPENAI_API_KEY=""

#Endpoint of the web socket, connect to here, model specified as gpt-realtime
url = "wss://api.openai.com/v1/realtime?model=gpt-realtime"

#For authorization in initial handshake to establish the websocket connection with the API
headers = ["Authorization: Bearer " + OPENAI_API_KEY]

#Runs when the web socket is opened successfully:
def on_open(ws):
    print("Connected to server.")

#Runs when the server (open AI) sends a message
#Can be used to log AI responses, message reception confirmations, the AI's configuration
def on_message(ws, message):
    #json.loads takes the JSON formatted string and converts it into a python dictionary
    #This makes it easier to parse
    data = json.loads(message)

    
    if data["type"]=="session.created":
        #JSON.dumps converts back into its original JSON string format as it's a neater output
        print("Initial Conditions:", json.dumps(data, indent=2))
   
    

    #Outputs text phrase by phrase (only if a text response is specified)
    if data["type"] == "response.output_text.delta":
        print(data["delta"], end="")
        
    #To process audio output (from the AI) phrase by phrase
    if data["type"] == "response.output_audio.delta":

        #Converts from base64 to raw PCM Audio bytes
        #Each sample is 16-bit PCM
        audio_bytes = base64.b64decode(data["delta"])  

        #Outputs audio to speakers   
        play_audio_chunk(audio_bytes)

def init_output_stream():
    global output_stream, p
    #Loads audio library
    p = pyaudio.PyAudio()

    #Opean AI realtime API works with 16bit PCM signals at a rate of 24kHz, mono
    #1024 frames per buffer is a conventional middleground size, can be adjusted as needed
    output_stream = p.open(format=pyaudio.paInt16, channels=1, rate=24000,
                          output=True, frames_per_buffer=1024)

def play_audio_chunk(audio_bytes):
    global output_stream
    output_stream.write(audio_bytes)

# Initialize the stream
init_output_stream()


ws = websocket.WebSocketApp(
    url, #End point of web socket
    header=headers, #Specifies header required for auth
    on_open=on_open, #Call on_open when opened
    on_message=on_message, #Call on_message when receiving a message from the server (openAI)
)

# Run the WebSocket in a separate thread
def run_ws():
    ws.run_forever()
    print("Websocket terminated")

thread_run = threading.Thread(target=run_ws)
thread_run.start()

#Define audio input formatting (Same as output formatting)
def init_input_stream():
    global input_stream
    p=pyaudio.PyAudio()
    input_stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=24000,
                    input=True,
                    frames_per_buffer=1024)
    
init_input_stream()


def microphone_thread(ws):
    #While the web socket connection is established
    while ws.sock and ws.sock.connected:
        #Read audio from mic 1024 frames at a time
        audio_chunk = input_stream.read(1024, exception_on_overflow=False)
        #Encodes PCM data into base 64 then formats that into JSON string
        audio_b64 = base64.b64encode(audio_chunk).decode()
        #Send the audio data over the websocket
        ws.send(json.dumps({
            "type": "input_audio_buffer.append",
            "audio": audio_b64
        }))
        

def input_listener():
        time.sleep(1)
        mic_thread = threading.Thread(target=microphone_thread, args=(ws,), daemon=True)
        mic_thread.start()
        user_text=""
        
        while user_text.lower()!="quit":
            user_text = input("Type 'quit' to stop: ")
        
        ws.close()

# Start the input listener in the main thread
input_listener()

# Wait for the websocket to terminate
thread_run.join()

print("Program finished")

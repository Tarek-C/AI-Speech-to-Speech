import json
import websocket
import time
import threading
import wave
import base64
import pyaudio
import numpy as np
from scipy.signal import resample

#Specifiy device indices for I/O and input device sampling rate, found by running audio_index.py in the for_testing folder
INPUT_INDEX=1
OUTPUT_INDEX=7
native_input_rate=48000

#openAI realtime API key
OPENAI_API_KEY=""

#Endpoint of the web socket, connect to here, model specified as gpt-realtime
url = "wss://api.openai.com/v1/realtime?model=gpt-realtime"

#For authorization in initial handshake to establish the websocket connection with the API
headers = ["Authorization: Bearer " + OPENAI_API_KEY]

#Define audio input formatting
#Opean AI realtime API works with 16bit PCM signals at a rate of 24kHz, mono
#1024 frames per buffer is a conventional middleground size, can be adjusted as needed
global input_stream, p
p=pyaudio.PyAudio()
input_stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=native_input_rate,
                input=True,
                frames_per_buffer=1024,
                input_device_index=INPUT_INDEX)

#Define audio output formatting
global output_stream
output_stream = p.open(format=pyaudio.paInt16, channels=1, rate=24000,
                    output=True, frames_per_buffer=1024, output_device_index=OUTPUT_INDEX)

#Play the dialup tone before the web socket connection is opened
def play_dial():
    file=wave.open("dial_sound_24.wav", mode="rb")
    chunk=2048
    data=file.readframes(chunk)

    while (len(data)):
        output_stream.write(data)
        data=file.readframes(chunk)

#Resamples audio input from native input rate to Open AI friendly 24kHz
def resample_to_24kHz(audio_native):
    samples = np.frombuffer(audio_native, dtype=np.int16).astype(np.float32)
    #Change native audio input rate to openAI friendly rate, function only accepts explicit int
    target_len = int(len(samples) * 24000 / native_input_rate)
    resampled = resample(samples, target_len)
    return resampled.astype(np.int16).tobytes()

#Runs when the web socket is opened successfully:
def on_open(ws):
    print("Connected to server.")
    #Sends a greeting message
    ws.send(json.dumps({
            "type": "conversation.item.create",
            "item": {
                    "type": "message",
                    "role": "user",
                    "content": [
                    {
                        "type": "input_text",
                        "text": f"Hi there!",
                    }
                ]
            }
        }))
    #Tells AI to begin conversing with user
    ws.send(json.dumps({
            "type": "response.create",
            "response":{
                "output_modalities": ["audio"],
                "instructions": "Start a conversation"
            }
        }))

    #Sets initial session parameters
    ws.send(json.dumps({
        "type":"session.update",
         "session":{
             "type": "realtime",
             "turn_detection": {
                "type": "semantic_vad",
            "create_response": true,
            "interrupt_response": false,
             }
         }
    }
    )
    )

#Runs when the server (open AI) sends a message
#Can be used to log AI responses, message reception confirmations, the AI's configuration
def on_message(ws, message):
    #json.loads takes the JSON formatted string and converts it into a python dictionary
    #This makes it easier to parse
    data = json.loads(message)

    #Displays the initial set up parameters of the AI
    if data["type"]=="session.created":
        #JSON.dumps converts back into its original JSON string format as it's a neater output
        print("Initial Conditions:", json.dumps(data, indent=2))
    
    #Detects when the AI begins speaking
    if data["type"]=="response.created":
        print("Response started!")
    
    #Outputs details of all messages, uncomment to troubleshoot any issues
    #print("Message Details:", json.dumps(data, indent=2))   
        
    #To process audio output (from the AI) phrase by phrase
    if data["type"] == "response.output_audio.delta":
        #Converts from base64 to raw PCM Audio bytes
        #Each sample sent to the output stream is 16-bit PCM
        audio_bytes = base64.b64decode(data["delta"])
        

        #Outputs audio to speakers   
        play_audio_chunk(audio_bytes)

    if data["type"]=="response.done":
        #p.set_input_device_volume(INPUT_INDEX, 100.0)
        print("Response complete!")

def play_audio_chunk(audio_bytes):
    global output_stream
    #Writes to output stream initialized through pyaudio
    output_stream.write(audio_bytes)

#Closes websocket and audio streams
def ws_close():
    ws.close()
    input_stream.close()
    output_stream.close()
    p.terminate()

ws = websocket.WebSocketApp(
    url, #End point of web socket
    header=headers, #Specifies header required for auth
    on_open=on_open, #Call on_open when opened
    on_message=on_message, #Call on_message when receiving a message from the server (openAI)
)

# Runs the websocket indefinitely
def run_ws():
    ws.run_forever()
    print("Websocket terminated")


def microphone_thread(ws):
    #While the web socket connection is established
    while ws.sock:
        #Read audio from mic 1024 frames at a time
        raw_audio_chunk = input_stream.read(1024, exception_on_overflow=False)
        #Resample the audio chunks to 24kHz
	audio_chunk=resample_to_24kHz(raw_audio_chunk)
        #Encodes PCM data into base 64 then formats that into JSON string
        audio_b64 = base64.b64encode(audio_chunk).decode()
        #Send the audio data over the websocket
        ws.send(json.dumps({
               "type": "input_audio_buffer.append",
               "audio": audio_b64
        }))

#This function is called from the main file so that the web socket can be passed into the microphone thread
def input_listener():
        time.sleep(1)
        mic_thread = threading.Thread(target=microphone_thread, args=(ws,), daemon=True)
        mic_thread.start()
        mic_thread.join()

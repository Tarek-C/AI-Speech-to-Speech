# AI-Speech-to-Speech
A simple program that lets you have real-time speech-to-speech conversation with a gpt model

Open AI's realtime API allows for direct speech-to-speech communication with the model without the need for any explicist text to speech or speech to text conversions

The model also automatically handles VAD (Voice Activity Detection) meaning there is no need to specify when input begins or ends you can use multithreading to run audio input synchronously

Things to keep in mind:
Requires the installation of pyaudio, websocket, and JSON (depending on the OS it may come pre-installed with JSON)

pyAudio uses the default audio device specified by the OS it is important that you configure your audio device accordingly

OpenAI's realtime API runs on a websocket connection which only accepts messages in the form of JSON formatted strings

The API works with audio in the form of 16 bit PCM samples at 24kHz on a mono channel, the audio data MUST be encoded in 64 bit when being transmitted

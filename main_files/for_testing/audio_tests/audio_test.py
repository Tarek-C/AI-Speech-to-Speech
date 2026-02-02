import pyaudio
import wave
import sys

p=pyaudio.PyAudio()
file=wave.open("output.wav", mode="rb")

output_stream=p.open(rate=24000, 
                     channels=1, 
                     format=pyaudio.paInt16,
                     output=True,
                     frames_per_buffer=1024,
output_device_index=1
	                     )

chunk=512
data=file.readframes(chunk)

while (len(data)):
    output_stream.write(data)
    print(f"Writing {len(data)} framess")
    print("\n")
    data=file.readframes(chunk)

output_stream.close()
p.terminate()

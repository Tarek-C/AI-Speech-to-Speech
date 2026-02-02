import pyaudio
import sys
import wave
import numpy as np
from scipy.signal import resample

p=pyaudio.PyAudio()
native_rate=48000


input_stream=p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=native_rate,
                    input=True,
                    frames_per_buffer=1024,
                    input_device_index=0)

resample_ratio=24000/native_rate
print("\n")
print("Recording!")

frames=[]
#Records for 5 seconds
for i in range(0, int(native_rate/1024 * 5)):
    data=input_stream.read(1024, exception_on_overflow=False)
    audio_data = np.frombuffer(data, dtype=np.int16)
    new_size = int(len(audio_data) * resample_ratio)
    resampled_data = resample(audio_data, new_size)
    resampled_data=resampled_data.astype(np.int16).tobytes()
    frames.append(resampled_data)

input_stream.close()
p.terminate()

file = wave.open('output.wav', mode='wb')

file.setnchannels(1)
file.setsampwidth(2)
file.setframerate(24000)
file.writeframes(b''.join(frames))
file.close()
print("done!")

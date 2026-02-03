# GPIO Speech — Setup & Deployment Guide

This project is a **Raspberry Pi** application that uses a physical phone (or GPIO-triggered device) to start a voice conversation with OpenAI’s Realtime API. When the phone is picked up, a dial tone plays and a WebSocket connection streams live audio to and from the API.

---

## Overview

- **Entry point:** `gpio_speech_main.py` — watches a GPIO pin for “phone off hook,” then starts dial tone and WebSocket.
- **Core logic:** `gpio_speech_body.py` — WebSocket client, audio I/O, resampling, and OpenAI Realtime session handling.
- **Trigger:** GPIO pin 4 (default) — high = phone picked up; low = phone put down (connection closes).
- **For Startup Operation:** Read startup_instructions.md

---

## Target Platform: Raspberry Pi

The program is intended to run on **Raspberry Pi** (e.g. Pi 4/5) with:

- Python 3 (3.8+ recommended)
- A microphone and speaker (or USB/ReSpeaker HAT)
- physical phone or button wired to GPIO 4

**ReSpeaker Pi HAT:** If you use a ReSpeaker, follow the official setup:  
[https://github.com/respeaker/seeed-voicecard](https://github.com/respeaker/seeed-voicecard)

---

## Audio Sampling & Format

### What the OpenAI Realtime API Expects

- **Format:** 16‑bit PCM, **mono**
- **Sample rate:** **24 kHz**
- **Transmission:** Audio must be **base64‑encoded** in JSON over the WebSocket.

### What This Project Does

- **Input (microphone):**  
  Opened at your device’s **native** sample rate (e.g. 48 kHz or 44.1 kHz). You set `native_input_rate` and `INPUT_INDEX` in `gpio_speech_body.py`.
- **Resampling:**  
  Audio from the mic is resampled from `native_input_rate` down to **24 kHz** before being base64‑encoded and sent. If your input device natively supports 24 kHz, you can set `native_input_rate=24000` and avoid extra resampling.
- **Output (speakers):**  
  Opened at **24 kHz** (API sends 24 kHz PCM). You set `OUTPUT_INDEX` in `gpio_speech_body.py`.
- **Buffer size:**  
  1024 frames per buffer for both input and output (can be tuned if needed).
- **Dial tone:**  
  `dial_sound_24.wav` must be a **24 kHz** mono WAV so it matches the output stream.

### Key Variables in `gpio_speech_body.py`

| Variable             | Meaning                                      | Example   |
|----------------------|----------------------------------------------|-----------|
| `INPUT_INDEX`        | PyAudio index for the microphone             | `1`       |
| `OUTPUT_INDEX`       | PyAudio index for the speaker                | `7`       |
| `native_input_rate`  | Mic’s native sample rate (Hz)                | `48000`   |

---

## How to Set the Project Up

### 1. Clone / Copy the Project

Copy the project (including `gpio_speech_main.py`, `gpio_speech_body.py`, `dial_sound_24.wav`, and the `for_testing` folder) to your Raspberry Pi.

### 2. Create a Virtual Environment (recommended)

On the Pi (Linux):

```bash
cd /path/to/main_files
python3 -m venv venv_audio
source venv_audio/bin/activate
```

Install dependencies (see **Required libraries** below):

```bash
pip install -r cursor_works/include.txt
```

Or install manually from `include.txt`. The venv can still use system packages (e.g. for GPIO) if needed.

### 3. Install System Audio / GPIO Dependencies (Raspberry Pi)

- **PyAudio** often needs system libraries:

  ```bash
  sudo apt update
  sudo apt install -y portaudio19-dev python3-dev
  ```

- **GPIO:** `gpiozero` uses the system’s GPIO; no extra install if you’re on Raspberry Pi OS.

### 4. Find Your Audio Device Indices and Sample Rate (Only do this step if you're not using Pulse for your output and a USB device for your input)

Run the helper script:

```bash
python3 for_testing/audio_tests/audio_index.py
```

From the output, note:

- The **index** of your microphone → use as `INPUT_INDEX`
- The **index** of your speaker/headphones → use as `OUTPUT_INDEX`
- The microphone’s **default sample rate** → use as `native_input_rate` (e.g. 48000 or 44100)

### 5. Configure `gpio_speech_body.py`

Edit the top of `gpio_speech_body.py`:

- Set `INPUT_INDEX`, `OUTPUT_INDEX`, and `native_input_rate` from the step above.
- Set `OPENAI_API_KEY` to your OpenAI API key (with Realtime API access).

**Security:** Do not commit the API key. Use environment variables or a local config file that’s in `.gitignore`.

### 6. Ensure `dial_sound_24.wav` Is Present

The file `dial_sound_24.wav` must be in the same directory as `gpio_speech_main.py`, and should be **24 kHz, mono, 16‑bit PCM** so it plays correctly on the 24 kHz output stream.

### 7. (Optional) Change the GPIO Pin

In `gpio_speech_main.py`, change `pin = 4` if your hardware uses a different GPIO pin for “phone off hook.”

---

## How to Run

1. Activate the virtual environment (if used):

   ```bash
   source venv_audio/bin/activate
   ```

2. From the project root (where `gpio_speech_main.py` lives):

   ```bash
   python3 gpio_speech_main.py
   ```

3. When the program prints “Pick up the phone!”, trigger the GPIO (e.g. pick up the phone). The dial tone will play, then the WebSocket will connect and the conversation will start. When the GPIO goes low again, the WebSocket and audio streams close.

---

## Testing

- **Audio I/O:** Use scripts in `for_testing/audio_tests/` (e.g. `audio_test.py`, `mic_check.py`) to verify microphone and speaker and sample rates.
- **Rotary / pulses:** Use `for_testing/rotary_signal_tests/read_pulse.py` to test rotary-dial or pulse detection if your hardware uses it.

---

## Summary Checklist

- [ ] Raspberry Pi with Python 3 and audio devices (and optional GPIO hardware)
- [ ] Dependencies installed (from `cursor_works/include.txt`) and system libs for PyAudio
- [ ] `audio_index.py` run to get `INPUT_INDEX`, `OUTPUT_INDEX`, `native_input_rate`
- [ ] `gpio_speech_body.py` updated with those values and your `OPENAI_API_KEY`
- [ ] `dial_sound_24.wav` in the project root (24 kHz mono)
- [ ] Run: `python3 gpio_speech_main.py` and trigger GPIO to start

For deployment on multiple Raspberry Pis, repeat the setup on each Pi and adjust only `INPUT_INDEX`, `OUTPUT_INDEX`, and `native_input_rate` (and optionally the GPIO pin) per device.

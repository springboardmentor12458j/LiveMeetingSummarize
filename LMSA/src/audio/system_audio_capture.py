# audio/system_audio_capture.py

import sounddevice as sd
import soundfile as sf
import queue
import time
import os


audio_queue = queue.Queue()


def callback(indata, frames, time_info, status):
    if status:
        print(status)
    audio_queue.put(indata.copy())


def get_wasapi_loopback_device():
    devices = sd.query_devices()
    hostapis = sd.query_hostapis()

    wasapi_index = next(
        i for i, api in enumerate(hostapis)
        if "Windows WASAPI" in api["name"]
    )

    for i, dev in enumerate(devices):
        if dev["hostapi"] == wasapi_index and dev["max_input_channels"] > 0:
            return i

    raise RuntimeError("No WASAPI loopback device found")


def record_audio(output_path: str, duration: int = 30):
    """
    Records system audio using WASAPI loopback
    """

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    device_index = get_wasapi_loopback_device()
    device_info = sd.query_devices(device_index)
    sample_rate = int(device_info["default_samplerate"])

    print("Using device:", device_info["name"])
    print("Sample rate:", sample_rate)
    print("Recording system audio...")

    with sf.SoundFile(
        output_path,
        mode="w",
        samplerate=sample_rate,
        channels=1,
        subtype="PCM_16"
    ) as file:

        with sd.InputStream(
            samplerate=sample_rate,
            device=device_index,
            channels=1,
            callback=callback,
            blocksize=1024,
            extra_settings=sd.WasapiSettings(exclusive=False)
        ):
            start = time.time()
            while time.time() - start < duration:
                file.write(audio_queue.get())

    print(f"Saved audio → {output_path}")

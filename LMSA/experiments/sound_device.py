import sounddevice as sd

output_index = sd.default.device[1]
device_info = sd.query_devices(output_index)

print("Current output device:")
print("Index:", output_index)
print("Name:", device_info["name"])
print("Host API:", sd.query_hostapis()[device_info["hostapi"]]["name"])
print("Sample rate:", device_info["default_samplerate"])
print("Max input channels:", device_info["max_input_channels"])

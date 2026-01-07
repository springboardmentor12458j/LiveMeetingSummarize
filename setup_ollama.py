import os
import urllib.request
import subprocess
import time

OLLAMA_URL = "https://ollama.com/download/OllamaSetup.exe"
INSTALLER_NAME = "OllamaSetup.exe"

def download_and_install_ollama():
    print(f"Downloading Ollama from {OLLAMA_URL}...")
    try:
        urllib.request.urlretrieve(OLLAMA_URL, INSTALLER_NAME)
        print("Download complete.")
        
        print(f"Running {INSTALLER_NAME}...")
        # Run the installer. This will likely trigger a UAC prompt on the user's screen.
        subprocess.Popen(INSTALLER_NAME, shell=True)
        print("Installer launched. Please complete the installation steps on your screen.")
        
    except Exception as e:
        print(f"Error downloading or running installer: {e}")

if __name__ == "__main__":
    download_and_install_ollama()

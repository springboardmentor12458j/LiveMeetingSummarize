import os
import sys
import zipfile
import shutil
import urllib.request

FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
FFMPEG_EXE_NAME = "ffmpeg.exe"
LOCAL_FFMPEG_DIR = os.path.join(os.getcwd(), "bin")
LOCAL_FFMPEG_EXE = os.path.join(LOCAL_FFMPEG_DIR, FFMPEG_EXE_NAME)

def check_and_install():
    """
    Checks if ffmpeg.exe exists in the local 'bin' directory.
    If not, downloads and extracts it.
    Returns the directory containing ffmpeg.exe.
    """
    if os.path.exists(LOCAL_FFMPEG_EXE):
        print(f"FFmpeg found at: {LOCAL_FFMPEG_EXE}")
        return LOCAL_FFMPEG_DIR
    
    print(f"FFmpeg not found. Downloading from {FFMPEG_URL}...")
    print("This may take a few minutes depending on your internet connection.")
    
    if not os.path.exists(LOCAL_FFMPEG_DIR):
        os.makedirs(LOCAL_FFMPEG_DIR)
        
    zip_path = os.path.join(LOCAL_FFMPEG_DIR, "ffmpeg.zip")
    
    try:
        # Download
        urllib.request.urlretrieve(FFMPEG_URL, zip_path)
        print("Download complete. Extracting...")
        
        # Extract
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Find the ffmpeg.exe file in the zip
            ffmpeg_zip_path = None
            for name in zip_ref.namelist():
                if name.endswith("ffmpeg.exe"):
                    ffmpeg_zip_path = name
                    break
            
            if ffmpeg_zip_path:
                source = zip_ref.open(ffmpeg_zip_path)
                target = open(LOCAL_FFMPEG_EXE, "wb")
                with source, target:
                    shutil.copyfileobj(source, target)
                print("Extraction complete.")
            else:
                print("Error: ffmpeg.exe not found in the downloaded zip.")
                
    except Exception as e:
        print(f"Error installing FFmpeg: {e}")
        # Clean up partial files
        if os.path.exists(zip_path):
            os.remove(zip_path)
        return None
        
    finally:
        # Cleanup zip
        if os.path.exists(zip_path):
            os.remove(zip_path)

    return LOCAL_FFMPEG_DIR

if __name__ == "__main__":
    check_and_install()

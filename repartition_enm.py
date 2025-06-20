import os
import sys
import subprocess
import webbrowser
import threading
import time

def resource_path(relative_path):
    """Get absolute path to resource (handles PyInstaller bundle or dev)."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

# def open_browser():
#     print("Calling open_browser)")
#     """Delay opening the browser to wait for Streamlit server to start"""
#     time.sleep(2)
#     webbrowser.open_new("http://localhost:8501")

if __name__ == "__main__":
    app_path = resource_path("app/app.py")

    # print("Opening browser")
    # threading.Thread(target=open_browser).start()

    print("Launching streamlit app")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", app_path,
        # "--server
        # "--browser.gatherUsageStats=false",
        # "--browser.serverAddress=localhost",
        # "--server.runOnSave=false",
        # "--browser.serverPort=8501"
    ])
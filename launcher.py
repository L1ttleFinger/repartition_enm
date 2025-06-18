# launcher.py
import subprocess
import sys
import os

streamlit_command = [
    "streamlit",
    "run",
    os.path.join("app", "app.py"),
]

# Add any extra args passed to the exe
if len(sys.argv) > 1:
    streamlit_command.extend(sys.argv[1:])

subprocess.run(streamlit_command)

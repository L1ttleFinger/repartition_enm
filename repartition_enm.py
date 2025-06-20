import os
import sys
import streamlit.web.cli as stcli

def resource_path(relative_path):
    """Get absolute path to resource (handles PyInstaller bundle or dev)."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    app_path = resource_path("app/app.py")
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())
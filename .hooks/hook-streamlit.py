from PyInstaller.utils.hooks import collect_data_files, copy_metadata

datas = [("enm_env/lib/python3.9/site-packages/streamlit/runtime", "./streamlit/runtime"), ("enm_env/lib/python3.9/site-packages/streamlit/static", "./streamlit/static")]
datas += collect_data_files("streamlit")
datas += copy_metadata("streamlit")
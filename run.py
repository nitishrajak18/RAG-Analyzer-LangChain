"""
This is the file you run.

In VS Code: open this file and click Run ▶ (or press F5), or in the
terminal run:  python run.py

It launches the Streamlit app (streamlit_app.py) and opens it in your
default browser automatically — you never need to type
`streamlit run streamlit_app.py` yourself or run two separate processes.
"""
import os
import sys
from streamlit.web import cli as stcli

if __name__ == "__main__":
    sys.argv = [
          "streamlit",
        "run",
        "streamlit_app.py",
        "--server.port",
        str(os.environ.get("PORT", 8501)),
        "--server.address",
        "0.0.0.0",
        "--server.headless",
        "true",   # ensures it opens your browser locally
    ]
    sys.exit(stcli.main())

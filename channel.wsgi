import os
import sys

# Change the current working directory to /home/u024/public_html.
# This is useful when your application relies on relative paths (e.g., for messages.json).
os.chdir("/home/u024/public_html")

# Insert the ChatNetwork directory at the start of the Python path so that channel.py can be found.
sys.path.insert(0, "/home/u024/public_html/ChatNetwork")

# Import the Flask application instance from channel.py.
from channel import app as application
"""
Root App Launcher.
Redirects execution to the full-stack LakePulse AI app in capestone_proj/app.py.
"""

import os
import sys

# Change working directory to capestone_proj
base_dir = os.path.dirname(os.path.abspath(__file__))
target_dir = os.path.join(base_dir, "capestone_proj")

if target_dir not in sys.path:
    sys.path.insert(0, target_dir)

os.chdir(target_dir)

# Execute capestone_proj/app.py
target_app = os.path.join(target_dir, "app.py")
with open(target_app, "r", encoding="utf-8") as f:
    code = compile(f.read(), target_app, "exec")
    exec(code)

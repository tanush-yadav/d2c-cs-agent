#!/usr/bin/env python3

import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, restart_func):
        self.restart_func = restart_func
        self.last_modified = time.time()

    def on_modified(self, event):
        # Filter out non-Python files and certain directories
        if not event.is_directory:
            file_path = event.src_path
            if file_path.endswith('.py') and '/.' not in file_path and '/__pycache__' not in file_path:
                # Avoid duplicate events (some filesystems may trigger multiple events)
                current_time = time.time()
                if current_time - self.last_modified > 1:
                    print(f"\n🔄 Change detected in {file_path}, restarting ADK server...")
                    self.last_modified = current_time
                    self.restart_func()

def restart_adk():
    """Kill running ADK web server and start a new one"""
    try:
        # Kill any running ADK web servers
        subprocess.run(["pkill", "-f", "adk web"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ Stopped previous ADK web server")
    except Exception as e:
        print(f"⚠️ Could not kill ADK web server: {e}")

    # Start a new ADK web server
    try:
        # First run the normal ADK run command to ensure the agent is initialized properly
        cmd = "adk web"
        subprocess.Popen(cmd, shell=True)
        print("✅ Started new ADK web server")
    except Exception as e:
        print(f"❌ Failed to start ADK web server: {e}")

if __name__ == "__main__":
    # Ensure we have the watchdog package
    try:
        import watchdog
    except ImportError:
        print("Installing watchdog package...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "watchdog"])
        print("Watchdog installed, restarting script...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

    # Start ADK web server initially
    print("Starting ADK web server...")
    restart_adk()

    # Set up file watcher
    event_handler = ChangeHandler(restart_adk)
    observer = Observer()

    # Watch the customer_service directory
    path = os.path.join(os.getcwd(), "customer_service")
    observer.schedule(event_handler, path, recursive=True)

    print(f"\n👀 Watching for changes in {path}...")
    print("Press Ctrl+C to stop")

    # Start the observer
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        # Kill the ADK web server when stopping
        subprocess.run(["pkill", "-f", "adk web"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("\n🛑 Stopped watching and terminated ADK web server")

    observer.join()
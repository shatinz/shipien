import os
import sys
import threading
import asyncio
import logging
import subprocess
from PIL import Image, ImageDraw
import pystray

# Import the main functions from product_manager
import product_manager

# Set up logging to write to both console and a log file
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "product_manager.log")

# Setup logger
logger = logging.getLogger("ShipienManager")
logger.setLevel(logging.INFO)

# File handler
fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
fh.setLevel(logging.INFO)

# Console handler
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

# Redirect product_manager prints/stdout to logger
def log_print(*args, **kwargs):
    msg = " ".join(map(str, args))
    logger.info(msg)

product_manager.print = log_print

# Global reference to the asyncio event loop and task
loop = None
client_thread = None
icon = None

def create_icon_image():
    # Generate a beautiful gear icon for the tray
    image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    dc = ImageDraw.Draw(image)
    
    # Draw dark blue circle background
    dc.ellipse([4, 4, 60, 60], fill=(26, 82, 118, 255), outline=(41, 128, 185, 255), width=3)
    # Draw gear core
    dc.ellipse([20, 20, 44, 44], fill=(255, 255, 255, 255))
    dc.ellipse([26, 26, 38, 38], fill=(26, 82, 118, 255))
    
    # Draw gear teeth
    for angle in range(0, 360, 45):
        dc.pieslice([14, 14, 50, 50], start=angle-15, end=angle+15, fill=(255, 255, 255, 255))
        
    dc.ellipse([20, 20, 44, 44], fill=(26, 82, 118, 255))
    dc.ellipse([25, 25, 39, 39], fill=(255, 255, 255, 255))
    return image

def on_open_terminal(icon, item):
    logger.info("Opening log viewer terminal...")
    # Launch a new PowerShell window that tails the log file
    cmd = f'Start-Process powershell -ArgumentList "-NoExit", "-Command", "Clear-Host; Write-Host \'=== Shipien Product Manager Live Log Terminal ===\' -ForegroundColor Cyan; Get-Content -Path \'{LOG_FILE}\' -Wait -Tail 50"'
    subprocess.Popen(["powershell", "-Command", cmd], shell=True)

def on_view_log_file(icon, item):
    logger.info("Opening log file in Notepad...")
    os.system(f'start notepad.exe "{LOG_FILE}"')

def on_run_pm(icon, item):
    logger.info("Manual trigger: Running PM loop now...")
    if loop:
        # Schedule the coroutine in the running event loop
        asyncio.run_coroutine_threadsafe(
            product_manager.run_daily_pm_loop(force=True), loop
        )

def on_sync_data(icon, item):
    logger.info("Manual trigger: Syncing databases from server...")
    if loop:
        asyncio.run_coroutine_threadsafe(
            sync_data_async(), loop
        )

async def sync_data_async():
    product_manager.sync_data()

def on_exit(icon, item):
    logger.info("Stopping Shipien Manager...")
    icon.stop()
    
    # Stop the asyncio loop
    if loop:
        loop.call_soon_threadsafe(loop.stop)

def run_async_loop():
    global loop
    logger.info("Initializing background asyncio loop...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(product_manager.main())
    except Exception as e:
        logger.error(f"Error in asyncio loop: {e}")
    finally:
        loop.close()

def main():
    global client_thread, icon
    logger.info("Starting Shipien Tray Icon application...")
    
    # 1. Start the Telegram client and PM loop in a background thread
    client_thread = threading.Thread(target=run_async_loop, daemon=True)
    client_thread.start()
    
    # 2. Build the System Tray Icon
    icon_image = create_icon_image()
    menu = pystray.Menu(
        pystray.MenuItem("Open Terminal (Live Logs)", on_open_terminal, default=True),
        pystray.MenuItem("View Log File (Notepad)", on_view_log_file),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Run PM Loop Now", on_run_pm),
        pystray.MenuItem("Sync Database", on_sync_data),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit", on_exit)
    )
    
    icon = pystray.Icon("ShipienManager", icon_image, "Shipien Agent Manager", menu)
    
    # 3. Run the tray icon (blocks main thread)
    icon.run()

if __name__ == "__main__":
    main()

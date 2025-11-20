#region Imports
from flask import Flask, render_template, jsonify, request, send_file
import os
from discord_webhook import DiscordWebhook
from datetime import datetime
import socket
import time
import logging
from dotenv import load_dotenv
import sys
import tkinter as tk
from tkinter import messagebox
import requests
import psutil
import GPUtil
from io import BytesIO
from PIL import Image
import mss
#endregion

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%d/%m/%y %H:%M',
    handlers=[
        logging.FileHandler('restshutdown.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

WEBHOOK_URL = os.getenv('WEBHOOK_URL')
PORT = os.getenv('port')
simpleLogLoc = os.getenv('simpleLog')
current_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
logger.info("Flask app started")

def newVerQuery():
    req = f'https://api.github.com/gists/f8291a771e19ae6fca1107a4657fc70e'
    res = requests.get(req)
    if res.status_code == 200:
        gdata = res.json()
        for filename, file_info in gdata["files"].items():
            latestVersion = float(file_info["content"])
        
        if os.path.exists(os.path.join(current_dir, 'VERSION')):
            with open(os.path.join(current_dir, 'VERSION'), 'r') as f:
                currentVersion = float(f.read())
                f.close()
            
            if currentVersion < latestVersion:
                logger.info("[UPDATER] You aren't on the latest version! Showing popup.")
                return True
            else:
                logger.info('[UPDATER] All up to date')
                return False
        else:
            logger.error("[UPDATER] Failed to fetch version from VERSION file. Does it exist?")
    else:
        logger.error(f'[UPDATER] Failed to fetch version data from gist: {res.status_code}')

def askContinueWithOldVer():
    root = tk.Tk()
    root.withdraw()

    result = messagebox.askyesno(
        "LANControl Updater",
        "Wait! A new version of LANControl is available.\n\n"
        "Run updater.py to automatically update to the newest version.\n\n"
        "Do you want to continue with the outdated version?"
    )

    root.destroy()
    return result

def wait_for_internet(host="8.8.8.8", port=53, timeout=3):
    logger.info("Checking internet connection")
    while True:
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            logger.info("Internet connected")
            print("Connected to the internet.")
            return True
        except Exception:
            print("No connection... retrying in 2 seconds")
            time.sleep(2)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        logger.info(f"Local IP: {local_ip}")
        return local_ip
    except Exception:
        logger.info("Failed to get local IP")
        return "unknown"
    finally:
        s.close()

def simpleLog(text):
    with open(rf'{simpleLogLoc}', 'a') as f:
        f.write(text)

#region Error Handlers
@app.route('/')
def renderHome():
    logger.info(f"Home page accessed from {request.remote_addr}")
    return render_template('index.html')

@app.errorhandler(404)
def internal_server_error(e):
    logger.info(f"404 from {request.remote_addr}")
    return

@app.errorhandler(Exception)
def handle_any_error(e):
    logger.info(f"Error from {request.remote_addr}: {str(e)[:50]}...")
    return jsonify({
        "success": False,
        "error": "Server error occurred. Please try again later."
    }), 500

# The following 3 routes are here to avoid console flooding if the address is opened on a webpage.
# The 3 files browsers (apple for the last 2) try to fetch dont exist so flood the console with 404 when it cant find them.
@app.route('/favicon.ico')
def fakefavicon():
    return

@app.route('/apple-touch-icon.png')
def fakeappletouch():
    return

@app.route('/apple-touch-icon-precompressed.png')
def fakeappletouchprec():
    return
#endregion

@app.route('/api/shutdown')
def shutdown():
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    logger.info(f"SHUTDOWN requested from {client_ip}")
    
    try:
        webhook = DiscordWebhook(url='https://discord.com/api/webhooks/1327708958584213574/8JbS067SNiEq9aT_m7rzWgHOc2MOyBISyDzK4R6qxwza851CPWiuSW9x5Z2rfjcfzUDm', 
                                content=f"System shutdown called from {client_ip}")
        
        logger.info("Executing shutdown")
        os.system('shutdown /s /t 20')
        
        webhook.execute()
        logger.info("Discord notification sent")
        
        simpleLog(f'{datetime.now()} | /api/shutdown called from {client_ip}. Headers: {user_agent}')

        logger.info("Shutdown initiated")
        return jsonify({
            "success": True,
            "data": "Shutdown scheduled for 20 seconds."
        })
    except Exception as e:
        logger.info(f"Shutdown failed: {str(e)[:30]}...")
        return jsonify({
            "success": False,
            "data": f"Failed to run shutdown: {e}"
        })
    
@app.route('/api/abortshutdown')
def abortShutdown():
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    try:
        webhook = DiscordWebhook(url=WEBHOOK_URL,
                                content=f"Shutdown aborted. Called from {client_ip}")
        
        logger.info('Aborting shutdown')
        os.system('shutdown /a')
        webhook.execute()
        
        logger.info('Discord abort notifaction sent.')
        simpleLog(f'{datetime.now()} | /api/abortshutdown called from {client_ip}. Headers: {user_agent}')
        logger.info('Shutdown aborted.')
        
        return jsonify({
            "success": True,
            "data": "Shutdown aborted."
        })
    except Exception as e:
        logger.info(f"Failed to abort shutdown: {e}")
        return jsonify({
            "success": False,
            "data": f"Failed to abort shutdown: {e}"
        })

@app.route('/api/stats')
def stats():
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    logger.info(f"System stats requested from {client_ip}")
    logger.info("Collecting system statistics, this may take a while..")
    simpleLog(f'{datetime.now()} | /api/stats called from {client_ip}. Headers: {user_agent}')

    cpu_ok = gpu_ok = drives_ok = ram_ok = uptime_ok = False

    # ---------- CPU ----------
    CPUUsage = 'unknown'
    try:
        CPUUsage = psutil.cpu_percent(interval=1)
        cpu_ok = True
        logger.info(f"CPU usage collected: {CPUUsage}%")
    except Exception as e:
        logger.error(f"Error collecting CPU usage: {e}")

    # ---------- GPU ----------
    gpu_list = 'unknown'
    try:
        gpus = GPUtil.getGPUs()
        tmp_gpu_list = []
        for gpu in gpus:
            tmp_gpu_list.append({
                "id": gpu.id,
                "name": gpu.name,
                "load_percent": gpu.load * 100,
                "memory_used_mb": gpu.memoryUsed,
                "memory_total_mb": gpu.memoryTotal,
                "temperature_c": gpu.temperature
            })
        gpu_list = tmp_gpu_list
        gpu_ok = True
        logger.info(f"GPU usage collected for {len(gpu_list)} GPU(s)")
    except Exception as e:
        logger.error(f"Error collecting GPU usage: {e}")

    # ---------- Storage / Drives ----------
    drives = 'unknown'
    try:
        tmp_drives = []
        for part in psutil.disk_partitions(all=False):
            if "cdrom" in part.opts or part.fstype == "":
                continue
            try:
                usage = psutil.disk_usage(part.mountpoint)
            except PermissionError:
                # Skip partitions we can't read
                continue

            tmp_drives.append({
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "percent_used": usage.percent,
            })
        drives = tmp_drives
        drives_ok = True
        logger.info(f"Storage usage collected for {len(drives)} drive(s)")
    except Exception as e:
        logger.error(f"Error collecting storage usage: {e}")

    # ---------- RAM ----------
    RAMUsage = 'unknown'
    try:
        vmem = psutil.virtual_memory()
        RAMUsage = {
            "total_gb": round(vmem.total / (1024**3), 2),
            "used_gb": round((vmem.total - vmem.available) / (1024**3), 2),
            "available_gb": round(vmem.available / (1024**3), 2),
            "percent_used": vmem.percent,
        }
        ram_ok = True
        logger.info("RAM usage collected")
    except Exception as e:
        logger.error(f"Error collecting RAM usage: {e}")

    # ---------- Uptime ----------
    uptime = 'unknown'
    try:
        boot_ts = psutil.boot_time()
        boot_time = datetime.fromtimestamp(boot_ts)
        now = datetime.now()
        delta = now - boot_time

        days = delta.days
        seconds = delta.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        uptime = {
            "boot_time": boot_time.strftime("%d-%m-%Y %H:%M:%S"),
            "uptime_days": days,
            "uptime_hours": hours,
            "uptime_minutes": minutes,
            "uptime_total_seconds": int(delta.total_seconds())
        }
        uptime_ok = True
        logger.info("System uptime collected")
    except Exception as e:
        logger.error(f"Error collecting system uptime: {e}")

    success = any([cpu_ok, gpu_ok, drives_ok, ram_ok, uptime_ok])

    data = {
        "cpu_usage_percent": CPUUsage,
        "gpu": gpu_list,
        "storage": drives,
        "ram": RAMUsage,
        "uptime": uptime,
    }

    return jsonify({
        "success": success,
        "data": data
    })

@app.route("/api/screenshot", methods=["GET"])
def screenshot():
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            screenshot = sct.grab(monitor)

            img = Image.frombytes(
                "RGB",
                screenshot.size,
                screenshot.bgra,
                "raw",
                "BGRX"
            )

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype="image/png",
            as_attachment=False,
            download_name="screenshot.png"
        )

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })



logger.info("Initializing application")
wait_for_internet()


if __name__ == '__main__':
    try:
        if newVerQuery():
            if askContinueWithOldVer():
                logger.info('Running on outdated version.')
                pass
            else:
                logger.info('Exiting to update.')
                sys.exit(0)

        localip = get_local_ip()
        webhook = DiscordWebhook(url=WEBHOOK_URL, 
                                    content=f"System online. Local IP: {localip}")

        try:
            webhook.execute()
            logger.info("Discord startup notification sent")
        except Exception:
            logger.info("Failed to send Discord notification")
        
        logger.info(f"Starting server on 0.0.0.0:{PORT}")
        app.run(debug=False, host='0.0.0.0', port=PORT)
    except Exception as e:
        logger.error(f"[ERROR] Failed to start Flask: {e}")

    finally:
        logger.info("Flask server stopped.")
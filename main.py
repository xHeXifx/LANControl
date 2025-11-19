from flask import Flask, render_template, jsonify, request
import os
from discord_webhook import DiscordWebhook
from datetime import datetime
import socket
import time
import logging

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

app = Flask(__name__)
logger.info("Flask app started")

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

#region Error Handlers
@app.route('/')
def renderHome():
    logger.info(f"Home page accessed from {request.remote_addr}")
    return render_template('index.html')

@app.errorhandler(404)
def internal_server_error(e):
    logger.info(f"404 from {request.remote_addr}")
    return render_template('error.html'), 404

@app.errorhandler(Exception)
def handle_any_error(e):
    logger.info(f"Error from {request.remote_addr}: {str(e)[:50]}...")
    return jsonify({
        "success": False,
        "error": "Server error occurred. Please try again later."
    }), 500
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
        
        with open(r'C:\Users\jdglo\Document\Documents\shutdownlog.txt', 'w') as f:
            f.write(f'{datetime.now()} | /api/shutdown called from {client_ip}. Headers: {user_agent}')

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
        webhook = DiscordWebhook(url='https://discord.com/api/webhooks/1327708958584213574/8JbS067SNiEq9aT_m7rzWgHOc2MOyBISyDzK4R6qxwza851CPWiuSW9x5Z2rfjcfzUDm', 
                                content=f"Shutdown aborted. Called from {client_ip}")
        
        logger.info('Aborting shutdown')
        os.system('shutdown /a')
        webhook.execute()
        logger.info('Discord abort notifaction sent.')
        with open(r'C:\Users\jdglo\Document\Documents\shutdownlog.txt', 'w') as f:
            f.write(f'{datetime.now()} | /api/abortshutdown called from {client_ip}. Headers: {user_agent}')
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

logger.info("Initializing application")
wait_for_internet()

localip = get_local_ip()
webhook = DiscordWebhook(url='https://discord.com/api/webhooks/1327708958584213574/8JbS067SNiEq9aT_m7rzWgHOc2MOyBISyDzK4R6qxwza851CPWiuSW9x5Z2rfjcfzUDm', 
                          content=f"System online. Local IP: {localip}")

try:
    webhook.execute()
    logger.info("Discord startup notification sent")
except Exception:
    logger.info("Failed to send Discord notification")

logger.info("Starting server on 0.0.0.0:6060")
app.run(debug=False, host='0.0.0.0', port='6060')
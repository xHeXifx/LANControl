# LANControl

LANControl is a simple python flask script that creates API routes allowing you to interact with your system remotely.

## How to setup

1. Run ```pip install -r requirements.txt```
2. Fill in the values in .env
3. Run main.py, if you want the window to be hidden change extension to .pyw

For ease of use i made an apple shortcut to call the routes, you'll have to manually fill in the IP address provided by the webhook message on startup. You can import it using the [LANControl.shortcut](LANControl.shortcut) file.

## How to use

Pretty simple, call a GET request on one of the routes below and it'll return the data. Your request **MUST** contain the header LANControl with value True otherwise you'll get a success false and invalid header error. For futher information of parsing data read [How to parse returned data](#how-to-parse-returned-data)


## Avalible Routes

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/shutdown` | GET | Schedule system shutdown in 20 seconds |
| `/api/abortshutdown` | GET | Cancel a scheduled shutdown |
| `/api/stats` | GET | Get (most) system statistics |
| `/api/screenshot` | GET | Get a full screenshot from your PC |

## Notifactions and logging

Each api route calls to discords webhooks when used, your webhook url gets set in the .env and states what IP called the route.

2 seperate logs are stored. 

**restshutdown.log** in the files location stores detailed logs on pretty much everything from the server spinning up to routes being called. 

The simpleLog in .env provides simple logs saying when routes are called along with the IP and headers of the client that requested.


## How to parse returned data

Data is returned extreamly simply using flasks jsonify, each request will return 2 keys: success and data.

Structure looks as follows:

```json
{
  "success": true/false,
  "data": "Response message or error details"
}
```

- `success`: Boolean indicating if the operation completed successfully
- `data`: String containing status message or error information

### /api/stats (yes this deserves its own section)
Parsing data from this is quite difficult to say the least.. below is the structure:

```json
{
  "success": "true/false (Boolean showing whether the request succeeded)",

  "data": {
    "cpu_usage_percent": "{percentage of current CPU usage}",

    "gpu": [
      {
        "id": "{GPU device ID}",
        "name": "{GPU model name, e.g. 'NVIDIA GTX 1650'}",
        "load_percent": "{current GPU load percentage}",
        "memory_used_mb": "{VRAM currently used in MB}",
        "memory_total_mb": "{total VRAM available in MB}",
        "temperature_c": "{GPU temperature in Celsius}"
      }
      /* ...repeat for multiple GPUs if present... */
    ],

    "ram": {
      "total_gb": "{total system memory in gigabytes}",
      "used_gb": "{amount of RAM currently used in gigabytes}",
      "available_gb": "{RAM available for use}",
      "percent_used": "{percentage of RAM currently used}"
    },

    "storage": [
      {
        "device": "{device path, e.g. /dev/disk3s1s1}",
        "fstype": "{filesystem type, e.g. apfs}",
        "mountpoint": "{mount location, e.g. /}",
        "total_gb": "{total disk capacity}",
        "used_gb": "{used space on the disk}",
        "free_gb": "{remaining free space}",
        "percent_used": "{percentage used}"
      }
      /* ...repeat for each volume... */
    ],

    "uptime": {
      "boot_time": "{timestamp when the system booted}",
      "uptime_days": "{total days system has been running}",
      "uptime_hours": "{hours past the full days}",
      "uptime_minutes": "{minutes past the full hours}",
      "uptime_total_seconds": "{total uptime in seconds}"
    }
  }
}

```

## Troubleshooting

### Common Issues

- **Port 6060 in use**: Change the port in `.env` or kill the process using the port

## Credits
**[HeXif](https://hexif.vercel.app)**

#### Python Modules
[discord-webhook](https://pypi.org/project/discord-webhook/)   
[Flask](https://pypi.org/project/Flask/)  
[python-dotenv](https://pypi.org/project/python-dotenv/)  
[art](https://pypi.org/project/art/)  
[GitPython](https://pypi.org/project/GitPython/)  
[requests](https://pypi.org/project/requests/)  
[psutil](https://pypi.org/project/psutil/)  
[GPUtil](https://pypi.org/project/GPUtil/)  
[pillow](https://pypi.org/project/pillow)  
[mss](https://pypi.org/project/mss)
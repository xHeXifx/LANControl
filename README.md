# LANControl

LANControl is a simple python flask script that creates API routes allowing you to interact with your system remotely.

## How to setup

1. Run ```pip install -r requirements.txt```
2. Fill in the values in .env
3. Run main.py, if you want the window to be hidden change extension to .pyw

For ease of use i made an apple shortcut to call the routes, you'll have to manually fill in the IP address provided by the webhook message on startup. You can find that [here](https://www.icloud.com/shortcuts/b7b919024c7e408ba8b6fb2733301220)


## Avalible Routes

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/shutdown` | GET | Schedule system shutdown in 20 seconds |
| `/api/abortshutdown` | GET | Cancel a scheduled shutdown |

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

## Troubleshooting

### Common Issues

- **Port 6060 in use**: Change the port in `.env` or kill the process using the port

## Credits
**[HeXif](https://hexif.vercel.app)**

#### Python Modules
[discord-webhook](https://pypi.org/project/discord-webhook/)   
[Flask](https://pypi.org/project/Flask/)  
[python-dotenv](https://pypi.org/project/python-dotenv/) 
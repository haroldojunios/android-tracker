# Simple Android tracker

A simple Android tracker that use Python and Termux (with Termux-API) to get the device location.

## Credentials

The credentials must be placed in the file `credentials.py` at the project root folder. It's in the format:

```[python]
BROKER = 'BROKER_ADDRESS'
PORT = 1883
BROKER_USER = 'USER' # if empty string the connection is made without username and password
BROKER_PASS = 'PASS' # if empty string the connection is made without password

PUB_TOPIC = 'TOPIC'
```

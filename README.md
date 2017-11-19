A Domoticz plugin for IKEA Trådfri (Tradfri) gateway - AIOCOAP - version

# Plugin

Since domoticz plugins doesn't support COAP and also doesn't allow threads or async calls, the IKEA-tradfri plugin contains two parts, the domoticz plugin and a python3 IKEA-tradfri adaptor written using the asyncio framework. The adaptor needs to be running at all times, and is intented to be run as a service using systemd. 

## A note about branches
The aiocoap version of the plugin only supports the latest beta of domoticz. 

## Requirements:
1. Domoticz compiled with support for Python-Plugins / lastest beta
2. Python library pytradfri by ggravlingen (https://github.com/ggravlingen/pytradfri). Required version: 4.0.2 or greater.
3. IKEA-Tradfri-plugin (https://github.com/moroen/IKEA-Tradfri-plugin)


## Local Installation
### 1. Clone IKEA-tradfri plugin into domoticz plugins-directory
```
~/$ cd /opt/domoticz/plugins/
/opt/domoticz/plugins$ git clone https://github.com/moroen/IKEA-Tradfri-plugin.git IKEA-Tradfri
```

### 2. Install required dependencies
```
/opt/domoticz/plugins$ cd IKEA-Tradfri
/opt/domoticz/plugins/IKEA-Tradfri$ pip3 install -r requirements.txt
```
Note: You should run pip3 as the user intended to run the adapter. Depending on your setup, pip3 might need to be run as root.

### 3. Create identity and pre-shared-key 
 - Yet to be implemented

### 4. Enable COAP-adaptor

#### From prompt (for testing)
```
/opt/domoticz/plugins/IKEA-Tradfri$ python3 tradfri_coap.py
```

#### Using systemd
Edit the ikea-tradfri.service-file, and specify the right path to the IKEA-tradfri directory and change user. Then copy the service-file to systemd-service directory, reload systemd-daemon and start the IKEA-tradfri service:
```
/opt/domoticz/plugins/IKEA-Tradfri$ sudo cp ikea-tradfri.service /lib/systemd/system/
/opt/domoticz/plugins/IKEA-Tradfri$ sudo systemctl daemon-reload
/opt/domoticz/plugins/IKEA-Tradfri$ sudo systemctl start ikea-tradfri.service
```

#### Using systemd to start the COAP-adaptor on startup
```
$ sudo systemctl enable ikea-tradfri.service
```


### 5. Restart domoticz and enable IKEA-Tradfri from the hardware page
To get domoticz to recognize changed states (using IKEA-remote, app or any other way of switching lights), observe changes must be enabled in the plugin-settings page.

## Docker Installation

To run the plugin in a Docker (for example to on a Synology NAS), package the adapter using the provided Docker build file:
```
docker build -t ikea-tradfri-plugin:latest .
```

Copy the docker image to the system running Domoticz and start the Docker instance:
```
docker run -t -p 127.0.0.1:1234:1234 ikea-tradfri-plugin:1234
```

Now the IKEA Tradfri to Domoticz adaptor is available on the localhost.

Clone IKEA-tradfri plugin into Domoticz plugins-directory
```
~/$ cd /opt/domoticz/plugins/
/opt/domoticz/plugins$ git clone https://github.com/moroen/IKEA-Tradfri-plugin.git IKEA-Tradfri
```

Restart Domoticz and the plugin should show up. When the plugin is loaded, the adaptor running in the Docker is automatically used.

## Usage
Lights and devices have to be added to the gateway as per IKEA's instructions, using the official IKEA-tradfri app. 

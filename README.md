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
### 1. Install aiocoap version of pytradfri-library, including requirements:
```shell
  $ git clone https://github.com/ggravlingen/pytradfri.git
  $ cd pytradfri
  $ pip3 install -r requirements.txt
  $ python3 setup.py install
```

### 2. Clone IKEA-tradfri plugin into domoticz plugins-directory
```
~/$ cd /opt/domoticz/plugins/
/opt/domoticz/plugins$ git clone https://github.com/moroen/IKEA-Tradfri-plugin.git IKEA-Tradfri
```

### 3. Create identity and pre-shared-key 
 - Yet to be implemented

### 4. Enable COAP-adaptor

#### From prompt (for testing)
```
/opt/domoticz/plugins/IKEA-Tradfri$ python3 tradfri_coap.py
```

#### Using systemd
 - Yet to be implemented


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

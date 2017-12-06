#!/usr/bin/env python3

import asyncio
import json, configparser, os

from pytradfri import Gateway
from pytradfri.api.aiocoap_api import APIFactory
from pytradfri.error import PytradfriError, RequestTimeout

version = 0.1

try:
    # pylint: disable=ungrouped-imports
    from asyncio import ensure_future
except ImportError:
    # Python 3.4.3 and earlier has this as async
    # pylint: disable=unused-import
    from asyncio import async
    ensure_future = async

def stringToBool(boolString):
    if boolString == "True":
        return True
    elif boolString == "False":
        return False
    else:
        return None

# Adapter configuration
INIFILE = "{0}/tradfri.ini".format(os.path.dirname(os.path.realpath(__file__)))
config = configparser.ConfigParser()
if os.path.exists(INIFILE):
    config.read(INIFILE)
else:
    print("Error: Missing configuration")
    quit()

# Device Configurations
INIFILE = "{0}/devices.ini".format(os.path.dirname(os.path.realpath(__file__)))
deviceDefaults = {"Dimmable": True, "HasWB": True, "HasRGB": False}

deviceConfig = configparser.ConfigParser()

if os.path.exists(INIFILE):
    deviceConfig.read(INIFILE)


loop = asyncio.get_event_loop()

def cleanupTasks():
    for task in asyncio.Task.all_tasks():
       task.cancel()
  
class IkeaFactory():
    gateway = None
    api = None

    devices = None
    groups = None
    lights = None

    deviceIDs = []
    groupIDs = []
    doObserve = False

    def __init__(self):
        pass

    async def heartBeat(self, client, pollinterval):
        i=0

        while 1:
            i=i+1
            if i==pollinterval:
                # print("Sending states")
                loop.create_task(self.sendAllStates(client))
                i=0
            await asyncio.sleep(1)


    async def initGateway(self, client, command):
        print("Setting gateway")
        api_factory = APIFactory(config["Gateway"]["ip"], config["Credentials"]["ident"],config["Credentials"]["psk"])
 
        self.api = api_factory.request
        self.gateway = Gateway()

        if command["observe"]=="True":
            loop.create_task(self.heartBeat(client, int(command["pollinterval"])))

        client.send_data({"action":"setConfig", "status": "Ok"})

    async def getLights(self, client):
        resultDevices = []
        answer = {}
        configChanged = False

        try:
            self.devices = await self.api(await self.api(self.gateway.get_devices()))
            self.groups = await self.api(await self.api(self.gateway.get_groups()))

            answer["action"] = "getLights"
            answer["status"] = "Ok"
        
        except RequestTimeout as err:
            print("GetLights - error: {0}".format(err))
            answer["action"] = "getLights"
            answer["status"] = "Error"
            answer["result"] =  "Request timed out"

        else:
            self.lights = [dev for dev in self.devices if dev.has_light_control]        

            for aLight in self.lights:
                
                if not aLight.device_info.model_number in deviceConfig:
                    print("Device settings not found for {0}. Creating defaults!".format(aLight.device_info.model_number))
                    deviceConfig[aLight.device_info.model_number] = deviceDefaults
                    configChanged = True
                
                levelVal = None
                if aLight.light_control.lights[0].dimmer is not None:
                    levelVal = aLight.light_control.lights[0].dimmer
                else:
                    levelVal = 0
                    
                resultDevices.append({"DeviceID": aLight.id, "Name": aLight.name, "State": aLight.light_control.lights[0].state, "Level": aLight.light_control.lights[0].dimmer, "Hex":aLight.light_control.lights[0].hex_color, "Type": "Light", "Dimmable": stringToBool(deviceConfig[aLight.device_info.model_number]['dimmable']), "HasWB": stringToBool(deviceConfig[aLight.device_info.model_number]['haswb']), "HasRGB": stringToBool(deviceConfig[aLight.device_info.model_number]['hasrgb'])})
                self.deviceIDs.append(aLight.id)

            for aGroup in self.groups:
                #print (aGroup)
                resultDevices.append({"DeviceID": aGroup.id, "Name": "Group - "+aGroup.name, "Type": "Group", "Dimmable": True, "HasWB": False})
                self.groupIDs.append(aGroup.id)

            if configChanged:
                with open(INIFILE, "w") as configfile:
                    deviceConfig.write(configfile)
            
            answer["result"] =  resultDevices

        # loop.create_task(self.startObservations())

        client.send_data(answer)

    async def sendState(self, client, deviceID):
        devices = []
        answer = {}

        answer["action"] = "deviceUpdate"
        deviceID = int(deviceID)

        try:
            if deviceID in self.deviceIDs:
                # print ("Sending state for a device")
                device = await self.api(self.gateway.get_device(deviceID))
                devices.append({"DeviceID": deviceID, "Name": device.name, "State": device.light_control.lights[0].state, "Level": device.light_control.lights[0].dimmer, "Hex": device.light_control.lights[0].hex_color})

            if deviceID in self.groupIDs:
                # print ("Sending state for a group")
                device = await self.api(self.gateway.get_group(deviceID))
                devices.append({"DeviceID": deviceID, "Name": device.name, "State": device.state, "Level": device.dimmer})

            answer["status"] = "Ok"
            answer["result"] =  devices
        except RequestTimeout:
            answer["status"] = "Error"
            answer["result"] =  "Request timed out"
        finally:
            client.send_data(answer)

    async def sendAllStates(self, client):
        for aLight in self.lights:
            loop.create_task(self.sendState(client, aLight.id))

        for aGroup in self.groups:
            loop.create_task(self.sendState(client, aGroup.id))

    async def setState(self, client, command):
        print(command)
        answer = {}
        answer["action"] = "setState"
        answer["status"] = "Ok"
        answer["deviceID"] = command['deviceID']

        deviceID = int(command['deviceID'])
        state = command['state']
        setStateCommand = None

        if state == "On":
            state = True

        if state == "Off":
            state = False
        try:
            if deviceID in self.deviceIDs:
                targetDevice = await self.api(self.gateway.get_device(deviceID))
                setStateCommand = targetDevice.light_control.set_state(state)
                
            if deviceID in self.groupIDs:
                targetGroup = await self.api(self.gateway.get_group(deviceID))
                setStateCommand = targetGroup.set_state(state)

            if setStateCommand is not None:
                await self.api(setStateCommand)

        except RequestTimeout:
            answer["status"] = "Error"
            answer["result"] =  "Request timed out"
        finally:
            client.send_data(answer)
            loop.create_task(self.sendState(client, deviceID))

    async def setLevel(self, client, command):
        answer = {}
        answer["action"] = "setLevel"
        answer["status"] = "Ok"
        answer["deviceID"] = command['deviceID']

        deviceID = int(command['deviceID'])
        level = int(command['level'])
        setStateCommand = None

        try:
            if deviceID in self.deviceIDs:
                targetDevice = await self.api(self.gateway.get_device(deviceID))
                setStateCommand = targetDevice.light_control.set_dimmer(level)
                
            if deviceID in self.groupIDs:
                targetGroup = await self.api(self.gateway.get_group(deviceID))
                setStateCommand = targetGroup.set_dimmer(level)

            if setStateCommand is not None:
                await self.api(setStateCommand)

        except RequestTimeout:
            answer["status"] = "Error"
            answer["result"] =  "Request timed out"
        finally:
            client.send_data(answer)
            loop.create_task(self.sendState(client, deviceID))

    async def setHex(self, client, command):
        
        answer = {}
        answer["action"] = "setHex"
        answer["status"] = "Ok"

        deviceID = int(command['deviceID'])
        targetDevice = await self.api(self.gateway.get_device(deviceID))
        setStateCommand = targetDevice.light_control.set_hex_color(command['hex'])

        try:
            if setStateCommand is not None:
                await self.api(setStateCommand)
                loop.create_task(self.sendState(client, deviceID))
        except RequestTimeout:
            answer["status"] = "Error"
            answer["result"] =  "Request timed out"
        finally:
            client.send_data(answer)

    # Observations

    tasks = []
    taskGroup = None

    async def HeartBeat(self):
        i=0
        while 1:
            print(i)
            if i==10:
                ensure_future(self.startObservations(True))
                i=0
            i=i+1
            await asyncio.sleep(1)

    async def startObservations(self, update=False):
        print("Starting observations")
            
        for light in self.lights:
            observe_command = light.observe(self.observe_callback, self.observe_err_callback,
                                            duration=0)
            ensure_future(self.api(observe_command))
            # await asyncio.sleep(0)

            

    def observe_callback(self, updated_device):
        light = updated_device.light_control.lights[0]
        print("Received message for: %s" % light)

    def observe_err_callback(self, err):
        print('observe error:', err)  

# an instance of EchoProtocol will be created for each client connection.
class IkeaProtocol(asyncio.Protocol):
    transport = None

    factory = IkeaFactory()

    def connection_made(self, transport):
        self.transport = transport
        print("Connected")

        self.send_data({"action": "clientConnect", "status": "Ok", "version": version})

    def data_received(self, data):
        # self.transport.write(data)
        print("Received: {0}".format(data))
        
        decoded = data.decode("utf-8")
        decoded = '[' + decoded.replace('}{', '},{') + ']'
        commands = json.loads(decoded)

        for command in commands:
            if command['action']=="setConfig":
                # print("Setting config")
                loop.create_task(self.factory.initGateway(self, command))

            if command['action']=="getLights":
                loop.create_task(self.factory.getLights(self))

            if command['action']=="getStates":
                loop.create_task(self.factory.getStates(self))

            if command['action']=="setState":
                loop.create_task(self.factory.setState(self, command))

            if command['action']=="setLevel":
                loop.create_task(self.factory.setLevel(self, command))

            if command['action']=="setHex":
                loop.create_task(self.factory.setHex(self, command))

            # if command['action']=="getLights":
            #     self.factory.sendDeviceList(self)

            # if command['action']=="setLevel":
            #     self.factory.setLevel(self, command["deviceID"], command["level"])

            # if command['action']=="setState":
            #     self.factory.setState(self, command["deviceID"], command["state"])

            # if command['action']=="setWB":
            #     self.factory.setWB(self, command["deviceID"], command['hex'])

    def connection_lost(self, exc):
        self.transport.close()
        #server.close()
        
        cleanupTasks()
        print("Disconnected")
        
        # loop.create_task(heartbeat(verbose=True))

    def send_data(self, dict):
        self.transport.write(json.dumps(dict).encode(encoding='utf_8'))



loop = asyncio.get_event_loop()
# loop.create_task(heartbeat(verbose=True))
# Each client connection will create a new protocol instance
coro = loop.create_server(IkeaProtocol, '', 1234)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('IKEA aiocoap-adapter version {0} listening on {1}'.format(version, server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
cleanupTasks()
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
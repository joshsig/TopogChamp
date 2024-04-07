#!/usr/bin/python3

import os
import re
import shutil
import ctypes
import socket
import struct
import datetime
import argparse
import traceback

# Args from the CLI
args = None
# Final msgs to display to user (ex. Complete Load Balancing, ...)
finalTodos = []

###############
## CONSTANTS ##
###############
#CONF_INTRO = """"""
DEFAULT_GW_STRING = "default"
LOCALHOST_IP = "127.0.0.1"
# LOAD BALANCER
LOADBALANCER_RANDOM_MODE = "random"
LOADBALANCER_NTH_MODE = "nth"
# DNS
ROOT_NAME = "."
ROOT_FANCY_NAME = "ROOT"
LOCAL_NAME = "None"
LOCAL_FANCY_NAME = "local"
NAMED_CONF_LINE = "zone \"%s\" {\n\ttype %s;\n\tfile \"/etc/bind/%s\";\n};\n\n"
DB_CONF_HEADER = "$TTL   60000\n@               IN      SOA     %s.%s    root.%s.%s %s 28800 14400 3600000 0\n\n"
# ZEBRA/QUAGGA
ZEBRA_CONF = """!
hostname zebra
password zebra
enable password zebra
!
log file /var/log/zebra/zebra.log"""

RIP_CONF = """!
hostname ripd
password zebra
enable password zebra
!
router rip
! Redistribute
%s
! Networks
%s
!
log file /var/log/zebra/ripd.log"""

OSPF_CONF = """!
hostname ospfd
password zebra
enable password zebra
! Costs Section (can be empty)
%s
!
router ospf
! Redistribute
%s
! Networks
%s
!
log file /var/log/zebra/ospfd.log"""

BGP_CONF = """!
hostname bgpd
password zebra
enable password zebra
!
router bgp %s
! Redistribute
%s
! Announced Networks
%s
! Neighbors
%s
!
log file /var/log/zebra/bgpd.log
!
debug bgp
debug bgp events
debug bgp filters
debug bgp fsm
debug bgp keepalives
debug bgp updates
!"""

#######################
## UTILITY FUNCTIONS ##
#######################
def log(line):
    if args.verbose:
        print(line)

def isValidIP(address):
    parts = address.split('/')[0].split(".") if '/' in address else address.split('.')

    if len(parts) != 4:
        raise Exception("Invalid ip %s." % address)

    for item in parts:
        if (not 1 <= len(item) <= 3) or (not 0 <= int(item) <= 255):
            raise Exception("Invalid ip %s." % address)

def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]

def getNetmaskInfo(ip):
    netmaskLength = -1
    try:
        netmaskLength = int(ip.split("/")[1])
    except Exception:
        raise Exception("Unable to get netmask information from `%s`. Ip addresses should be x.y.z.w/n." % ip)

    netmask = ctypes.c_uint32(0xFFFFFFFF) # 32 bits. using ctypes guarantees that shifts do not overflow
    netmask.value <<= (32 - netmaskLength) # obtain actual netmask

    ipInt = ip2int(ip.split("/")[0]) # converts the ip to a number
    prefix = ipInt & netmask.value

    return prefix, netmask.value

##############
## COMMANDS ##
##############
def _ip(addr, currentState = {}):
    currInterface = currentState["currInterface"]
    currInterface.setIp(addr)

def _to(destination, gw, currentState = {}):
    if destination != DEFAULT_GW_STRING:
        isValidIP(destination)

    isValidIP(gw)

    currInterface = currentState["currInterface"]
    currInterface.gateways.append((destination, gw))

def _webserver(params, currentState = {}):
    # Split matched params on , and spaces
    splittedParams = re.split(r'[,\s]+', params)

    deviceName = splittedParams.pop(0)
    apacheMods = splittedParams

    currLab = currentState["currLab"]
    currDevice = currLab.get(deviceName)
    currDevice.services.append(WebServer(currDevice, apacheMods))

def _balancer(params, currentState = {}):
    # Split matched params on , and spaces
    splittedParams = re.split(r'[,\s]+', params)

    deviceName = splittedParams.pop(0)
    mode = splittedParams.pop(0)
    sourceInterfaceNum = splittedParams.pop(0)
    destinationDevices = splittedParams

    if mode != LOADBALANCER_RANDOM_MODE and mode != LOADBALANCER_NTH_MODE:
        raise Exception("%s mode not supported on Load Balancer `%s`." % (mode, deviceName))

    if len(destinationDevices) <= 0:
        raise Exception("You should declare at least one device managed by Load Balancer `%s`." % deviceName)

    currLab = currentState["currLab"]
    currDevice = currLab.get(deviceName)
    currDevice.services.append(LoadBalancer(currDevice, mode, sourceInterfaceNum, destinationDevices))

def _has_name(name, currentState = {}):
    currDevice = currentState["currDevice"]
    currLab = currentState["currLab"]

    currLab.nameserverTree.addNamedDevice(name, currDevice, currentState["currInterface"])

def _ns_resolv(deviceName, nsName2ifaceNum, currentState = {}):
    currLab = currentState["currLab"]
    currDevice = currLab.get(deviceName)

    # A Device can only have one Local NS
    if currDevice.getServiceByType(NameserverDefault) is None:
        nsName, ifaceNum = nsName2ifaceNum.split("|")
        currDevice.services.append(NameserverDefault(currDevice, nsName, ifaceNum))

def _dns(deviceName, ifaceNum, name, dnsType, currentState = {}):
    currLab = currentState["currLab"]
    currDevice = currLab.get(deviceName)

    currLab.nameserverTree.addDNSDevice(name, dnsType, currDevice, ifaceNum)

    # Nameserver Service should be declared only once on Device.
    if currDevice.getServiceByType(Nameserver) is None:
        currDevice.services.append(Nameserver(currDevice))

def _rip(params, currentState = {}):
    # Split matched params on , and spaces
    splittedParams = re.split(r'[,\s]+', params)

    deviceName = splittedParams.pop(0)
    network = splittedParams.pop(0)
    redistribute = splittedParams

    currLab = currentState["currLab"]
    currDevice = currLab.get(deviceName)

    ripService = currDevice.getServiceByType(Rip)
    # check whether a rip service already exists
    if ripService is None:
        currDevice.services.append(Rip(currDevice, [network], redistribute))
    else:
        ripService.networks.append(network)
        ripService.redistribute.extend(redistribute)

def _ospf(params, currentState = {}):
    # Split matched params on , and spaces
    splittedParams = re.split(r'[,\s]+', params)

    deviceName = splittedParams.pop(0)
    network = splittedParams.pop(0)
    area = splittedParams.pop(0)
    redistribute = splittedParams

    currLab = currentState["currLab"]
    currDevice = currLab.get(deviceName)

    ospfService = currDevice.getServiceByType(OSPF)
    # check whether an ospf service already exists
    if ospfService is None:
        ospfService = OSPF(currDevice, [])
        currDevice.services.append(ospfService)

    ospfService.networks2areas[network] = area
    ospfService.redistribute.extend(redistribute)

def _ospf_cost(cost, currentState = {}):
    currInterfaceIndex = currentState["currInterface"].index
    currDevice = currentState["currDevice"]
    ospfService = currDevice.getServiceByType(OSPF)

    # check whether an ospf service already exists
    if ospfService is None:
        ospfService = OSPF(currDevice, [])
        currDevice.services.append(ospfService)

    ospfService.costs[currInterfaceIndex] = int(cost)

def _bgp(params, currentState = {}):
    # Split matched params on , and spaces
    splittedParams = re.split(r'[,\s]+', params)

    deviceName = splittedParams.pop(0)
    asNum = splittedParams.pop(0)
    neighborName2iface = splittedParams.pop(0)
    redistribute = splittedParams

    currLab = currentState["currLab"]
    currDevice = currLab.get(deviceName)

    bgpService = currDevice.getServiceByType(BGP)
    # check whether a bgp service already exists
    if bgpService is None:
        currDevice.services.append(BGP(currDevice, asNum, neighborName2iface, redistribute))
    else:
        bgpService.neighbors.append(neighborName2iface)

def _bgp_announce(deviceName, network, currentState = {}):
    currLab = currentState["currLab"]
    currDevice = currLab.get(deviceName)

    isValidIP(network)

    bgpService = currDevice.getServiceByType(BGP)
    # check whether a bgp service already exists
    if bgpService is None:
        raise Exception("Cannot announce a BGP network if BGP is not declared on device `%s`." % currDevice.name)

    bgpService.announcedNetworks.append(network)

names2commands = {
    "^ip\\((.+)\\)$": _ip,
    "^to\\((.+)\s?,\s?(.+)\\)$": _to,
    "^webserver(?:\\()(.+)+(?:\\))$": _webserver,
    "^balancer(?:\\()(.+)+(?:\\))$": _balancer,
    "^has_name\\((.+)\\)$": _has_name,
    "^ns_resolv\\((.+)\s?,\s?(.+)\\)$": _ns_resolv,
    "^dns\\((.+)\s?,\s?(.+),\s?(.+),\s?(.+)\\)$": _dns,
    "^rip(?:\\()(.+)+(?:\\))$": _rip,
    "^ospf(?:\\()(.+)+(?:\\))$": _ospf,
    "^ospf_cost\\((.+)\\)$": _ospf_cost,
    "^bgp(?:\\()(.+)+(?:\\))$": _bgp,
    "^bgp_announce\\((.+)\s?,\s?(.+)\\)$": _bgp_announce
}

##############
## SERVICES ##
##############
class Interface(object):
    def __init__(self, device, index):
        self.device = device

        self.index = index
        self.ip = None
        self.gateways = []

    def setIp(self, ip):
        isValidIP(ip)
        self.ip = ip

    def getIp(self, withSubnet = False):
        if withSubnet:
            return self.ip

        return self.ip.split("/")[0]

    def dump(self, startupFile):
        log("\t- Creating interface eth%s with ip %s." % (self.index, self.ip))

        dumpString = "ip address add %s dev eth%s\n" % (self.ip, self.index)
        for gateway in self.gateways:
            netLine = "default"

            if gateway[0] != DEFAULT_GW_STRING:
                netLine = "-net %s" % (gateway[0])

            log("\t\t- Setting %s gateway at %s." % (gateway[0], gateway[1]))
            dumpString += "route add %s gw %s dev eth%s\n" % (netLine, gateway[1], self.index)

        startupFile.write(dumpString)

class WebServer(object):
    def __init__(self, device, mods):
        self.device = device
        self.mods = mods

        self.INDEX_HTML_STUB = "<html>\n\t<body><h1>Courtesy of `%s` webserver.</h1><br /><p>Autogenerated by tacata.py</p></body>\n</html>"

    def dump(self, startupFile):
        log("\t- Adding apache2 and creating index.html.")

        os.makedirs(self.device.name + "/var/www/html")

        # Write autogenerated index.html file
        with open(self.device.name + "/var/www/html/index.html", "w") as indexHtmlFile:
            indexHtmlFile.write(self.INDEX_HTML_STUB % self.device.name)

        for mod in self.mods:
            startupFile.write("a2enmod %s\n" % mod)

        startupFile.write("systemctl start apache2\n")

class LoadBalancer(object):
    def __init__(self, device, mode, sourceInterfaceNum, destinationDevices):
        self.device = device

        self.mode = mode
        self.sourceInterfaceNum = sourceInterfaceNum
        self.destinationDevices = destinationDevices

    def dump(self, startupFile):
        log("\t- Creating load balancing on %s with `%s` mode." % (self.sourceInterfaceNum, self.mode))

        finalTodos.append("- Complete the iptables commands in %s.startup file with balancing information." % self.device.name)

        sourceIp = self.device.getInterfaceByNum(self.sourceInterfaceNum).getIp()

        for i, name2iface in enumerate(self.destinationDevices):
            name, interfaceNum = name2iface.split("|")
            destIp = self.device.lab.get(name).getInterfaceByNum(interfaceNum).getIp()

            log("\t\t- Adding device `%s` (%s - %s) rule." % (name, destIp, interfaceNum))

            ipTablesParams = ""
            if i < len(self.destinationDevices) - 1:
                ipTablesParams = "-m statistic --mode random --probability ##PROB##"
                if self.mode == LOADBALANCER_NTH_MODE:
                    ipTablesParams = "-m statistic --mode nth --every ##N##"

            startupFile.write("iptables -t nat -A PREROUTING -d %s %s -j DNAT --to-destination %s\n" % (sourceIp, ipTablesParams, destIp))

class NameserverDefault(object):
    def __init__(self, device, nsName, nsIface):
        self.device = device

        self.nsName = nsName
        self.nsIface = nsIface

    def dump(self, startupFile):
        # Sometimes /etc/ folder already exists...
        if not os.path.exists(self.device.name + "/etc/"):
            os.makedirs(self.device.name + "/etc/")

        with open(self.device.name + "/etc/resolv.conf", "w") as resolvFile:
            if self.device.name == self.nsName: # If device configured is ALSO local NS for the device
                nsIp = LOCALHOST_IP
            else:
                nsIp = self.device.lab.get(self.nsName).getInterfaceByNum(self.nsIface).getIp()

            log("\t- Local nameserver for this device is `%s` (%s)." % (self.nsName, nsIp))

            # Write NS IP
            resolvFile.write("nameserver %s\n" % nsIp)

            # Search Name for this NS Device
            name = self.device.lab.nameserverTree.getNameByDevice(self.nsName)
            if name != None: # If local DNS (or not declared), skip the line
                name = name[:-1] # Purge last dot
                resolvFile.write("search %s" % name)

class Nameserver(object):
    def __init__(self, device):
        self.device = device

    def dump(self, startupFile):
        # Write bind startup in startup file
        startupFile.write("systemctl start bind9\n")

        # Prepare bind directory for Nameserver dump
        os.makedirs(self.device.name + "/etc/bind")

    # Writes a line in the named.conf file
    def writeNamedConfLine(self, zone, type, fileName):
        with open(self.device.name + "/etc/bind/named.conf", "a") as namedFile:
            namedFile.write(NAMED_CONF_LINE % (zone, type, fileName))

    # Write db file.
    def writeDbFile(self, name, type, fileName, lines, newDeviceName = None):
        with open(self.device.name + "/etc/bind/" + fileName, "a") as dbFile:
            if type == "master": # Write db header when master
                deviceName = self.device.name
                if newDeviceName != None:
                    deviceName = newDeviceName

                today = datetime.date.today() # Used to generate serial for SOA line
                dbFile.write(DB_CONF_HEADER % (deviceName, name, deviceName, name, today.strftime("%Y%m%d%U")))

            for line in lines:
                dbFile.write(line)

class Zebra(object):
    # redistribuible routes
    REDISTRIBUIBLE = {"connected", "rip", "ospf", "bgp", "kernel"}

    def __init__(self, device):
        self.device = device

    def shouldInitZebra(self):
        # only the first zebra service should init zebra
        zebraServices = self.device.getServicesByType(Zebra)
        return zebraServices != [] and zebraServices[0] is self

    def buildRedistributeString(self, redistribute):
        redistributeString = ""
        for red in set(redistribute):
            if red not in self.REDISTRIBUIBLE:
                raise Exception("Cannot redistribute `%s` use one of: %s." % (red, list(self.REDISTRIBUIBLE)))

            redistributeString += "redistribute %s\n" % red

        return redistributeString

    def dumpZebraConf(self):
        with open(self.device.name + "/etc/quagga/zebra.conf", "w") as zebraFile:
            zebraFile.write(ZEBRA_CONF)

    def addDaemon(self, deamonName):
        with open(self.device.name + "/etc/quagga/daemons", "a") as deamonFile:
            deamonFile.write("%s=yes\n" % deamonName)

    def dump(self, startupFile):
        if not os.path.exists(self.device.name + "/etc/quagga"):
            os.makedirs(self.device.name + "/etc/quagga")

        if self.shouldInitZebra():
            startupFile.write("/etc/init.d/zebra start\n")
            self.dumpZebraConf()
            self.addDaemon("zebra")

class Rip(Zebra):
    def __init__(self, device, networks = [], redistribute = []):
        super(Rip, self).__init__(device)

        self.networks = networks
        self.redistribute = redistribute

    def getNetworks(self):
        networksStr = ""
        for network in self.networks:
            isValidIP(network)
            networksStr += "network %s\n" % network

        return networksStr

    def dump(self, startupFile):
        super(Rip, self).dump(startupFile)

        self.addDaemon("ripd")

        self.networks = set(self.networks) # Removes duplicated networks

        with open(self.device.name + "/etc/quagga/ripd.conf", "w") as ripFile:
            redistributeString = super(Rip, self).buildRedistributeString(self.redistribute)
            ripFile.write(RIP_CONF % (redistributeString, self.getNetworks()))

        log("\t- Adding RIP daemon in Zebra/Quagga (redistributes: %s)..." % self.redistribute)
        for network in self.networks:
                log("\t\t- Network %s added to RIP." % network)

        finalTodos.append("- Complete the RIP ripd.conf configuration file of device `%s` (if required)." % self.device.name)

class OSPF(Zebra):
    def __init__(self, device, redistribute = []):
        super(OSPF, self).__init__(device)

        self.networks2areas = dict()
        self.redistribute = redistribute
        self.costs = {} # interface -> cost

    def getCosts(self):
        costStr = ""
        for ifaceNum in self.costs:
            costStr += "interface eth%s\nospf cost %d\n" % (ifaceNum, self.costs[ifaceNum])

        return costStr

    def getNetworksAndAreas(self):
        netAndAreas = ""

        areasSet = []

        for network in self.networks2areas:
            area = self.networks2areas[network]

            isValidIP(network)
            isValidIP(area)
            netAndAreas += "network %s area %s\n" % (network, area)

            areasSet.append(area)

        stubs = set(areasSet) - {"0.0.0.0"} # 0.0.0.0 should not be added to stub areas
        for stub in stubs:
            netAndAreas += "area %s stub\n" % stub

        return netAndAreas

    def dump(self, startupFile):
        if self.networks2areas == []:
            raise Exception("Cost specified but OSPF not configured for device `%s`." % self.device.name)

        super(OSPF, self).dump(startupFile)

        self.addDaemon("ospfd")

        with open(self.device.name + "/etc/quagga/ospfd.conf", "w") as ospfFile:
            redistributeString = super(OSPF, self).buildRedistributeString(self.redistribute)
            ospfFile.write(OSPF_CONF % (self.getCosts(), redistributeString, self.getNetworksAndAreas()))

        log("\t- Adding OSPF daemon in Zebra/Quagga (redistributes: %s)..." % self.redistribute)
        for ifaceNum in self.costs:
            log("\t\t- Interface eth%s has cost %d." % (ifaceNum, self.costs[ifaceNum]))
        for network in self.networks2areas:
            log("\t\t- Network %s (belonging to area %s) added to OSPF." % (network, self.networks2areas[network]))

        finalTodos.append("- Complete the OSPF ospfd.conf configuration file of device `%s` (if required)." % self.device.name)

class BGP(Zebra):
    def __init__(self, device, asNum, neighborName2iface, redistribute = []):
        super(BGP, self).__init__(device)

        self.asNum = asNum
        self.neighbors = [neighborName2iface]
        self.redistribute = redistribute
        self.announcedNetworks = []

    def parseNeighbor(self, neighborName2iface):
        name, iface = neighborName2iface.split("|")
        otherDevice = self.device.lab.get(name)

        ip = otherDevice.getInterfaceByNum(iface).getIp()
        asNum = otherDevice.getServiceByType(BGP).asNum

        return ip, name, asNum

    def getNeighbors(self):
        neighStr = ""

        for neighborName2iface in self.neighbors:
            ip, neighborName, asNum = self.parseNeighbor(neighborName2iface)
            isValidIP(ip)
            neighStr += "neighbor %s remote-as %s\nneighbor %s description Router %s of AS%s\n" % (ip, asNum, ip, neighborName, asNum)

            log("\t\t- Adding neighbor %s (with AS Number %s)." % (ip, asNum))

        return neighStr

    def getAnnouncedNetworks(self):
        netStr = ""

        for network in set(self.announcedNetworks):
            netStr += "network %s\n" % network

        return netStr

    def dump(self, startupFile):
        super(BGP, self).dump(startupFile)

        self.addDaemon("bgpd")

        log("\t- Adding BGP daemon in Zebra/Quagga (redistributes: %s)..." % self.redistribute)

        with open(self.device.name + "/etc/quagga/bgpd.conf", "w") as bgpFile:
            redistributeString = super(BGP, self).buildRedistributeString(self.redistribute)
            bgpFile.write(BGP_CONF % (self.asNum, redistributeString, self.getAnnouncedNetworks(), self.getNeighbors()))

        finalTodos.append("- Complete the BGP bgpd.conf configuration file of device `%s` (if required)." % self.device.name)

#####################
## GENERIC CLASSES ##
#####################
class Device(object):
    def __init__(self, lab, name):
        self.lab = lab
        self.name = name
        self.services = []

    def dump(self):
        log("- Dumping device `%s`..." % self.name)

        os.mkdir(self.name)
        with open(self.name + ".startup", "w") as deviceFile:
            for service in self.services:
                service.dump(deviceFile)

    # Returns a specific eth interface declared on the Device.
    def getInterfaceByNum(self, index):
        if index.startswith("eth"):
            index = index.replace("eth", "")

        for service in self.services:
            if isinstance(service, Interface) and index == service.index:
                return service

        raise Exception("Interface %s not found on device `%s`." % (index, self.name))

    # Checks if the Device has a specified Service, if so return the first instance. If not, return None.
    def getServiceByType(self, serviceType):
        for service in self.services:
            if isinstance(service, serviceType):
                return service

        return None

    def getServicesByType(self, serviceType):
        return [service for service in self.services if isinstance(service, serviceType)]

class NameserverNode(object):
    def __init__(self, name):
        self.name = name            # Name of the zone: ex. lugroma3.org.
        self.hostnames2ifaces = []  # Devices which aren't involved as nameservers, couple (hostname (ex. www), Interface instance)
        self.nsDevices2types2ifaces = []   # Devices which are part of NS infrastructure, couple (Device instance, NS type (ex. master))
        self.servedNames = {}       # Children served names of the current name

    def dump(self, rootLines):
        isRoot = False
        nameToUse = self.name

        # We're on root, assign db standard name "db.root"
        if self.name == ROOT_NAME:
            dbFileName = "db.root"
            isRoot = True
        else: # We're not on root, db name = current node name - last dot
            dbFileName = "db." + self.name[:-1]
            nameToUse = nameToUse[:-1]

        log("- Dumping `%s` zone..." % self.name)
        if len(self.servedNames) > 0:
            log("\t- Known zones are:")
            for name in self.servedNames:
                log("\t\t- %s" % name)

        if len(self.hostnames2ifaces) > 0:
            log("\t- Known hosts are:")
            for hostname2iface in self.hostnames2ifaces:
                log("\t\t- `%s` at %s" % (hostname2iface[0], hostname2iface[1].getIp()))

        # Foreach nameserver device declared in the current node.
        for device2type2iface in self.nsDevices2types2ifaces:
            log("\t- Adding device `%s` as %s for this zone." % (device2type2iface[0].name, device2type2iface[1]))

            nameserverService = device2type2iface[0].getServiceByType(Nameserver)

            # We're not in root, write db.root line & file.
            if not isRoot:
                nameserverService.writeNamedConfLine(ROOT_NAME, "hint", "db.root")
                nameserverService.writeDbFile(None, "hint", "db.root", rootLines)

            # Write Info About Served Names in named.conf file
            nameserverService.writeNamedConfLine(nameToUse, device2type2iface[1], dbFileName)

            dbLines = []
            # Info about myself
            deviceName = device2type2iface[0].name
            name = self.name

            # Special names for root node.
            if isRoot:
                deviceName = "ROOT-SERVER"
                name = ""

            dbLines.append("@     IN  NS  %s.%s\n" % (deviceName, name))
            if isRoot:
                deviceName += "."

            dbLines.append("%s    IN  A   %s\n\n" % (deviceName, device2type2iface[2].getIp()))

            if len(self.servedNames) > 0:    # I'm not a leaf, tell what I know about my children
                for servedName in self.servedNames:
                    childInfo = self.servedNames[servedName]
                    shortName = childInfo.name

                    if not isRoot:
                        # Example: fullName = lugroma3.org. => shortName = lugroma3
                        # Why `not isRoot`? Because in root we want => org. instead of => org!
                        shortName = childInfo.name.replace(self.name, "")[:-1]

                    for childDevice2type2iface in childInfo.nsDevices2types2ifaces:
                        dbLines.append("%s    IN  NS  %s.%s\n" % (shortName, childDevice2type2iface[0].name, childInfo.name))
                        dbLines.append("%s.%s IN  A   %s\n\n" % (childDevice2type2iface[0].name, shortName, childDevice2type2iface[2].getIp()))

            dbLines.append("\n")

            if len(self.hostnames2ifaces) > 0: # I have some registered hosts!
                for hostname2iface in self.hostnames2ifaces:
                    dbLines.append("%s IN  A   %s\n" % (hostname2iface[0], hostname2iface[1].getIp()))

            newDeviceName = None
            if isRoot:
                newDeviceName = deviceName[:-1]

            nameserverService.writeDbFile(name, device2type2iface[1], dbFileName, dbLines, newDeviceName)

class NameserverTree(object):
    def __init__(self):
        self.root = NameserverNode(ROOT_NAME)                # Root Nameserver Node, here everything starts.
        self.local = NameserverNode("~")                     # Nodes without any authority, they only know information about root nodes.

    def addDNSDevice(self, name, dnsType, device, ifaceNum):
        iface = device.getInterfaceByNum(ifaceNum)

        if name == ROOT_NAME or name == ROOT_FANCY_NAME: # This is a root NS, add it to the roots
            self.root.nsDevices2types2ifaces.append((device, dnsType, iface))
            return

        if name == LOCAL_NAME: # No name defined
            if dnsType != LOCAL_FANCY_NAME: # Type MUST be local!
                raise Exception("You should declare a name if type isn't `%s` on `%s`" % (LOCAL_FANCY_NAME, device.name))

            self.local.nsDevices2types2ifaces.append(device)
            return

        if name.endswith('.'):
            name = name[:-1] # Purge last dot if declared

        # Start tree recursion
        names = name.split('.')
        self._addToName(self.root, names, "", "nsDevices2types2ifaces", device, dnsType, iface)

    def addNamedDevice(self, name, device, iface):
        if name == ROOT_NAME or name == ROOT_FANCY_NAME:
            raise Exception("You can't add a named host to the root DNS name!")

        if name.endswith('.'):
            name = name[:-1] # Purge last dot if declared

        names = name.split('.')
        hostName = names.pop(0) # Gets hostname, example: pc1.lugroma3.org => pc1

        self._addToName(self.root, names, "", "hostnames2ifaces", hostName, None, iface)

    def _addToName(self, parentNode, names, name, devType, device, dnsType, iface):
        nextName = names.pop()
        finalName = nextName + "." + name

        # Add Served Name to the current namenode.
        if nextName not in parentNode.servedNames:
            parentNode.servedNames[nextName] = NameserverNode(finalName)

        # End of recursion
        if len(names) == 0:
            if dnsType == None: # Named host, not part of NS infrastructure, only append couple (hostname, iface)
                toAppend = (device, iface)
            else: # Part of NS infrastructure, append triple (device, type, iface)
                toAppend = (device, dnsType, iface)

            devices = getattr(parentNode.servedNames[nextName], devType)
            # Append device to the current name.
            devices.append(toAppend)
            setattr(parentNode.servedNames[nextName], devType, devices)

            return

        # Still some nodes to traverse, launch recursion on children
        self._addToName(parentNode.servedNames[nextName], names, finalName, devType, device, dnsType, iface)

    def dump(self):
        if len(self.root.nsDevices2types2ifaces) == 0: # No nameservers in root, don't dump DNS
            log("- Nameserver tree is empty. Nothing to dump.")
            return

        # Lines for db.root file (when current node is local or not root NS)
        rootLines = []
        rootLines.append(". IN  NS  ROOT-SERVER.\n")
        for device2type2iface in self.root.nsDevices2types2ifaces:
            rootLines.append("ROOT-SERVER.  IN  A   %s" % (device2type2iface[2].getIp()))

        # Dump the NS tree for real.
        self._realDump(self.root, rootLines)

        # Dump local NS
        self._dumpLocals(rootLines)

    def _realDump(self, currentNode, rootLines):
        currentNode.dump(rootLines)

        # Foreach served name, do the same stuff.
        for servedName in currentNode.servedNames:
            self._realDump(currentNode.servedNames[servedName], rootLines)

    def _dumpLocals(self, rootLines):
        for device in self.local.nsDevices2types2ifaces:
            log("- `%s` is a local nameserver (only knows information about roots)..." % device.name)

            nameserverService = device.getServiceByType(Nameserver)

            nameserverService.writeNamedConfLine(ROOT_NAME, "hint", "db.root")
            nameserverService.writeDbFile(None, "hint", "db.root", rootLines)

    def getNameByDevice(self, deviceName):
        return self._getNameByDeviceRecursive(self.root, deviceName)

    def _getNameByDeviceRecursive(self, currentNode, deviceName):
        # Scan in current DNS devices
        for device2type2iface in currentNode.nsDevices2types2ifaces:
            # If we found the device
            if device2type2iface[0].name == deviceName:
                # Return the name of this node
                return currentNode.name

        # No luck, search in children
        for servedName in currentNode.servedNames:
            result = self._getNameByDeviceRecursive(currentNode.servedNames[servedName], deviceName)

            if result != None:
                return result

        # No luck in children, return None
        return None

class Lan(object):
    def __init__(self, lab, name):
        self.lab = lab
        self.name = name
        self.interfaces = []

        # data representing ips for this lan
        # all interfaces on the same lan should be compliant
        self.netmask = None
        self.prefix = None

    def addInterface(self, iface):
        ifaceNetmask, ifacePrefix = getNetmaskInfo(iface.getIp(withSubnet = True))

        if len(self.interfaces) == 0: # this is the first interface, lets set netmask and prefix
            self.netmask = ifaceNetmask
            self.prefix = ifacePrefix
        if ifaceNetmask != self.netmask or ifacePrefix != self.prefix:
            raise Exception("Interface `%s` in LAN `%s` has different prefix!" % (iface.index, self.name))

        self.interfaces.append(iface)

class Lab(object):
    def __init__(self):
        # configuration for netkit lab.conf
        self.confLines = []
        self.name2devices = {}
        self.name2lans = {}
        self.nameserverTree = NameserverTree()
        self.labDir = (args.dir or ".") + "/lab"

        if os.path.exists(self.labDir):
            if args.force:
                shutil.rmtree(self.labDir, ignore_errors = True)
            else:
                print("A lab already exists in this directory. Use -f to force deletion.")
                exit()

        os.mkdir(self.labDir)
        os.chdir(self.labDir)

    def addConfLine(self, line):
        self.confLines.append(line)

    def getOrNew(self, name):
        if name not in self.name2devices:
            self.name2devices[name] = Device(self, name)

        return self.name2devices[name]

    def get(self, name):
        return self.name2devices[name]

    def getLan(self, lanName):
        return self.name2lans[lanName]

    def getOrNewLan(self, lanName):
        if lanName not in self.name2lans:
            self.name2lans[lanName] = Lan(self, lanName)

        return self.getLan(lanName)

    def dump(self):
        log("\n============= WRITING lab.conf FILE =============")
        confString = "\n".join(self.confLines)
        #confString = CONF_INTRO + confString
        with open("lab.conf", "w", newline='\n') as labConfFile:
            labConfFile.write(confString)

        log("- Done!")

        log("================ DUMPING DEVICES ================")
        for device in self.name2devices:
            self.name2devices[device].dump()

        log("============ DUMPING NAMESERVER TREE ============")
        self.nameserverTree.dump()

        print("================= DUMPING DONE! =================")
        for i, todo in enumerate(finalTodos):
            print("\t" + str(i + 1) + " " + todo)

def parseDeviceAndInterface(declaration):
    if declaration == "":
        return None, None
    matches = re.search("(.*)\\[(\d+)\\]=\"?(\w+)\"?", declaration)

    if matches is None or len(matches.groups()) != 3:
        raise Exception("Wrong interface declaration. Should be <device>[<interface_number>]=<lan>.")

    return matches.groups()

def parseCommands(commandString, **kwargs):
    commands = commandString.split(";")
    commands = [command.strip() for command in commands if command.strip() != ""] # trim em all
    for command in commands:
        commandFound = False

        for commandRe in names2commands:
            matches = re.search(commandRe, command)
            if matches is not None:
                args = matches.groups()
                names2commands[commandRe](*args, currentState=kwargs)
                commandFound = True
                break
        if not commandFound:
            raise Exception("Command `%s` not declared!" % command)

def launch_lab():
    if args.run:
        os.system("$NETKIT_HOME/lwipe")
        os.system("$NETKIT_HOME/lstart")

def parse():
    print("####################################################")
    print("#                                                  #")
    print("#              WELCOME TO TACATA                   #")
    print("#    A lightweight Python Kathara lab generator    #")
    print("#                                                  #")
    print("####################################################")
    print("")

    currentLine = 0
    try:
        currLab = Lab()
        with open("../lab.confu", "r") as labfile:
            log("- `lab.confu` file found in specified folder, starting dump...")

            for line in labfile:
                currentLine += 1

                line = line.replace("\r", "").replace("\n", "").rstrip()
                print(line)
                if line == "" or line.startswith("#"): # Skip empty lines and comments
                    continue

                netkitDef, commands = line.split("$")
                netkitDef = netkitDef.strip()

                currDevice, currInterface, currLan = None, None, None

                if netkitDef != "":
                    currLab.addConfLine(netkitDef)

                    currDeviceName, currInterfaceNum, currLanName = parseDeviceAndInterface(netkitDef)

                    currDevice = currLab.getOrNew(currDeviceName)
                    currInterface = Interface(currDevice, currInterfaceNum)
                    currDevice.services.append(currInterface)

                    currLan = currLab.getOrNewLan(currLanName)

                parseCommands(commands, currDevice = currDevice, currInterface = currInterface, currLab = currLab)

                # after commands are parsed so that ip is set on interface
                if currLan is not None:
                    currLan.addInterface(currInterface)

        currLab.dump()
    except Exception as e:
        print("Error at line %d: %s" % (currentLine, str(e)))

        if args.testing:
            traceback.print_exc(e)

        exit()

if __name__ == '__main__':
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-d", "--dir", help="The directory where lab.confu is stored. Default is current directory.")
    argParser.add_argument("-v", "--verbose", help="Enables output verbosity.", action="store_true")
    argParser.add_argument("-r", "--run", help="Runs the created lab.", action="store_true")
    argParser.add_argument("-f", "--force", help="Deletes previous labs if any.", action="store_true")
    argParser.add_argument("-t", "--testing", help="Runs in debugging mode", action="store_true")
    args = argParser.parse_args()

    parse()
    launch_lab()

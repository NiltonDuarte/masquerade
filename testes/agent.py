#!/root/wishful/dev/bin/python
# -*- coding: utf-8 -*-

import logging
import wishful_framework as msgs
import wishful_agent
import yaml
import platform
import time
import netifaces as ni
import threading


log = logging.getLogger('wishful_agent')
logLevel = logging.DEBUG
logging.basicConfig(level=logLevel, format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s',
                    filename="/tmp/wishful_agent.log")

#Create and configure
agent = wishful_agent.Agent()

name = "WishfulAgent-{0}".format(platform.node()) #Returns the computer’s network name
info = "Wishful Agent on {0} node. {1}".format(platform.node(), platform.uname())
groupName = "wishful_icarus"
agent.set_agent_info(name=name, info=info, iface="eth0")

agent.add_module(moduleName="discovery", pyModule="wishful_module_discovery_pyre", 
                 className="PyreDiscoveryAgentModule", kwargs={"iface":"eth0", "groupName":groupName})

agent.add_module(moduleName="wmp", pyModule="wishful_module_wifi_wmp", 
                 className="WmpModule", interfaces=['wlan0'])

txQList = []
txBytesList = []
def gatherTxQueueStatistics():
    """From proc manual
       /proc/net/tcp
              Holds a dump of the TCP socket table.  Much of the information is not of use apart from debugging.  The "sl" value is the kernel hash slot for the socket,  the  "local_address"  is
              the  local  address  and port number pair.  The "rem_address" is the remote address and port number pair (if connected).  "St" is the internal status of the socket.  The "tx_queue"
              and "rx_queue" are the outgoing and incoming data queue in terms of kernel memory usage.  The "tr", "tm->when", and "rexmits" fields hold internal information of the kernel  socket
              state and are only useful for debugging.  The "uid" field holds the effective UID of the creator of the socket.
       /proc/net/udp
              Holds  a  dump  of the UDP socket table.  Much of the information is not of use apart from debugging.  The "sl" value is the kernel hash slot for the socket, the "local_address" is
              the local address and port number pair.  The "rem_address" is the remote address and port number pair (if connected). "St" is the internal status of the socket.  The "tx_queue" and
              "rx_queue"  are  the  outgoing  and incoming data queue in terms of kernel memory usage.  The "tr", "tm->when", and "rexmits" fields are not used by UDP.  The "uid" field holds the
              effective UID of the creator of the socket.  The format is:
        The format is:
         sl  local_address rem_address   st tx_queue rx_queue tr rexmits  tm->when uid
          1: 01642C89:0201 0C642C89:03FF 01 00000000:00000001 01:000071BA 00000000 0
          1: 00000000:0801 00000000:0000 0A 00000000:00000000 00:00000000 6F000100 0
          1: 00000000:0201 00000000:0000 0A 00000000:00000000 00:00000000 00000000 0
    """
    global txQList
    global txBytesList
    iface="wlan0"
    #get iface ip addr and mask list
    ip_maskList = [(inetaddr['addr'],inetaddr['netmask']) for inetaddr in ni.ifaddresses(iface)[ni.AF_INET]]
    #convert to list of int
    ip_maskList = [([int(x) for x in ip.split(".")], [int(x) for x in mask.split(".")]) for (ip,mask) in ip_maskList]
    #make bitwise and with ip and mask to get the networkAddr prefix
    networkAddr = [[x&y for (x,y) in zip(ipList,maskList)] for (ipList,maskList) in ip_maskList]
    udpF = open("/proc/net/udp")
    tcpF = open("/proc/net/tcp")
    devF = open("/proc/net/dev")
    i = 0
    while True:
        currTxQ = 0
        time.sleep(0.2)
        devF.seek(0)
        udpF.seek(0)
        tcpF.seek(0)
        udpF.readline()
        for line in udpF:
            #get the tx_queue
            txQ = line.split()[4].split(":")[0]
            txQ = int(txQ, 16)
            #get remote addr
            remIP = line.split()[2].split(":")[0]
            remIP = ["".join(x) for x in zip(*[iter(remIP)]*2)]
            remIP = [int(x, 16) for x in remIP]
            remIP = remIP[::-1]
            #check if the remote addr is in the same range any of the wlan0 network addresses prefix
            #Wlan0AddrRangeCheck = [netAddr==checkedAddr for (netAddr,checkedAddr) in zip(networkAddr,[[x&y for (x,y) in zip(remIP,netAddr)] for netAddr in networkAddr])]
            Wlan0AddrRangeCheck = [[x&y for (x,y) in zip(remIP,netAddr)]==netAddr for netAddr in networkAddr]
            if True in Wlan0AddrRangeCheck and txQ>0:
                currTxQ += txQ
        tcpF.readline()
        for line in tcpF:
            #get the tx_queue
            txQ = line.split()[4].split(":")[0]
            txQ = int(txQ, 16)
            #get remote addr
            remIP = line.split()[2].split(":")[0]
            remIP = ["".join(x) for x in zip(*[iter(remIP)]*2)]
            remIP = [int(x, 16) for x in remIP]
            remIP = remIP[::-1]
            #Wlan0AddrRangeCheck = [netAddr==checkedAddr for (netAddr,checkedAddr) in zip(networkAddr,[[x&y for (x,y) in zip(remIP,netAddr)] for netAddr in networkAddr])]
            Wlan0AddrRangeCheck = [[x&y for (x,y) in zip(remIP,netAddr)]==netAddr for netAddr in networkAddr]
            if True in Wlan0AddrRangeCheck and txQ>0:
                currTxQ += txQ
        txQList.append(currTxQ)
        for line in devF:
            splittedLine = line.split()
            iface = splittedLine[0][:-1]
            if iface == "wlan0":
                txBytesList.append(int(splittedLine[9]))

def sendStatistics():
    global txQList
    global txBytesList
    dest = "controller"
    while True:
        if agent.controllerMonitor.connectedToController:
            ret = str(txQList,txBytesList)
            txQList = []
            txBytesList = []
            respDesc = msgs.CmdDesc()
            respDesc.type = "ProactiveStatistics"
            respDesc.func_name = gatherTxQueueStatistics.__name__
            response = [dest, respDesc, ret]
            agent.send_upstream(response)
        time.sleep(5)

try:
    #Start agent
    stat_thread = threading.Thread(target=gatherTxQueueStatistics)
    stat_thread.daemon = True
    stat_thread.start()
    send_thread = threading.Thread(target=sendStatistics)
    send_thread.daemon = True
    send_thread.start()
    agent.run()

except KeyboardInterrupt:
    print("Agent exits")
finally:
    #Stop agent
    agent.stop()
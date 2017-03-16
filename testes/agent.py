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


import subprocess
import re
import datetime

#===== Those class should be in a separated file, I've kept in a single file for sake of simplicity ===============

class WMPy:
    def __init__(self):
        self.reg1 = None
        self.reg2 = None
        self.mem1 = None
        self.mem2 = None
        self.mem3 = None
        self.currBytecode = None
        self.path = '/root/bytecode-manager/bytecode-manager'
    def updateView(self):
        p = subprocess.Popen(self.path+ ' -v', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            line = line.decode()
            pos = line.find('=')+2
            if 'CURRENT BYTECODE' in line:
                self.currBytecode = int(line[pos:],16)
            elif 'Register 1' in line:
                self.reg1 = int(line[pos:],16)
            elif 'Register 2' in line:
                self.reg2 = int(line[pos:],16)
            elif 'Memory 1' in line:
                self.mem1 = int(line[pos:],16)
            elif 'Memory 2' in line:
                self.mem2 = int(line[pos:],16)
            elif 'Memory 3' in line:
                self.mem3 = int(line[pos:],16)
        retval = p.wait()
    def load(self, bytecodePath, position):
        p = subprocess.Popen(self.path + ' -l '+str(position) + ' -m '+ bytecodePath, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def active(self, position):
        p = subprocess.Popen(self.path + ' -a '+str(position), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def __repr__(self):
        ret= "Current Bytecode = " + str(self.currBytecode) + '\n'
        ret+= "Registro 1 (Var1) = " + str(self.reg1) + '\n'
        ret+= "Registro 2 (Var2) = " + str(self.reg2) + '\n'
        ret+= "Memory 1 (Var3) = " + str(self.mem1) + '\n'
        ret+= "Memory 2 (Var4) = " + str(self.mem2) + '\n'
        ret+= "Memory 3 (Var5) = " + str(self.mem3)
        return ret

class AgentStatistics:
    def __init__(self, agent, iface):
        self.agent = agent
        self.iface = iface
        self.gatherInterval = 0.2
        self.sendInterval = 1
        self.statisticsFunctions = []
        self.processFunctions = []
        self.ip_maskList = None
        self.networkAddr = None
        self.gatheredData = {}
        self.dataLock = threading.Lock()
        self.updateSystemInfo()
    def start(self):       
        gather_thread = threading.Thread(target=self.startGathering)
        gather_thread.daemon = True
        gather_thread.start()
        send_thread = threading.Thread(target=self.startSending)
        send_thread.daemon = True
        send_thread.start()
    def startGathering(self):
        while True:
            time.sleep(self.gatherInterval)
            with self.dataLock:
                for (func, varargs, kwargs) in self.statisticsFunctions:
                    ret = func(*varargs, **kwargs)
                    if func.__name__ in self.gatheredData:
                        self.gatheredData[func.__name__].append(ret)
                    else:
                        self.gatheredData[func.__name__] = [ret]
                #print("func {} - ret {}".format(func.__name__, ret))
    def startSending(self):
        while True:
            time.sleep(self.sendInterval)
            with self.dataLock:
                dataCopy = self.gatheredData.copy()
                self.gatheredData = {}
            self.sendStatistics(dataCopy)
    def sendStatistics(self, data):
        dest = "controller"
        msg = {}
        if self.agent.controllerMonitor.connectedToController:
            for (func, varargs, kwargs) in self.processFunctions:
                kw, values = func(data, *varargs, **kwargs)
                msg[kw] = values
            msg = str(msg)
            respDesc = msgs.CmdDesc()
            respDesc.type = "AgentStatistics"
            respDesc.func_name = 'AgentStatistics'
            respDesc.serialization_type = msgs.CmdDesc.PICKLE
            response = [dest, respDesc, msg]
            self.agent.send_upstream(response)
    def addGatheringFunction(self, func, *varargs, **kwargs):
        self.statisticsFunctions.append((func, varargs, kwargs))
    def addProcessFunction(self, func, *varargs, **kwargs):
        self.processFunctions.append((func, varargs, kwargs))
    def updateSystemInfo(self):
        #get iface ip addr and mask list
        ip_maskList = [(inetaddr['addr'],inetaddr['netmask']) for inetaddr in ni.ifaddresses(self.iface)[ni.AF_INET]]
        #convert to list of int
        ip_maskList = [([int(x) for x in ip.split(".")], [int(x) for x in mask.split(".")]) for (ip,mask) in ip_maskList]
        #make bitwise and with ip and mask to get the networkAddr prefix
        networkAddr = [[x&y for (x,y) in zip(ipList,maskList)] for (ipList,maskList) in ip_maskList]
        self.ip_maskList = ip_maskList
        self.networkAddr = networkAddr
    def gatherLostPacketsCounter(self):
        wmpy = WMPy()
        wmpy.updateView()
        lostCounter = wmpy.mem1
        return lostCounter
    def gatherTxBytes(self):
        #devF = open("/proc/net/dev")
        with open("/proc/net/dev") as devF:
            for line in devF:
                splittedLine = line.split()
                iface = splittedLine[0][:-1]
                if iface == self.iface:
                    return int(splittedLine[9])
    def gatherNumberOfConnections(self):
        conns = 0
        with open("/proc/net/udp") as udpF:
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
                Wlan0AddrRangeCheck = [[x&y for (x,y) in zip(remIP,netAddr)]==netAddr for netAddr in self.networkAddr]
                if True in Wlan0AddrRangeCheck:
                    conns += 1
        with open("/proc/net/tcp") as tcpF:
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
                Wlan0AddrRangeCheck = [[x&y for (x,y) in zip(remIP,netAddr)]==netAddr for netAddr in self.networkAddr]
                if True in Wlan0AddrRangeCheck:
                    conns += 1
        return conns
    def gatherTxQueue(self):
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
        #udpF = open("/proc/net/udp")
        #tcpF = open("/proc/net/tcp")
        currTxQ = 0
        with open("/proc/net/udp") as udpF:
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
                Wlan0AddrRangeCheck = [[x&y for (x,y) in zip(remIP,netAddr)]==netAddr for netAddr in self.networkAddr]
                if True in Wlan0AddrRangeCheck and txQ>0:
                    currTxQ += txQ
        with open("/proc/net/tcp") as tcpF:
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
                Wlan0AddrRangeCheck = [[x&y for (x,y) in zip(remIP,netAddr)]==netAddr for netAddr in self.networkAddr]
                if True in Wlan0AddrRangeCheck and txQ>0:
                    currTxQ += txQ
        return currTxQ
    def exponentialMovingAverage(self, dataSet, dictKeyWord, alfa):
        values = dataSet[dictKeyWord]
        mean = values[0]
        for i in values[1:]:
            mean = alfa*i+(1-alfa)*mean
        return (dictKeyWord+'EMA', mean)
    def deltaExponentialMovingAverage(self,dataSet, dictKeyWord, alfa):
        values = dataSet[dictKeyWord]
        mean = values[1] - values[0]
        prev_i = values[1]
        for i in values[2:]:
            mean = alfa*(i-prev_i)+(1-alfa)*mean
            prev_i = i
        return (dictKeyWord+'DEMA', mean)
    def arithmeticMean(self, dataSet, dictKeyWord):
        values = dataSet[dictKeyWord]
        valSum = 0.0
        for i in values:
            valSum += i
        mean = valSum/len(values)
        return (dictKeyWord+'AM', mean)
    def deltaArithmeticMean(self, dataSet, dictKeyWord):
        values = dataSet[dictKeyWord]
        valSum = 0.0
        prev_i = values[0]
        for i in values[1:]:
            valSum += i-prev_i
            prev_i = i
        mean = valSum/(len(values)-1)
        return (dictKeyWord+'DAM', mean)

#====================
#===== Here is the agent code ===============


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


try:
    agentStatistics = AgentStatistics(agent, "wlan0")
    #agentStatistics.addGatheringFunction(agentStatistics.gatherNumberOfConnections)
    #agentStatistics.addProcessFunction(agentStatistics.arithmeticMean,'gatherNumberOfConnections')
    agentStatistics.addGatheringFunction(agentStatistics.gatherLostPacketsCounter)
    agentStatistics.addProcessFunction(agentStatistics.deltaArithmeticMean,'gatherLostPacketsCounter')
    agentStatistics.start()
    #Start agent
    agent.run()

except KeyboardInterrupt:
    print("Agent exits")
finally:
    #Stop agent
    agent.stop()

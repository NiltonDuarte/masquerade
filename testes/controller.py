#!/root/wishful/dev/bin/python
# -*- coding: utf-8 -*-

import datetime
import logging
import wishful_controller
import gevent
import wishful_upis as upis
import platform
import netifaces as ni
import ast
import traceback
import math
from dcf_throughput import *

log = logging.getLogger('wishful_controller')
log_level = logging.DEBUG
logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s',
                    filename="/tmp/wishful_controller.log")

#Create controller
eth0_ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
dlport=8990
ulport=8989
dl="tcp://{0}:{1}".format(eth0_ip, dlport)
ul="tcp://{0}:{1}".format(eth0_ip, ulport)
controller = wishful_controller.Controller(dl=dl, ul=ul)

#Configure controller
groupName = "wishful_icarus"
name = "WishfulController-{0}".format(platform.node())
info = "Wishful Controller on {0} node. {1}".format(platform.node(), platform.uname())
controller.set_controller_info(name=name, info=info)
controller.add_module(moduleName="discovery", pyModuleName="wishful_module_discovery_pyre",
                      className="PyreDiscoveryControllerModule", 
                      kwargs={"iface":"eth0", "groupName":groupName, "downlink":dl, "uplink":ul})

nodes = []

class ContentionWindowPriority:
    def __init__(self):
        self.valueDict = {}
        self.dcfOpt = DCF_Optimizer()
        self.nodes = []
    def addNode(self, node):
        self.nodes.append(node)
        self.valueDict[node.id] = 1
    def delNode(self, node):
        self.nodes.remove(node)
    def updateValue(self, node, value):
        if value == 0:
            return
        self.valueDict[node.id] = value
    def getCW(self):
        rate = self.valueDict[nodes[0].id]/self.valueDict[nodes[1].id]
        self.dcfOpt.r= rate
        #Optimize A=rB
        self.dcfOpt.otim_rate()
        return [(self.nodes[0], self.dcfOpt.wa), (self.nodes[1], self.dcfOpt.wb)]

cwPrio=ContentionWindowPriority()





def AgentStatistics():
    pass

@controller.new_node_callback()
def new_node(node):
    nodes.append(node)
    cwPrio.addNode(node)
    print("New node appeared:")
    print(node)


@controller.node_exit_callback()
def node_exit(node, reason):
    if node in nodes:
        nodes.remove(node);
        cwPrio.delNode(node)
    print("NodeExit : NodeID : {} Reason : {}".format(node.id, reason))


@controller.set_default_callback()
def default_callback(group, node, cmd, data):
    print("{} DEFAULT CALLBACK : Group: {}, NodeName: {}, Cmd: {}, Returns: {}".format(datetime.datetime.now(), group, node.name, cmd, data))

def print_response(group, node, data):
    print("{} Print response : Group:{}, NodeIP:{}, Result:{}".format(datetime.datetime.now(), group, node.ip, data)) 


@controller.add_callback(upis.radio.set_parameter_lower_layer)
def get_channel_reponse(group, node, data):
    print("{} get_set_parameter_reponse : Group:{}, NodeId:{}, msg:{}".format(datetime.datetime.now(), group, node.id, data))

@controller.add_callback(AgentStatistics)
def statCallback(group, node, data):
    print("{} AgentStatisticsCallback : Group:{}, NodeName:{}, msg:{}".format(datetime.datetime.now(), group, node.name, data))
    dataDict = ast.literal_eval(data)
    selector = 2
    if (selector==1):
        dataVal = dataDict['gatherNumberOfConnectionsAM']
        cwPrio.updateValue(node, dataVal if dataVal > 0 else 0.01)
    if (selector==2):
        dataVal = dataDict['gatherLostPacketsCounterDAM']
        dataVal = dataVal + 1 #avoid 0 (domain error), adding one to both result will not change the results drastically
        cwPrio.updateValue(node, math.log(dataVal))

try:
    #Start controller
    controller.start()
    #control loop
    while True:
        print("\n")
        print("Connected nodes", [str(node.name) for node in nodes])
        if len(nodes)==2:
            nodeList = cwPrio.getCW()
            for (node, cw) in nodeList:
                cw = max(4,cw)
                cw = min(256,cw)
                controller.blocking(False).node(node).radio.iface("wlan0").set_parameter_lower_layer(interface='wlan0',
                    CSMA_CW_MIN=cw, CSMA_CW_MAX=cw*4)
            gevent.sleep(1)
        else:
            gevent.sleep(10)
except KeyboardInterrupt:
    print("Controller exits")
    traceback.print_exc()
finally:
    controller.stop()

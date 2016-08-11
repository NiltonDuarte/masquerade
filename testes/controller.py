#!/root/wishful/dev/bin/python
# -*- coding: utf-8 -*-

import datetime
import logging
import wishful_controller
import gevent
import wishful_upis as upis
import platform
import netifaces as ni

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

def AgentStatistics():
    pass

@controller.new_node_callback()
def new_node(node):
    nodes.append(node)
    print("New node appeared:")
    print(node)


@controller.node_exit_callback()
def node_exit(node, reason):
    if node in nodes:
        nodes.remove(node);
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
    print("{} statCallback : Group:{}, NodeId:{}, msg:{}".format(datetime.datetime.now(), group, node.id, data))



try:
    #Start controller
    controller.start()
    #control loop
    while True:
        print("\n")
        print("Connected nodes", [str(node.name) for node in nodes])
        if nodes:
            for node in nodes:
                highPrio = {'interface' : 'wlan0', "CSMA_CW" : 1, "CSMA_CW_MIN" : 1, "CSMA_CW_MAX" : 16}
                #result = wmpm.set_parameter_lower_layer(args)
                #controller.blocking(False).node(nodes[0]).radio.iface("wlan0").set_parameter_lower_layer(args)
                controller.blocking(False).node(node).radio.iface("wlan0").set_parameter_lower_layer(**highPrio)
                gevent.sleep(10)
                lowPrio = {'interface' : 'wlan0', "CSMA_CW" : 32, "CSMA_CW_MIN" : 32, "CSMA_CW_MAX" : 4095}
                controller.blocking(False).node(node).radio.iface("wlan0").set_parameter_lower_layer(**lowPrio)
        else:
            gevent.sleep(10)
except KeyboardInterrupt:
    print("Controller exits")
finally:
    controller.stop()
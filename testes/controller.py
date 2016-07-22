#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import logging
import wishful_controller
import gevent
import wishful_upis as upis

log = logging.getLogger('wishful_controller')
log_level = logging.DEBUG
logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s')

#Create controller
controller = wishful_controller.Controller(dl="tcp://10.129.11.2:8990", ul="tcp://10.129.11.2:8989")

#Configure controller
controller.set_controller_info(name="WishfulController", info="WishfulControllerInfo")
controller.add_module(moduleName="discovery", pyModuleName="wishful_module_discovery_pyre",
                      className="PyreDiscoveryControllerModule", 
                      kwargs={"iface":"eth0", "groupName":"wishful_1234", "downlink":"tcp://10.129.11.2:8990", "uplink":"tcp://10.129.11.2:8989"})

nodes = []

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




try:
    #Start controller
    controller.start()
    #control loop
    while True:
        print("\n")
        print("Connected nodes", [str(node.name) for node in nodes])
        if nodes:
            for node in nodes:
            hightPrio = {'interface' : 'wlan0', "CSMA_CW" : 1, "CSMA_CW_MIN" : 1, "CSMA_CW_MAX" : 16}
            #result = wmpm.set_parameter_lower_layer(args)
            #controller.blocking(False).node(nodes[0]).radio.iface("wlan0").set_parameter_lower_layer(args)
            controller.blocking(False).node(node).radio.iface("wlan0").set_parameter_lower_layer(**hightPrio)
            gevent.sleep(10)
            lowPrio = {'interface' : 'wlan0', "CSMA_CW" : 32, "CSMA_CW_MIN" : 32, "CSMA_CW_MAX" : 4095}
            controller.blocking(False).node(node).radio.iface("wlan0").set_parameter_lower_layer(**lowPrio)
        gevent.sleep(10)
except KeyboardInterrupt:
    print("Controller exits")
finally:
    controller.stop()
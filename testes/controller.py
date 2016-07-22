#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import logging
import wishful_controller
import gevent
import wishful_upis as upis

log = logging.getLogger('wishful_controller')
log_level = logging.INFO
logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s')

#Create controller
controller = wishful_controller.Controller(dl="tcp://127.0.0.1:8990", ul="tcp://127.0.0.1:8989")

#Configure controller
controller.set_controller_info(name="WishfulController", info="WishfulControllerInfo")
controller.add_module(moduleName="discovery", pyModuleName="wishful_module_discovery_pyre",
                      className="PyreDiscoveryControllerModule", 
                      kwargs={"iface":"lo", "groupName":"wishful_1234", "downlink":"tcp://127.0.0.1:8990", "uplink":"tcp://127.0.0.1:8989"})

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


@controller.add_callback(upis.radio.set_parameter_lower_layer)
def get_channel_reponse(group, node, data):
    print("{} get_set_parameter_reponse : Group:{}, NodeId:{}, msg:{}".format(datetime.datetime.now(), group, node.id, data))


def print_response(group, node, data):
    print("{} Print response : Group:{}, NodeIP:{}, Result:{}".format(datetime.datetime.now(), group, node.ip, data)) 


try:
    #Start controller
    controller.start()

    #control loop
    while True:
        print("\n")
        print("Connected nodes", [str(node.name) for node in nodes])
        if nodes:
            args = {'interface' : 'wlan0', "CSMA_CW" : 15, "CSMA_CW_MIN" : 15, "CSMA_CW_MAX" : 15}
            #result = wmpm.set_parameter_lower_layer(args)
            controller.blocking(False).node(nodes[0]).radio.iface("wlan0").set_parameter_lower_layer(args)

        gevent.sleep(10)

except KeyboardInterrupt:
    print("Controller exits")
finally:
    controller.stop()
#!/root/wishful/dev/bin/python
# -*- coding: utf-8 -*-

import logging
import wishful_agent
import yaml
import platform

log = logging.getLogger('wishful_agent')
logLevel = logging.DEBUG
logging.basicConfig(level=logLevel, format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s',
					filename="/tmp/wishful_agent.log")

#Create and configure
agent = wishful_agent.Agent()

name = "WishfulAgent-{0}".format(plataform.node()) #Returns the computer’s network name
info = "Wishful Agent on {0} node. {1}".format(plataform.node(), platform.uname())
groupName = "wishful_icarus"
agent.set_agent_info(name=name, info=info, iface="eth0")

agent.add_module(moduleName="discovery", pyModule="wishful_module_discovery_pyre", 
                 className="PyreDiscoveryAgentModule", kwargs={"iface":"eth0", "groupName":groupName})

agent.add_module(moduleName="wmp", pyModule="wishful_module_wifi_wmp", 
                 className="WmpModule", interfaces=['wlan0'])

try:
    #Start agent
    agent.run()
except KeyboardInterrupt:
    print("Agent exits")
finally:
    #Stop agent
    agent.stop()
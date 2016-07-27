#!/root/wishful/dev/bin/python
# -*- coding: utf-8 -*-

import logging
import wishful_agent

log = logging.getLogger('wishful_agent')
logLevel = logging.DEBUG
logging.basicConfig(level=logLevel, format='%(asctime)s - %(name)s.%(funcName)s() - %(levelname)s - %(message)s')

#Create and configure
agent = wishful_agent.Agent()

agent.set_agent_info(name="BasicAgent", info="BasicAgentInfo", iface="eth0")


agent.add_module(moduleName="discovery", pyModule="wishful_module_discovery_pyre", 
                 className="PyreDiscoveryAgentModule", kwargs={"iface":"eth0", "groupName":"wishful_1234"})

agent.add_module(moduleName="wmp", pyModule="wishful_module_wifi_wmp", 
                 className="WmpModule", interfaces=['wlan0'])

agent.add_module(moduleName="iperf", pyModule="wishful_module_iperf", 
                 className="IperfModule")

try:
    #Start agent
    agent.run()
except KeyboardInterrupt:
    print("Agent exits")
finally:
    #Stop agent
    agent.stop()
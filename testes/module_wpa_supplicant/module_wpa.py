import logging
import wishful_upis as upis
import wishful_framework as wishful_module
import subprocess
from wishful_framework.classes import exceptions
import netifaces as ni
import inspect
from pyroute2 import IPRoute

@wishful_module.build_module
class WPAModule(wishful_module.AgentModule):
    def __init__(self):
        super(WPAModule, self).__init__()
        self.log = logging.getLogger('wpa_module.main')

    @wishful_module.bind_function(upis.net.set_parameter_higher_layer)
    def set_parameter_higher_layer(self, **kwargs):
        """
        Set the parameter on higher layers of protocol stack (higher MAC and above)
        Args:
            param_key_value: key and value of this parameter
            iface : interface name (required) e.g. "wlan0" (str)
            ip_addres : interface ip adress e.g. "10.0.0.1" (str)
            netmask : interface network mask e.g. 24 (int)
        """
        if "iface" in kwargs:
            iface = kwargs["iface"]
        else:
            return False
        ipr = IPRoute()
        idx = ip.link_lookup(ifname=iface)[0]

        netmask=None
        if "netmask" in kwargs:
            netmask=kwargs["netmask"]

        if "ip_address" in kwargs:
            ip_address=kwargs["ip_address"]
            ipr.addr('add', index=idx, address=ip_address, netmask=netmask)
        return True


    @wishful_module.bind_function(upis.wifi.net.connect_to_network)
    def connect_to_network(self, iface, **kwargs):
        '''Connects a given interface to some network
        e.g. WiFi network identified by SSID.
        '''

        self.pidFile = '/tmp/wpa.pid'
        self.configFile = '/tmp/wpa.conf'

        content = self.defineContent(**kwargs)
        self.createFile(self.configFile, content)

        cmd_str = "wpa_supplicant -B -P {0} -i{1} -c{2}".format(self.pidFile, iface,self.configFile)

        try:
            # attempt to stop any active wpa_supplicant instances
            # ideally we do this just for the interface we care about
            [rcode, sout, serr] = self.run_command('killall wpa_supplicant')
            #connect
            [rcode, sout, serr] = self.run_command(cmd_str)
        except Exception as e:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("An error occurred in %s: %s" % (fname, e))
            raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))
        return True


    def defineContent(self, **kwargs):
        wpaModel = (
            "network={{\n" +
            "    ssid=\"{ssid}\"\n" +
            "    scan_ssid=1\n" +
            "    key_mgmt=NONE\n" +
            "}}"
        )
        content = wpaModel.format(**kwargs)
        return content

    def createFile(self, filePath, fileContent):
        try:
            with open(filePath, 'w') as f:
                f.write(fileContent)
        except Exception as e:
            fname = inspect.currentframe().f_code.co_name
            self.log.fatal("An error occurred in %s: %s" % (fname, e))
            raise exceptions.UPIFunctionExecutionFailedException(func_name=fname, err_msg=str(e))

    def run_command(self, command):
        '''
            Method to start the shell commands and get the output as iterater object
        '''

        sp = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = sp.communicate()

        #if False:
        if out:
            self.log.debug("standard output of subprocess:")
            self.log.debug(out)
        if err:
            self.log.debug("standard error of subprocess:")
            self.log.debug(err)

        if err:
            raise Exception("An error occurred in WPA Module: %s" % err)

        return [sp.returncode, out.decode("utf-8"), err.decode("utf-8")]
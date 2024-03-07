#!/usr/bin/python

#  Copyright 2019-present Open Networking Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import argparse

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import Host
from mininet.topo import Topo
from stratum import StratumBmv2Switch

CPU_PORT = 255


class IPv4Host(Host):
    """Host that can be configured with an IPv4 gateway (default route).
    """

    def config(self, mac=None, ip=None, defaultRoute=None, lo='up', gw=None,
               gwMac=None, **_params):
        super(IPv4Host, self).config(mac, ip, defaultRoute, lo, **_params)
        self.cmd('ip -4 addr flush dev %s' % self.defaultIntf())
        self.cmd('ip -6 addr flush dev %s' % self.defaultIntf())
        self.cmd('ip -4 link set up %s' % self.defaultIntf())
        self.cmd('ip -4 addr add %s dev %s' % (ip, self.defaultIntf()))
        if gw:
            self.cmd('ip -4 route add default via %s' % gw)
            if gwMac:
                self.cmd("arp -s %s %s" %(gw, gwMac))
        # Disable offload
        # for attr in ["rx", "tx", "sg"]:
        #     cmd = "/sbin/ethtool --offload %s %s off" % (
        #         self.defaultIntf(), attr)
        #     self.cmd(cmd)

        def updateIP():
            return ip.split('/')[0]

        self.defaultIntf().updateIP = updateIP


class TutorialTopo(Topo):
    """2x2 fabric topology with IPv4 hosts"""

    def __init__(self, *args, **kwargs):
        Topo.__init__(self, *args, **kwargs)

        # Leaves
        # gRPC port 50001
        s1 = self.addSwitch('s1', cls=StratumBmv2Switch, cpuport=CPU_PORT)
        s2 = self.addSwitch('s2', cls=StratumBmv2Switch, cpuport=CPU_PORT)
        s3 = self.addSwitch('s3', cls=StratumBmv2Switch, cpuport=CPU_PORT)
        s4 = self.addSwitch('s4', cls=StratumBmv2Switch, cpuport=CPU_PORT)

        # s1 = self.addSwitch('s1', cpuport=CPU_PORT)
        # s2 = self.addSwitch('s2', cpuport=CPU_PORT)
        # s3 = self.addSwitch('s3', cpuport=CPU_PORT)
        # s4 = self.addSwitch('s4', cpuport=CPU_PORT)


        # IPv4 hosts attached to leaf 1
        h1 = self.addHost('h1', cls=IPv4Host, mac="08:00:00:00:01:11",
                           ip='10.0.1.1/24', gw='10.0.1.10', gwMac="08:00:00:00:01:00" )
        h2 = self.addHost('h2', cls=IPv4Host, mac="08:00:00:00:02:22",
                           ip='10.0.2.2/24', gw='10.0.2.20', gwMac="08:00:00:00:02:00" )
        h3 = self.addHost('h3', cls=IPv4Host, mac="08:00:00:00:03:33",
                           ip='10.0.3.3/24', gw='10.0.3.30', gwMac="08:00:00:00:03:00" )
        h4 = self.addHost('h4', cls=IPv4Host, mac="08:00:00:00:04:44",
                           ip='10.0.4.4/24', gw='10.0.4.40', gwMac="08:00:00:00:04:00")


        self.addLink(h1, s1, port2=1)  # s1 - port 1
        self.addLink(h2, s1, port2=2)  # s1 - port 2
        self.addLink(h3, s2, port2=1)  # s2 - port 1
        self.addLink(h4, s2, port2=2)  # s2 - port 2
        self.addLink(s1, s3, port1=3, port2=1)
        self.addLink(s1, s4, port1=4, port2=2)
        self.addLink(s2, s3, port1=4, port2=2)
        self.addLink(s2, s4, port1=3, port2=1)

def main():
    net = Mininet(topo=TutorialTopo(), controller=None)
    net.start()
    CLI(net)
    net.stop()
    print('#' * 80)
    print('ATTENTION: Mininet was stopped! Perhaps accidentally?')
    print('No worries, it will restart automatically in a few seconds...')
    print('To access again the Mininet CLI, use `make mn-cli`')
    print('To detach from the CLI (without stopping), press Ctrl-D')
    print('To permanently quit Mininet, use `make stop`')
    print('#' * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Mininet topology script for 2x2 fabric with stratum_bmv2 and IPv4 hosts')
    args = parser.parse_args()
    setLogLevel('info')

    main()

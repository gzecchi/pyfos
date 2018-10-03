#!/usr/bin/env python3

# Copyright 2018 Brocade Communications Systems LLC.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may also obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""

:mod:`extension_circuit_statistics_pktloss_show` - PyFOS util to show  pktloss
********************************************************************************
The :mod:`extension_circuit_statistics_pktloss_show` Util for circuit pktloss

This module is a standalone script that can be used to show extension \
circuit statistics for packet loss and percentage packetloss.

extension_circuit_statistics_pktloss_show.py : Usage

* Infrastructure options:
    * -i,--ipaddr=IPADDR:IP address of FOS switch.
    * -L,--login=LOGIN:login name.
    * -P,--password=PASSWORD:password.
    * -f,--vfid=VFID:VFID to which the request is directed to.
    * -s,--secured=MODE:HTTPS mode "self" or "CA"[OPTIONAL].
    * -v,--verbose:verbose mode[OPTIONAL].

* Util scripts options:
    * -n,--name=NAME : set "name" or slot/port of the circuit
    * -c,--circuit-id=CIRCUIT-ID : set "circuit-id" of the circuit

* outputs:
    * Json format details for circuit level percentage packet loss with \
    corresponding GE statistics

.. function:: extension_circuit_statistics_show.\
show_pktloss(session,name, cid, local, remote)

    *show extension circuit statistics for pktloss*

        Example usage of the method::

                ret = extension_circuit_statistics_show.
                show_pktloss(session,
                name, cid)
                print (ret)

        * inputs:
            :param session: session returned by login
            :param name: VE port name expressed as slot/port.
            :param cid: circuit ID.

        * outputs:
            :rtype: list of circuit stats with pecentage packet loss

        *use cases*

        1. show percentage packet loss per circuit

"""


import pyfos.pyfos_auth as pyfos_auth
import pyfos.pyfos_util as pyfos_util
from pyfos.pyfos_brocade_extension_tunnel import extension_circuit_statistics
from pyfos.pyfos_brocade_extension_tunnel import extension_circuit
from pyfos.pyfos_brocade_extension_ip_interface import extension_ip_interface
from pyfos.pyfos_brocade_gigabitethernet import \
     gigabitethernet_statistics

import sys
import pyfos.utils.brcd_util as brcd_util
import json


def getgedetails(gelist, name):
    obj = None
    if isinstance(gelist, gigabitethernet_statistics):
        if gelist.peek_name() == name:
            obj = json.loads(gelist.__repr__())
    elif isinstance(gelist, list):
        for i in range(len(gelist)):
            if gelist[i].peek_name() == name:
                obj = json.loads(gelist[i].__repr__())
    else:
        return None
    return obj


def getipdetails(iplist, gelist, ip):
    obj = None
    if isinstance(iplist, extension_circuit):
        if iplist.peek_name == ip:
            obj = json.loads(iplist.__repr__())
            obj['extension-ip-interface']['GE-details'] = getgedetails(
                gelist, iplist.peek_name())
    elif isinstance(iplist, list):
        for i in range(len(iplist)):
            if iplist[i].peek_ip_address() == ip:
                obj = json.loads(iplist[i].__repr__())
                obj['extension-ip-interface']['GE-details'] = getgedetails(
                    gelist, iplist[i].peek_name())
    else:
        return None
    return obj


def getcircuitdetails(circuitlist, iplist, gelist, name, cid):
    obj = None
    if isinstance(circuitlist, extension_circuit):
        if circuitlist.peek_name == name and \
           circuitlist.peek_circuit_id() == cid:
            obj = json.loads(circuitlist.__repr__())
            obj['extension-circuit']['ip-details'] = getipdetails(
                iplist, gelist, circuitlist.peek_local_ip_address())
    elif isinstance(circuitlist, list):
        for i in range(len(circuitlist)):
            if circuitlist[i].peek_name() == name and \
               circuitlist[i].peek_circuit_id() == cid:
                obj = json.loads(circuitlist[i].__repr__())
                obj['extension-circuit']['local-ip-details'] = getipdetails(
                    iplist, gelist, circuitlist[i].peek_local_ip_address())
                obj['extension-circuit']['local-ha-ip-details'] = getipdetails(
                    iplist, gelist, circuitlist[i].peek_local_ha_ip_address())
    else:
        return None
    return obj


def _show_pktloss(session, cirobject):
    getfilters = ["name", "circuit_id", "out_packet_lost", "out_packet_total"]
    statslist = extension_circuit_statistics.get(session)
    getfilters = ["name", "circuit_id", "out_packet_lost", "out_packet_total",
                  "local_ip_address", "local_ha_ip_address"]
    circuitlist = extension_circuit.get(session, None, getfilters)
    iplist = extension_ip_interface.get(session, None, ["name", "ip_address"])
    gestatslist = gigabitethernet_statistics.get(session)
    percentagelist = []
    if isinstance(statslist, extension_circuit_statistics):
        statslist = [statslist]
    if isinstance(circuitlist, extension_circuit):
        circuitlist = [circuitlist]
    if isinstance(iplist, extension_ip_interface):
        iplist = [iplist]
    if isinstance(gestatslist, gigabitethernet_statistics):
        gestatslist = [gestatslist]
    if isinstance(statslist, list):
        for i in range(len(statslist)):
            if cirobject.peek_name() is not None and \
               cirobject.peek_name() != statslist[i].peek_name():
                continue
            if cirobject.peek_circuit_id() is not None and\
               cirobject.peek_circuit_id() != statslist[i].peek_circuit_id():
                continue
            obj = json.loads(statslist[i].__repr__())

            percentage = 0
            lost = statslist[i].peek_out_packet_lost()
            total = statslist[i].peek_out_packet_total()
            k1 = 'extension-circuit-statistics'
            k2 = 'percentage-pktloss'
            if lost != 0 and total != 0:
                percentage = (float(lost) * 100 / float(total))
                obj[k1][k2] = percentage
            else:
                obj[k1][k2] = 0
            val = getcircuitdetails(circuitlist, iplist, gestatslist,
                                    statslist[i].peek_name(),
                                    statslist[i].peek_circuit_id())
            obj[k1]['circuit-details'] = val
            percentagelist.append(obj)

    else:
        print(statslist)
    return percentagelist


def show_pktloss(session, name, cid=None):
    value_dict = {'name': name, 'circuit-id': cid}
    cirobject = extension_circuit_statistics(value_dict)
    result = _show_pktloss(session, cirobject)
    return result


def main(argv):
    # myinput = "-v -i 10.17.3.70 -L admin -P password --name=7/35"
    # argv = myinput.split()
    filters = ["name", "circuit_id"]
    inputs = brcd_util.parse(argv, extension_circuit_statistics, filters)
    circobject = inputs['utilobject']
    session = brcd_util.getsession(inputs)
    result = _show_pktloss(session, circobject)
    if len(result) == 0:
        print("No Circuit stats found.")
    else:
        pyfos_util.response_print(result)
    pyfos_auth.logout(session)


if __name__ == "__main__":
    main(sys.argv[1:])
from asyncio.subprocess import DEVNULL
from multiprocessing import connection
import re
import os
from netmiko import ConnectHandler
import logging
from incidentrepo import IncidentRepository
logging.basicConfig(filename='network_device.log', level=logging.ERROR, format='%(asctime)s %(message)s')
import commandparser

class Network_device(object):
    """Class to represent network switches and routers"""
    def __init__(self, repository, credential_params, secret, device_os):
        self.username = credential_params['username']
        self.password = credential_params['password']
        self.secret = secret
        self.repository = repository
        self.incident = repository.get_incident({"number": credential_params['number']})
        self.ip = self.incident.ip_address
        self.neighbor_ip = self.incident.neighbor_ip
        self.interface = self.incident.interface
        self.device_os = device_os
        self.is_alive = False
        self.good_ssh_connection = False
        self.connection = None
        self.is_alive = self.ping_device()
        self.createconnection()
   
    def ping_device(self):
        """
        Returns True if host responds to a ping request
        """ 
        import subprocess, platform
        try:
            x =  subprocess.call(f"ping -c 1 {self.ip}", shell=True, stdout=DEVNULL) == 0  
            return x 
        except:
            return False

    def createconnection(self):
        """Creates a new SSH / Netmiko connection to the network device
        at ip using username and password to login. Returns the new connection object."""
        connection_dict = {
                "ip": self.ip,
                "username": self.username,
                "password": self.password,
                "secret": self.secret,
                "device_type": self.device_os,
                "global_delay_factor": 5,
                "banner_timeout" : 20,
                "auth_timeout" : 60 
            }
        try:
            self.connection = ConnectHandler(**connection_dict)
            self.good_ssh_connection = True
            # self.connection.enable()
        except:
            self.connection = None
            self.good_ssh_connection = False

    def sendcommand(self, x_command_string:str, x_expect_string = '#', x_strip_prompt = False, x_strip_command = True):
        """Formats and sends a Netmiko 'send_command()' using the connection and command passed in. The return
        is the output from the device after executing the command. Command is passed as x_command. If the expected 
        response is something other than the standard prompt then you can specify a unique string in the argument x_expect_string. x_strip_prompt controls if
        the device prompts are included in what is returned. """
        try:
            output = self.connection.send_command(
            command_string = x_command_string,
            # expect_string = x_expect_string,
            # strip_prompt = x_strip_prompt,
            # strip_command = x_strip_command
            )
            return output
        except:
            return False

    def get_env_details(self):
        pass

    def get_inventory(self):
        pass

    def power_failure_details(self):
        pass

    def get_eigrp_log(self, neighbor_ip):
        pass

    def get_eigrp_neighbors(self):
        pass

    def get_interface_detail(self, interface): 
        pass

    def get_interface_detail_with_neighbor_ip(self, neighbor_ip): 
        pass 

    def get_bgp_summary(self, neighbor_ip):
        pass
    
    def get_bgp_neighbor(self, neighbor_ip):
        pass
    
    def get_interface_connection(self, neighbor_ip):
        pass

    def get_ospf_neighbor(self):
        pass

    def head(self, text, n):
        output = text.split('\n')
        first = output[:n]
        my_str = '\n'.join(first)
        return my_str

    def tail(self,text, n):
        output = text.split('\n')
        last = output[-n:]
        my_str = '\n'.join(last)
        return my_str

    def percentage(self, frac_str):
        num, denom = frac_str.split('/')
        frac = (float(num) / float(denom))*100
        if frac < 1:
            frac = 1
        else:
            frac = int(round(frac,0))
        return str(frac) + "%"

    def put_incident(self, params):
        self.repository.put_incident(params=params)
        
class IOS_device(Network_device):

    def __init__(self, repository, credential_params, secret=''):
        super().__init__(repository, credential_params, secret, 'cisco_ios')

    def get_env_details(self):
        try:
            output = self.sendcommand('show environment all')
            check_if_invalid = re.findall(r'% Invalid', output)
            if len(check_if_invalid):
                output = self.sendcommand('show environment')
                return output
            else:
                pass
            return output
        except Exception as e:
            return 'Error'
            
    def get_inventory(self):
        try:
            output = self.sendcommand('show inventory')
            return output
        except BaseException as e:
            logging.exception(f'IOS_device - get_inventory failed for device {self.ip} Error: {e}')

    def power_failure_details(self) -> dict:
        try:
            environment_details = self.get_env_details()
            bad_power = re.findall(r'.*Bad.*|.*No Input Power.*|.*Not Present.*', environment_details)
            if len(bad_power):
                    for item in bad_power:
                        print(item)
                        check_for_serial = re.search(r'(?=.*[A-Z])(?=.*[0-9])[A-Z0-9]{11}', item)
                        if check_for_serial != None:
                            print('SERIAL IS AVAILABLE')
                            print("Full match: % s" % (check_for_serial.group(0)))
                            return {"environment_details" : environment_details}
                        else:
                            inventory_details = self.get_inventory()
                            print('NO AVAILABLE SERIAL')
                            print(environment_details)
                            print(inventory_details)
                            return {"inventory_details" : inventory_details, "environment_details" : environment_details}
            else:
                return {"environment_details" : environment_details} 
        except Exception as e:
            return 'Error'

    def get_eigrp_log(self):
        try:
            command = 'show log | inc EIGRP'
            output = self.sendcommand(command)
            output = self.tail(output, 10)
            return output
        except Exception as e:
            return 'Error'

    def get_eigrp_neighbors(self):
        try:
            output = self.sendcommand('show ip eigrp neighbors')
            return output
        except Exception as e:
            return 'Error'
            
    def get_interface_detail(self, interface): 
        try:
            command = 'show interface ' + interface
            output = self.sendcommand(command)
            return output
        except Exception as e:
            return 'Error'

    def get_interface_detail_from_eigrp_log(self):
        try:
            output = self.get_eigrp_log()
            output = self.tail(output, 2)
            interface = commandparser.CommandParser(r'Neighbor.*|on interface.*', output).get_interface()
            output = self.get_interface_detail(interface)
            output = self.head(output, 6)
            return output
        except Exception as e:
            return 'Error'
    
    def get_interface_detail_txrx(self, interface) -> dict:
        try:
            interface_detail = self.get_interface_detail(interface)
            txload = commandparser.CommandParser(r'reliability\s.*', interface_detail).get_txload()
            txload = self.percentage(txload)
            rxload = commandparser.CommandParser(r'reliability\s.*', interface_detail).get_rxload()
            rxload = self.percentage(rxload)
            interface_detail = self.head(interface_detail, 8)
            return {'txload': txload, 'rxload': rxload, 'interface' : interface_detail}
        except Exception as e:
            return 'Error'

    def get_bgp_summary(self, neighbor_ip):
        try:
            command = 'show ip bgp summary | include ' + neighbor_ip
            output = self.sendcommand(command)
            return output
        except Exception as e:
            return 'Error'

    def get_bgp_neighbor(self, neighbor_ip):
        try:
            command = 'show ip bgp neighbor ' + neighbor_ip
            output = self.sendcommand(command)
            return output
        except Exception as e:
            return 'Error'
    
    def get_bgp_connection(self, neighbor_ip):
        try:
            bgp_neighbor = self.get_bgp_neighbor(neighbor_ip)
            local_host = commandparser.CommandParser(r'Local\shost:.*', bgp_neighbor).get_local_host()
            command = 'sh ip int br | inc ' + local_host
            output = self.sendcommand(command)
            return output
        except Exception as e:
            return 'Error'    

    def get_interface_description(self, neighbor_ip):
        try:
            bgp_connection = self.get_bgp_connection(neighbor_ip)
            interface = commandparser.CommandParser(r'.*', bgp_connection).get_first_index()
            command = 'show int ' + interface
            interface_description = self.sendcommand(command)
            return interface_description
        except Exception as e:
            return 'Error'

    def get_ospf_neighbor(self):
        try:
            output = self.sendcommand('show ip ospf neighbor')
            return output
        except Exception as e:
            return 'Error'

    def get_ospf_log(self, neighbor_ip):
        try:
            command = 'show logging | inc ' + neighbor_ip
            output = self.sendcommand(command)
            output = self.tail(output, 10)
            return output
        except Exception as e:
            return 'Error' 

    def get_ospf_interface(self, neighbor_ip):
        try:
            ospf_log = self.get_ospf_log(neighbor_ip)
            ospf_log = re.findall(r'on interface.*', ospf_log)[-1]
            interface = commandparser.CommandParser(r'on interface.*', ospf_log).get_interface()
            command = 'show interface ' + interface
            output = self.sendcommand(command)
            return output
        except Exception as e:
            return 'Error'

class JUNOS_device(Network_device):
    already_got_running_config = False
    already_got_version = False
    running_config = ''
    startup_config = ''
    version_config = '' 

    def __init__(self, repository, credential_params, secret=''):
        super().__init__(repository, credential_params, secret, 'juniper_junos')

    def get_env_details(self):
        try:
            output = self.sendcommand('show chassis environment')
            return output
        except BaseException as e:
            return 'Error' 

    def get_inventory(self):
        try:
            output = self.sendcommand('show chassis hardware')
            return output
        except BaseException as e:
            return 'Error'  

    def power_failure_details(self) -> dict:
        try:
            environment_details = self.get_env_details()
            bad_power = re.findall(r'.*Bad.*', environment_details)
            if len(bad_power):
                inventory_details = self.get_inventory()
                return {"inventory_details" : inventory_details, "environment_details" : environment_details}
            else:
                pass
            return {"environment_details" : environment_details} 
        except Exception as e:
            return 'Error'

    def get_eigrp_log(self, neighbor_ip):
        pass

    def get_eigrp_neighbors(self):
        pass

    def get_interface_detail(self, neighbor_ip): 
        pass

    def get_interface_detail_with_neighbor_ip(self, neighbor_ip):
        pass
   
    def get_bgp_summary(self, neighbor_ip):
        try:
            command = 'show bgp summary | match ' + neighbor_ip
            output = self.sendcommand(command)
            output = self.head(output, 1)
            return output
        except Exception as e:
            return 'Error'

    def get_bgp_neighbor(self, neighbor_ip):
        try:
            command = 'show bgp neighbor ' + neighbor_ip
            output = self.sendcommand(command)
            output = self.head(output, 20)
            return output
        except Exception as e:
            return 'Error'

    def get_bgp_connection(self, neighbor_ip):
        try:
            bgp_neighbor = self.get_bgp_neighbor(neighbor_ip)
            local_ip = commandparser.CommandParser(r'Local:\s\d+.\d+.\d+.\d+', bgp_neighbor).get_local_ip()
            command = 'show interfaces terse | match ' + local_ip
            output = self.sendcommand(command)
            output = self.head(output, 1)
            return output
        except Exception as e:
            return 'Error'   

    def get_interface_description(self, neighbor_ip) -> dict:
        try: 
            interface_connection = self.get_bgp_connection(neighbor_ip)
            interface = commandparser.CommandParser(r'.*', interface_connection).get_first_index()
            command = 'show configuration interfaces ' + interface + ' | display set'
            interface_description = self.sendcommand(command)
            command2 = 'show interfaces ' + interface
            validate_interface = self.sendcommand(command2)
            return {"interface_description" : interface_description, "validate_interface" : validate_interface}
        except Exception as e:
            return 'Error'
        
    def get_ospf_neighbor(self):
        pass

    def get_ospf_log(self, neighbor_ip):
        pass

    def get_ospf_interface(self, neighbor_ip):
	    pass

if __name__ == "__main__":
    print('This should only print during testing of this class ***********************************************************************')

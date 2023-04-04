from triage import NetworkTriage

class OSPFTriage(NetworkTriage):
    def __init__(self, networkDevice):
        super().__init__(networkDevice)

    def operate(self) -> dict:
        ospf_neighbor = self.networkDevice.get_ospf_neighbor()
        ospf_log = self.networkDevice.get_ospf_log(self.networkDevice.neighbor_ip)
        interface_detail = self.networkDevice.get_ospf_interface(self.networkDevice.neighbor_ip)
        if self.networkDevice.good_ssh_connection:
            result = {
                'IP address' : self.networkDevice.ip,
                'Is Alive' : self.networkDevice.is_alive,
                'Good SSH Connection' : self.networkDevice.good_ssh_connection,
                '#show ip ospf neighbor' : '\n' + ospf_neighbor,
                '#show logging | inc <neighbor_ip>': '\n' + ospf_log,
                '#show interface' : '\n' + interface_detail 
            }
        else:
            result = {
                'IP address' : self.networkDevice.ip,
                'Is Alive' : False,
                'Good SSH Connection' : False,
                'Log': None,
                'Result': None
            }
    
        singularString = ""
        for key, result in result.items():
             singularString = singularString + (key + " : " + str(result)) + "\n\n"
        print('Adding work notes for OSPF Down Alert')
        self.networkDevice.put_incident(singularString)
        return result
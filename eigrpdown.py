from triage import NetworkTriage

class EIGRPTriage(NetworkTriage):
    def __init__(self, networkDevice):
        super().__init__(networkDevice)

    def operate(self) -> dict:
        eigrp_log = self.networkDevice.get_eigrp_log()
        eigrp_neighbor = self.networkDevice.get_eigrp_neighbors()
        interface_detail = self.networkDevice.get_interface_detail_from_eigrp_log()
        if self.networkDevice.good_ssh_connection:
            result = {
                'IP address' : self.networkDevice.ip,
                'Is Alive' : self.networkDevice.is_alive,
                'Good SSH Connection' : self.networkDevice.good_ssh_connection,
                '#show log | inc EIGRP': '\n' + eigrp_log,
                '#show ip eigrp neighbor' : '\n' + eigrp_neighbor,
                '#show interface <interface>' : '\n' + interface_detail 
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
        print('Adding work notes for EIGRP Down Alert')
        self.networkDevice.put_incident(singularString)
        return result
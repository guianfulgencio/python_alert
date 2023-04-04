from triage import NetworkTriage

class InterfaceUtilizationTriage(NetworkTriage):
    def __init__(self, networkDevice):
        super().__init__(networkDevice)

    def operate(self) -> dict:
        txrx = self.networkDevice.get_interface_detail_txrx(self.networkDevice.interface)
        if self.networkDevice.good_ssh_connection:
            result = {
                'IP address' : self.networkDevice.ip,
                'Is Alive' : self.networkDevice.is_alive,
                'Good SSH Connection' : self.networkDevice.good_ssh_connection,
                '\n#show interface' : '\n' + txrx['interface'] + '\n',
                'Txload' : txrx['txload'], 
                'Rxload' : txrx['rxload']
            }
        else:
            result = {
                'IP address' : self.networkDevice.ip,
                'Is Alive' : False,
                'Good SSH Connection' : False,
                'Interface details': None
            }
            
        singularString = ""
        for key, result in result.items():
             singularString = singularString + (key + " : " + str(result)) + "\n"
        print('Adding work notes for Interfaceutil Alert')
        self.networkDevice.put_incident(singularString)
        return result
import incidentrepo
from powersupplyfailure import PowerSupplyTriage
from eigrpdown import EIGRPTriage
from ospfdown import OSPFTriage
from interfaceoututilization import InterfaceUtilizationTriage
from bgpdown import BGPTriage
from device_factory import Device_Factory
import sys, re
from triage import NetworkTriage

ssh_username = str(sys.argv[1])
ssh_password = str(sys.argv[2])
snow_username = str(sys.argv[3])
snow_password = str(sys.argv[4])
number = str(sys.argv[5])
build_number = str(sys.argv[6])
print(number)
url = 'https://chevron.service-now.com'


def Main():
    credential_params = {
        'username': ssh_username,
        'password': ssh_password,
        'number' : number 
    }
    repository = incidentrepo.IncidentRepository(baseurl=url, user_name=snow_username, password=snow_password)
    vendor = repository.get_incident({'number': credential_params['number']}).device_vendor
    print(vendor)
    incident_description = repository.get_incident({'number': credential_params['number']}).incident_description
    networkDevice = Device_Factory.get_device(vendor, repository=repository, credential_params=credential_params)
    if "Power Supply Failure" in incident_description:
        powersupply = PowerSupplyTriage(networkDevice=networkDevice)
        result = powersupply.operate()       
        check_errors = re.findall(r'% Invalid|error|Error', str(result))
        if len(check_errors):
            subject = (f'Error - Power Supply Failure - Build number: {build_number} - Incident: {number}')
            body = (f'{vendor}\nBuild number: {build_number}\nIncident number: {number}\n{result}')
            send = NetworkTriage.send_email(subject, body)
        else:
            pass
        print(result)
    
    elif "EIGRP Down" in incident_description:
        eigrp = EIGRPTriage(networkDevice=networkDevice)
        result = eigrp.operate()
        check_errors = re.findall(r'% Invalid|error|Error', str(result))
        if len(check_errors):
            subject = (f'Error - EIGRP Down - Build number: {build_number} - Incident: {number}')
            body = (f'{vendor}\nBuild number: {build_number}\nIncident number: {number}')
            send = NetworkTriage.send_email(subject, body)
        else:
            pass
        print(result)
    elif "BGP Down - Polling" in incident_description:
        bgpdown = BGPTriage(networkDevice=networkDevice)
        result = bgpdown.operate()
        check_errors = re.findall(r'% Invalid|error|Error', str(result))
        if len(check_errors):
            subject = (f'Error - BGP Down - Build number: {build_number} - Incident: {number}')
            body = (f'{vendor}\nBuild number: {build_number}\nIncident number: {number}')
            send = NetworkTriage.send_email(subject, body)
        else:
            pass
        print(result)  
    elif "OSPF Down" in incident_description:
        ospfdown = OSPFTriage(networkDevice=networkDevice)
        result = ospfdown.operate()
        check_errors = re.findall(r'% Invalid|error|Error', str(result))
        if len(check_errors):
            subject = (f'Error - OSPF Down - Build number: {build_number} - Incident: {number}')
            body = (f'{vendor}\nBuild number: {build_number}\nIncident number: {number}')
            send = NetworkTriage.send_email(subject, body)
        else:
            pass  
        print(result)
    elif "Perf-Interface-In-Util" or "Perf-Campus" in  incident_description: 
        interfaceutilization = InterfaceUtilizationTriage(networkDevice=networkDevice)
        result = interfaceutilization.operate()
        check_errors = re.findall(r'% Invalid|error|Error', str(result))
        if len(check_errors):
            subject = (f'Error - Interface Utilization - Build number: {build_number} - Incident: {number}')
            body = (f'{vendor}\nBuild number: {build_number}\nIncident number: {number}')
            send = NetworkTriage.send_email(subject, body)
        else:
            pass
        print(result)


if __name__ == "__main__":
    Main()

from env_lab import dnac
import json
import requests
import urllib3
from requests.auth import HTTPBasicAuth
from prettytable import PrettyTable
import time
import re
import pprint

# define a pretty-printer for diagnostics
pp = pprint.PrettyPrinter(indent=4)

# Used to mock-up functionality for development and testing
# use_mock = True -> use the mock
# use_mock = False -> run the real code
use_mock = False

# Example of pretty printing a table
dnac_devices = PrettyTable(['Hostname', 'Platform Id', 'Software Type', 'Software Version', 'Up Time'])
dnac_devices.padding_width = 1

# Silence the insecure warning due to SSL Certificate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Standard HTTP headers we need for our requests
headers = {
              'content-type': "application/json",
              'x-auth-token': "",
              '__runsync': "True",
              '__timeout': "30"
          }


def check_response_code(response, code):
    if response.status_code != code:
        # response not OK
        print('Did not receive ' + str(code))
        print('Actual response was: ' + str(response.status_code))
        return False
    # response OK
    return True


def dnac_login(host, username, password):
    if use_mock:
        return 'mock_token_abcdefg'

    url = "https://{}/api/system/v1/auth/token".format(host)
    response = requests.request("POST", url, auth=HTTPBasicAuth(username, password),
                                headers=headers, verify=False)

    # Check to make sure we got an OK response
    if not check_response_code(response, code=200):
        exit(1)

    return response.json()["Token"]


def network_device_list(dnac, token):
    if use_mock:
        data = {'response': [{'family': 'Routers', 'errorCode': None, 'lastUpdateTime': 1540126573210, 'type': 'Cisco ASR 1001-X Router', 'location': None, 'serialNumber': 'FXS1932Q1SE', 'lastUpdated': '2018-10-21 12:56:13', 'macAddress': '00:c8:8b:80:bb:00', 'role': 'BORDER ROUTER', 'softwareVersion': '16.3.2', 'hostname': 'asr1001-x.abc.inc', 'upTime': '6 days, 19:56:02.75', 'errorDescription': None, 'softwareType': 'IOS-XE', 'inventoryStatusDetail': '<status><general code="SUCCESS"/></status>', 'tagCount': '0', 'locationName': None, 'collectionInterval': 'Global Default', 'roleSource': 'AUTO', 'associatedWlcIp': '', 'bootDateTime': '2018-01-11 15:47:26', 'collectionStatus': 'Managed', 'interfaceCount': '12', 'lineCardCount': '9', 'lineCardId': '5e1b93c1-bed2-4324-b504-7bd0ed564c6d, 80781bb5-32b4-415e-96b4-ce580f66ac6e, aae1f793-fd41-420a-ab0e-4a53ead7af08, 6855077f-deab-479d-bafd-630f3f51cf71, a6fabc8d-3163-4fcb-b6c0-6244d35f69c5, 3ca823be-2c16-4cc8-b870-5993a53f8c50, 9dd486e6-c3b2-4e33-90dc-8e32c8877892, 375caca8-46da-413a-92af-d019a095ef47, 0cb53bff-e124-430e-a2b1-4337b5777a47', 'managementIpAddress': '10.10.22.74', 'memorySize': '3819298032', 'platformId': 'ASR1001-X', 'reachabilityFailureReason': '', 'reachabilityStatus': 'Reachable', 'series': 'Cisco ASR 1000 Series Aggregation Services Routers', 'snmpContact': '', 'snmpLocation': '', 'tunnelUdpPort': None, 'waasDeviceMode': None, 'apManagerInterfaceIp': '', 'instanceTenantId': 'SYS0', 'instanceUuid': '5337536f-0bb4-40eb-abd6-676894c9712c', 'id': '5337536f-0bb4-40eb-abd6-676894c9712c'}, {'family': 'Switches and Hubs', 'errorCode': None, 'lastUpdateTime': 1540126446869, 'type': 'Cisco Catalyst 9300 Switch', 'location': None, 'serialNumber': 'FCW2136L0AK', 'lastUpdated': '2018-10-21 12:54:06', 'macAddress': 'f8:7b:20:67:62:80', 'role': 'ACCESS', 'softwareVersion': '16.6.1', 'hostname': 'cat_9k_1.abc.inc', 'upTime': '5 days, 2:16:08.53', 'errorDescription': None, 'softwareType': 'IOS-XE', 'inventoryStatusDetail': '<status><general code="SUCCESS"/></status>', 'tagCount': '0', 'locationName': None, 'collectionInterval': 'Global Default', 'roleSource': 'AUTO', 'associatedWlcIp': '', 'bootDateTime': '2018-01-11 14:42:26', 'collectionStatus': 'Managed', 'interfaceCount': '41', 'lineCardCount': '2', 'lineCardId': '1cd043ef-aaf7-4b2e-b720-7af782b98b1c, a2b2467b-1692-46d4-8c64-e1765945efc1', 'managementIpAddress': '10.10.22.66', 'memorySize': '889226872', 'platformId': 'C9300-24UX', 'reachabilityFailureReason': '', 'reachabilityStatus': 'Reachable', 'series': 'Cisco Catalyst 9300 Series Switches', 'snmpContact': '', 'snmpLocation': '', 'tunnelUdpPort': None, 'waasDeviceMode': None, 'apManagerInterfaceIp': '', 'instanceTenantId': 'SYS0', 'instanceUuid': '7db64c76-60d6-4ba7-a3cd-3c9efe8b652b', 'id': '7db64c76-60d6-4ba7-a3cd-3c9efe8b652b'}, {'family': 'Switches and Hubs', 'errorCode': None, 'lastUpdateTime': 1540127042444, 'type': 'Cisco Catalyst 9300 Switch', 'location': None, 'serialNumber': 'FCW2140L039', 'lastUpdated': '2018-10-21 13:04:02', 'macAddress': 'f8:7b:20:71:4d:80', 'role': 'ACCESS', 'softwareVersion': '16.6.1', 'hostname': 'cat_9k_2.abc.inc', 'upTime': '5 days, 2:27:17.97', 'errorDescription': None, 'softwareType': 'IOS-XE', 'inventoryStatusDetail': '<status><general code="SUCCESS"/></status>', 'tagCount': '0', 'locationName': None, 'collectionInterval': 'Global Default', 'roleSource': 'AUTO', 'associatedWlcIp': '', 'bootDateTime': '2018-01-11 14:44:26', 'collectionStatus': 'Managed', 'interfaceCount': '41', 'lineCardCount': '2', 'lineCardId': 'c365974a-068d-4edd-a57e-40810e869ec3, f0ce2b8f-28e0-4936-bd7c-25bc277b6cc5', 'managementIpAddress': '10.10.22.70', 'memorySize': '889226872', 'platformId': 'C9300-24UX', 'reachabilityFailureReason': '', 'reachabilityStatus': 'Reachable', 'series': 'Cisco Catalyst 9300 Series Switches', 'snmpContact': '', 'snmpLocation': '', 'tunnelUdpPort': None, 'waasDeviceMode': None, 'apManagerInterfaceIp': '', 'instanceTenantId': 'SYS0', 'instanceUuid': '4757da48-3730-4833-86db-a0ebfbdf0009', 'id': '4757da48-3730-4833-86db-a0ebfbdf0009'}, {'family': 'Switches and Hubs', 'errorCode': None, 'lastUpdateTime': 1540105424432, 'type': 'Cisco Catalyst38xx stack-able ethernet switch', 'location': None, 'serialNumber': 'FOC1833X0AR', 'lastUpdated': '2018-10-21 07:03:44', 'macAddress': 'cc:d8:c1:15:d2:80', 'role': 'DISTRIBUTION', 'softwareVersion': '16.6.2s', 'hostname': 'cs3850.abc.inc', 'upTime': '4 days, 20:22:00.02', 'errorDescription': None, 'softwareType': 'IOS-XE', 'inventoryStatusDetail': '<status><general code="SYNC"/></status>', 'tagCount': '0', 'locationName': None, 'collectionInterval': 'Global Default', 'roleSource': 'AUTO', 'associatedWlcIp': '', 'bootDateTime': '2018-01-15 03:40:27', 'collectionStatus': 'In Progress', 'interfaceCount': '59', 'lineCardCount': '2', 'lineCardId': '42047c3d-4648-4df9-a256-ba1238ba8905, e3b99b6b-ca0b-4bc9-a561-34e1049e88f7', 'managementIpAddress': '10.10.22.69', 'memorySize': '873744896', 'platformId': 'WS-C3850-48U-E', 'reachabilityFailureReason': '', 'reachabilityStatus': 'Reachable', 'series': 'Cisco Catalyst 3850 Series Ethernet Stackable Switch', 'snmpContact': '', 'snmpLocation': '', 'tunnelUdpPort': None, 'waasDeviceMode': None, 'apManagerInterfaceIp': '', 'instanceTenantId': 'SYS0', 'instanceUuid': '99b1ec00-3dcb-44b8-9b6e-2ad6fc141f36', 'id': '99b1ec00-3dcb-44b8-9b6e-2ad6fc141f36'}], 'version': '1.0'}
    else:
        url = "https://{}/dna/intent/api/v1/network-device".format(dnac['host'])
        headers["x-auth-token"] = token
        response = requests.get(url, headers=headers, verify=False)

        if not check_response_code(response, code=200):
            exit(1)

        data = response.json()

    # pp.pprint(data)
    for item in data['response']:
        dnac_devices.add_row([item["hostname"],item["platformId"],item["softwareType"],item["softwareVersion"],item["upTime"]])


def network_health_result(dnac, executionId):
    if use_mock:
        # data mock-up with a 90% health score
        data = {'bapiKey': 'ca91-da84-401a-bba1', 'bapiName': 'Network Health', 'bapiExecutionId': '935c2d98-e73d-41a1-9d71-74e1a96cc1e1', 'startTime': 'Sun Oct 21 13:58:45 UTC 2018', 'startTimeEpoch': 1540130325970, 'endTime': 'Sun Oct 21 13:58:46 UTC 2018', 'endTimeEpoch': 1540130326767, 'timeDuration': 797, 'status': 'SUCCESS', 'bapiSyncResponse': '{"response":{"measuredBy":"global","latestMeasuredByEntity":null,"latestHealthScore":90,"monitoredDevices":4,"unMonitoredDevices":0,"healthDistirubution":[{"category":"Access","totalCount":2,"healthScore":100,"goodPercentage":100,"badPercentage":0,"fairPercentage":0},{"category":"Distribution","totalCount":1,"healthScore":100,"goodPercentage":100,"badPercentage":0,"fairPercentage":0},{"category":"Router","totalCount":1,"healthScore":100,"goodPercentage":100,"badPercentage":0,"fairPercentage":0}]}}'}
    else:
        # requests may take several seconds to execute.  Retry the request until successful
        request_in_progress = True
        url = "https://{}/api/dnacaap/v1/dnacaap/management/execution-status/{}".format(dnac['host'], executionId)
        while request_in_progress:
            response = requests.get(url, headers=headers, verify=False)

            if not check_response_code(response, code=200):
                exit(1)

            data = response.json()

            # print out the request status
            print (data["status"] + ' ', end='')
            if data["status"] != 'IN_PROGRESS':
                request_in_progress = False
                print('DONE')
            else:
                # wait for 5 seconds to try again
                time.sleep(5)

    # pp.pprint(data)

    # This could also be converted to json if desired instead of using regular expressions
    # re_match = re.search(r'"latestHealthScore":(\d+)', data['bapiSyncResponse'])
    re_match = re.search(r'"latestHealthScore":(\d+)', str(data))
    if re_match:
        latestHealthScore = re_match.group(1)
    else:
        print('Could not find latestHealthScore in response!')
        exit(1)

    return latestHealthScore


def network_health_request(dnac, token):
    if use_mock:
        return 'mock_executionId_abcdefg'
    else:

        url = "https://{}/dna/intent/api/v1/network-health?timestamp=".format(dnac['host'])
        headers["x-auth-token"] = token
        response = requests.get(url, headers=headers, verify=False)

        # Expect to get back a 202 'accepted' code from DNAC
        if not check_response_code(response, code=202):
            exit(1)

        data = response.json()

    return data["executionId"]

def network_health(dnac, token):
    # Request the network health and get back an execution ID
    executionId = network_health_request(dnac,token)
    print ('Got executionId = ' + executionId)

    # Retrieve the actual result
    return network_health_result(dnac, executionId)


login = dnac_login(dnac["host"], dnac["username"], dnac["password"])
network_device_list(dnac, login)
health_score = network_health(dnac, login)

print(dnac_devices)
print('+++')
print('The current health score is: ', health_score)

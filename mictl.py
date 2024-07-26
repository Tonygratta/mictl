import ipaddress
from os import path
from os import mkdir
from netmiko import ConnectHandler

DEF_INTERFACE = '192.168.1.250/24' # Router interface in IP.AD.DR.ESS/prefixlen format
DHCP_S = -10 # DHCP start range IP address shifting from outer interface 
DHCP_E = -1 # DHCP end range IP address shifting from outer interface 
DEF_USERNAME = 'admin'
DEF_ROUTERNAME = 'router.lan' # Router hostname or IP address for connecting to. Will be using 'router.lan' for DNS setting in case of IP.
DEF_PORT = '22'
DEF_READINITCONF = True
DEF_READRESULTCONF = True

print ("Input router IP/len (default is " + DEF_INTERFACE + ")")
REQ_INTERFACE = input ()
if REQ_INTERFACE:
    DEF_INTERFACE = REQ_INTERFACE

INT_NET_OBJECT = ipaddress.IPv4Interface(DEF_INTERFACE)
DHCP_START_OBJECT = INT_NET_OBJECT.ip + DHCP_S
DHCP_END_OBJECT = INT_NET_OBJECT.ip + DHCP_E
NETWORK = str (INT_NET_OBJECT.network)
ROUTER = str (INT_NET_OBJECT.ip)
DHCP_START = str (DHCP_START_OBJECT)
DHCP_END = str (DHCP_END_OBJECT)
rtr_prefixlen = INT_NET_OBJECT.network.prefixlen

print ("***")
print ("INTERFACE = " + DEF_INTERFACE)
print ("NETWORK = " + NETWORK)
print ("ROUTER = " + ROUTER)
print ("DHCP_START = " + DHCP_START)
print ("DHCP_END = " + DHCP_END)
print ("***")

# Checking if the DHCP addresses in the same net as router
if DHCP_START_OBJECT not in INT_NET_OBJECT.network.hosts()  or \
   DHCP_END_OBJECT not in INT_NET_OBJECT.network.hosts():
    print ("ERROR: DHCP addresses not in the same net as router. Do you really WANT to write this? (yes/no)")
    if input().lower() != 'yes':
        exit()


print ("Input password for " + DEF_USERNAME)
PASSWORD = input()


logspath = path.join(path.dirname(__file__), "logs")
if not path.exists(logspath):
    mkdir (logspath)

mikrotik_router_1 = {
'device_type': 'mikrotik_routeros',
'host': DEF_ROUTERNAME,
'port': DEF_PORT,
'username': DEF_USERNAME,
'password': PASSWORD,
'session_log': path.join(logspath, "netmiko_session.log")
}

with ConnectHandler(**mikrotik_router_1) as sshCli:
    
    prompt = sshCli.find_prompt()
    print(prompt)

    if DEF_READINITCONF:
        print ("Reading config...")
        with open(path.join(logspath, "config-initial.txt"), "w") as config_file:
            config_file.write(sshCli.send_command("/export", expect_string = prompt + '[ \t]*$', read_timeout = 90.0))
        print ("Init config retrieved")
    
    #Setting dhcp pool parameters
    #/ip dhcp-server set address-pool=dhcp 0
    #/ip pool set dhcp ranges=192.168.1.220-192.168.1.248
    print ("Setting pool...")
    sshCli.send_command("/ip dhcp-server set address-pool=dhcp 0")
    command = "/ip pool set dhcp ranges=" + DHCP_START + "-" + DHCP_END
    sshCli.send_command(command)
    print ("Done.")

    #Setting dhcp network parameters
    #/ip dhcp-server network set address=192.168.1.0/24 netmask=0 (маска берётся от интерфейса) gateway=192.168.1.250 dns-server=192.168.1.250 0
    print ("Setting DHCP-Server...")
    command = "/ip dhcp-server network set address=" + NETWORK + " netmask=0 gateway=" + ROUTER + " dns-server=" + ROUTER + " 0"
    sshCli.send_command(command)
    print ("Done.")    

    #Setting DNS static record for further connecting to router using static hostname
    #/ip dns static set name=router.lan address=192.168.1.250 0
    print ("Setting DNS...")
    
    try:
        ipaddress.ip_address(DEF_ROUTERNAME)
        print ("WARNING: IP address is defined instead of hostname. Name 'router.lan' will be using.")
        command = "/ip dns static set name=" + "router.lan" + " address=" + ROUTER + " 0"
        sshCli.send_command(command)

    except ValueError:
        command = "/ip dns static set name=" + DEF_ROUTERNAME + " address=" + ROUTER + " 0"
        sshCli.send_command(command)

    print ("Done.")

    #Setting Router IP address
    #/ip address set address=192.168.1.250/24 interface=bridge 0
    print ("Setting Address...")
    command = "/ip address set interface=bridge address=" + DEF_INTERFACE + " 0"
    sshCli.send_command(command)
    print ("Done.")

    #print (sshCli.send_command("/interface print", expect_string = '\n\n\n'))

    if DEF_READRESULTCONF:
        print ("Reading config...")
        with open(path.join(logspath, "config-final.txt"), "w") as config_file:
            config_file.write(sshCli.send_command("/export", expect_string = prompt + '[ \t]*$', read_timeout = 90.0))
        print ("Final config retrieved")

    print ("Exit")

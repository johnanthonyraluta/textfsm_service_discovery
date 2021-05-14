from modules.service_fact_collector import service_facts
from datetime import datetime
import pandas as pd
import sys
try:
  sys.argv[1]
  sys.argv[2]
  sys.argv[3]
  sys.argv[4]
except:
  print("Please provide the host management IP, hostname, and service to be tested e.g infra,vpws,vpls,l3vpn,evpn or all")
  sys.exit(1)
myhost = sys.argv[1]
hostname = sys.argv[2]
service = sys.argv[3]
delay = int(sys.argv[4])
rnodes = ["10.205.130.1","10.205.130.2","10.205.130.3"]
date = datetime.now().strftime("%Y_%m_%d-%I%p")
path = r"/home/users/jraluta/tnt_script/textfsm/data_output/"
host_path = path + hostname + "_service_check_" + date + ".xlsx"
writer = pd.ExcelWriter(host_path, engine = 'xlsxwriter')
initiate_connection = service_facts()
session = initiate_connection.init_conn(host=myhost,delay_factor=delay)
print(session)

if service == "infra" or service == "all":
    try:
        infra = initiate_connection.infra_facts(session,writer)
    except:
        print("Aborting task on " + hostname)

if service == "vpws" or service == "all":
    try:
        l2p2p = initiate_connection.l2vpn_p2p_facts(session,writer)
    except:
        print("Aborting task on " + hostname)
        print("An internal error occured or no vpws configured on " + hostname)

if service == "vpls" or service == "all":
    try:
        vpls = initiate_connection.l2vpn_p2mp_facts(session,writer)
    except:
       print("Aborting task on " + hostname)
       print("An internal error occured or no vpls configured on " + hostname)

if service == "dhcp" or service == "all":
    try:
        dhcp = initiate_connection.dhcp_facts(session,writer)
    except:
       print("Aborting task on " + hostname)
       print("An internal error occured or no dhcp configured on " + hostname)


if service == "evpn" or service == "all":
    try:
        evpn = initiate_connection.evpn_facts(session,writer)
    except:
       print("Aborting task on " + hostname)
       print("An internal error occured or no evpn configured on " + hostname)

if service == "l3vpn" or service == "all":
    try:
        l3vpn_service_check = initiate_connection.l3vpn_v2(session,writer)
    except:
        print("Aborting task on " + hostname)
        print("An internal error occured or no l3vpn configured on " + hostname)

if service == "remote_ping":
    rnode_sess = initiate_connection.init_conn(host="10.205.138.1",delay_factor=delay)
    rping = initiate_connection.remote_ping(session,rnode_sess,writer)
    print("Disconnecting remote...")
    rnode_sess.disconnect()

writer.save()
session.disconnect()
print("Disconnected " + hostname)

from ntc_templates.parse import parse_output
from netmiko import ConnectHandler
from datetime import datetime
import pandas as pd
import json
import ipaddr
import random
import time
l2p2mp=pd.DataFrame()
l3vpn=pd.DataFrame()
ip_int=pd.DataFrame()
int_desc=pd.DataFrame()

#date = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")

class service_facts():
    def init_conn(self,host,delay_factor):
        print('Connecting to ' + host + '...')
        tnt_session = ConnectHandler(
            device_type="cisco_xr",
            host=host,
            username="pldtadmin",
            password="3nter_Me-1n2admin",
            global_delay_factor=delay_factor
        )
        return tnt_session
    def infra_facts(self,tnt_session,writer):
        #tnt_session = self.init_conn()
        infra=pd.DataFrame()
        ip_int_infra=pd.DataFrame()
        int_desc_infra=pd.DataFrame()
        l3_facts = tnt_session.send_command("show arp", use_textfsm=True)
        ip_facts = tnt_session.send_command("show ip interface brief | ex Shutdown", use_textfsm=True)
        #tint_session.disconnect()
        for t in l3_facts:
            infra = infra.append(t, ignore_index=True)
        print(infra.head())
        pd.DataFrame(infra).to_csv('./data_output/infra.csv', index=False)
        #tnt_session.disconnect()
        for t in ip_facts:
            ip_int_infra=ip_int_infra.append(t, ignore_index=True)
        pd.DataFrame(ip_int_infra).to_csv('./data_output/ip_int_infra.csv', index=False)
        print(ip_int_infra.head())
        df = pd.read_csv("./data_output/ip_int_infra.csv")
        df1 = pd.read_csv("./data_output/infra.csv")
        df_new = df.rename(columns={'intf': 'interface','ipaddr':'src_ip'})
        results = pd.merge(df_new, df1, how='left', on=["interface", "interface"])
        indexNames = results[(results['state'] == 'Interface')].index
        results.drop(indexNames, inplace=True)
        df = results.dropna()
        print(df.head())
        pd.DataFrame(results).to_csv('./data_output/merged_out_infra.csv', index=False)
        pd.read_csv("./data_output/merged_out_infra.csv")
        intf_list = []
        for intf in df['interface']:
            if intf in intf_list:
                continue
            else:
                intf_list.append(intf)

        for intf in intf_list:
            mac_list = []
            print(f"show interface {intf}")
            int_facts = tnt_session.send_command(f"show interface {intf}", use_textfsm=True)
            desc = int_facts[0]['description']
            rate_pps_in = int_facts[0]['rate_pps_in']
            rate_pps_out = int_facts[0]['rate_pps_out']
            rate_bps_in = int_facts[0]['rate_bps_in']
            rate_bps_out = int_facts[0]['rate_bps_out']
            for index, row in df.iterrows():
                try:
                    if row["interface"] == intf:
                        mac_list.append(row['mac'])
                except:
                    continue
            mac_list = [mac_list[0], mac_list[-1]]
            print(mac_list)
            src_ip = df.loc[df['mac'] == mac_list[0], 'src_ip'].iloc[0]
            vrf = df.loc[df['mac'] == mac_list[0], 'vrf'].iloc[0]
            dst_ip = df.loc[df['mac'] == mac_list[0], 'address'].iloc[0]
            command = "ping " + dst_ip + " source " + src_ip
            print(command)
            ping_result = tnt_session.send_command(command, use_textfsm=True)
            ping_json = json.dumps(ping_result[0],indent=4, sort_keys=True)
            if ping_result[0]['success_pct'] == '100':
                df.loc[df['mac'] == mac_list[0], ['ping_result']] = "Ping Success"
            elif ping_result[0] == []:
                df.loc[df['mac'] == mac_list[0], ['ping_result']] = "Ping Failed"
            else:
                df.loc[df['mac'] == mac_list[0], ['ping_result']] = "Ping Failed"
            exec_time = tnt_session.send_command("show clock", use_textfsm=True)
            df.loc[df['mac'] == mac_list[0], ['exec_time']] = exec_time
            df.loc[df['mac'] == mac_list[0], ['ping_test']] = ping_json
            df.loc[df['mac'] == mac_list[0], ['commands']] = command
            df.loc[df['mac'] == mac_list[0], ['service_name']] = desc
            df.loc[df['mac'] == mac_list[0], ['rate_bps_in']] = rate_bps_in
            df.loc[df['mac'] == mac_list[0], ['rate_bps_out']] = rate_bps_out
            df.loc[df['mac'] == mac_list[0], ['rate_pps_in']] = rate_pps_in
            df.loc[df['mac'] == mac_list[0], ['rate_pps_out']] = rate_pps_out
            # output_df.loc[output_df['DISTANCE_TO_TARGET_SITE'] <= 10, ['SOURCE_SFP_TYPE']] = 'LR4'
            src_ip = df.loc[df['mac'] == mac_list[-1], 'src_ip'].iloc[0]
            vrf = df.loc[df['mac'] == mac_list[-1], 'vrf'].iloc[0]
            dst_ip = df.loc[df['mac'] == mac_list[-1], 'address'].iloc[0]
            command = "ping " + dst_ip + " source " + src_ip
            print(command)
            ping_result = tnt_session.send_command(command, use_textfsm=True)
            ping_json = json.dumps(ping_result[0],indent=4, sort_keys=True)
            if ping_result[0]['success_pct'] == '100':
                df.loc[df['mac'] == mac_list[-1], ['ping_result']] = "Ping Success"
            elif ping_result[0] == []:
                df.loc[df['mac'] == mac_list[-1], ['ping_result']] = "Ping Failed"
            else:
                df.loc[df['mac'] == mac_list[-1], ['ping_result']] = "Ping Failed"
            exec_time = tnt_session.send_command("show clock", use_textfsm=True)
            df.loc[df['mac'] == mac_list[-1], ['exec_time']] = exec_time
            df.loc[df['mac'] == mac_list[-1], ['ping_test']] = ping_json
            df.loc[df['mac'] == mac_list[-1], ['commands']] = command
            df.loc[df['mac'] == mac_list[-1], ['service_name']] = desc
            df.loc[df['mac'] == mac_list[-1], ['rate_bps_in']] = rate_bps_in
            df.loc[df['mac'] == mac_list[-1], ['rate_bps_out']] = rate_bps_out
            df.loc[df['mac'] == mac_list[-1], ['rate_pps_in']] = rate_pps_in
            df.loc[df['mac'] == mac_list[-1], ['rate_pps_out']] = rate_pps_out
        write_df = df[["service_name","interface","rate_bps_in","rate_bps_out","rate_pps_in","rate_pps_out",\
                   "mac","vrf","proto",\
                   "status","src_ip",\
                   "address","commands",\
                   "ping_test","ping_result","exec_time"]]
        #pd.DataFrame(write_df).to_csv(f"./data_output/final_infra_"+date+".csv", index=False)
        pd.DataFrame(write_df).to_excel(writer, sheet_name="infra",index=False)
        #tnt_session.disconnect()
        #print('Disconnected')

    def l3vpn_facts(self,tnt_session,writer):
        #tnt_session = self.init_conn()
        #l3vpn=pd.DataFrame()
        ip_int=pd.DataFrame()
        #l3_facts = tnt_session.send_command("show arp vrf all det", use_textfsm=True)
        ip_facts = tnt_session.send_command("show ip interface brief | ex default", use_textfsm=True)
        #tnt_session.disconnect()
        for t in ip_facts:
            ip_int = ip_int.append(t, ignore_index=True)
        #print(l3vpn.head())
        pd.DataFrame(ip_int).to_csv('./data_output/ip_int.csv', index=False)
        indexNames = ip_int[(ip_int['status'] == 'Shutdown')].index
        ip_int.drop(indexNames, inplace=True)
        #tnt_session.disconnect()
        vrf_df = pd.DataFrame()
        vrf_list=[]
        for vrfs in ip_int['vrf']:
            if vrfs in vrf_list:
                continue
            else:
                vrf_list.append(vrfs)
        for vrf in vrf_list:
            print(vrf)
            tnt_session.send_command("term le 30")
            try:
                my_vrf = tnt_session.send_command(f"show arp vrf {vrf} detail", use_textfsm=True, expect_string=" --More-- ")
                tnt_session.send_command_timing("\x03")
                tnt_session.send_command_timing("show clock")
            except:
                my_vrf = tnt_session.send_command(f"show arp vrf {vrf} detail", use_textfsm=True)
                tnt_session.send_command("show clock")
            if isinstance(my_vrf, str) == True:
                continue
            else:
                for t in my_vrf:
                    vrf_df = vrf_df.append(t,ignore_index=True)
        tnt_session.send_command("show clock")
        #print(ip_int.head())
        df_new = ip_int.rename(columns={'intf': 'interface','ipaddr':'src_ip'})
        df1 = vrf_df
        results = pd.merge(df_new, df1, how='left', on=["interface", "interface"])
        indexNames = results[(results['state'] != 'Dynamic')].index
        results.drop(indexNames, inplace=True)
        new_results = results.drop_duplicates(subset=["interface","vrf","address"])
        df = new_results.dropna()
        print(df.head())
        pd.DataFrame(df).to_csv('./data_output/merged_out.csv', index=False)
        pd.read_csv("./data_output/merged_out.csv")
        intf_list = []
        for intf in df['interface']:
            if intf in intf_list:
                continue
            else:
                intf_list.append(intf)
        tnt_session.send_command("show clock")
        for intf in intf_list:
            tnt_session.send_command("term le 0")
            int_facts = tnt_session.send_command(f"show interface {intf}", use_textfsm=True)
            desc = int_facts[0]['description']
            rate_pps_in = int_facts[0]['rate_pps_in']
            rate_pps_out = int_facts[0]['rate_pps_out']
            rate_bps_in = int_facts[0]['rate_bps_in']
            rate_bps_out = int_facts[0]['rate_bps_out']
            df.loc[df['interface'] == intf, ['service_name']] = desc
            df.loc[df['interface'] == intf, ['rate_bps_in']] = rate_bps_in
            df.loc[df['interface'] == intf, ['rate_bps_out']] = rate_bps_out
            df.loc[df['interface'] == intf, ['rate_pps_in']] = rate_pps_in
            df.loc[df['interface'] == intf, ['rate_pps_out']] = rate_pps_out
            tnt_session.send_command("show clock")
        address_list = []
        for ip in df['address']:
            if ip in address_list:
                continue
            else:
                address_list.append(ip)
        for dest_ip in address_list:
            tnt_session.send_command("show clock")
            src_ip = df.loc[df['address'] == dest_ip, 'src_ip'].iloc[0]
            vrf = df.loc[df['address'] == dest_ip, 'vrf'].iloc[0]
            dst_ip = dest_ip
            command = "ping " +'vrf ' +vrf + " " + dst_ip + " source " + src_ip
            print(command)
            try:
                ping_result = tnt_session.send_command(command, use_textfsm=True)
                ping_json = json.dumps(ping_result[0], indent=4, sort_keys=True)
                if ping_result[0]['success_pct'] == '100':
                    df.loc[df['address'] == dest_ip, ['ping_result']] = "Ping Success"
                elif ping_result[0] == []:
                    df.loc[df['address'] == dest_ip, ['ping_result']] = "Ping Failed"
                else:
                    df.loc[df['address'] == dest_ip, ['ping_result']] = "Ping Failed"
                exec_time = tnt_session.send_command("show clock", use_textfsm=True)
                df.loc[df['address'] == dest_ip, ['exec_time']] = exec_time
                df.loc[df['address'] == dest_ip, ['ping_test']] = ping_json
                df.loc[df['address'] == dest_ip, ['commands']] = command
                tnt_session.send_command("show clock")
            except:
                df.loc[df['address'] == dest_ip, ['ping_result']] = "Ping Failed"
                df.loc[df['address'] == dest_ip, ['exec_time']] = ""
                df.loc[df['address'] == dest_ip, ['ping_test']] = ""
                df.loc[df['address'] == dest_ip, ['commands']] = ""
        write_df = df[["service_name","interface","rate_bps_in","rate_bps_out","rate_pps_in","rate_pps_out",\
                   "mac","vrf","proto",\
                   "status","src_ip",\
                   "address","commands","ping_test","ping_result","exec_time"]]
        #pd.DataFrame(write_df).to_csv(f"./data_output/final_l3vpn_"+date+".csv", index=False)
        pd.DataFrame(write_df).to_excel(writer, sheet_name="l3vpn",index=False)
        #tnt_session.disconnect()
        #print('Disconnected')
    def l3vpn_v2(self,tnt_session,writer):
        ip_int=pd.DataFrame()
        vrf_df = pd.DataFrame()
        #l3_facts = tnt_session.send_command("show arp vrf all det", use_textfsm=True)
        ip_facts = tnt_session.send_command("show ip interface brief | ex default", use_textfsm=True)
        #tnt_session.disconnect()
        for t in ip_facts:
            ip_int = ip_int.append(t, ignore_index=True)
        #print(l3vpn.head())
        pd.DataFrame(ip_int).to_csv('./data_output/ip_int.csv', index=False)
        indexNames = ip_int[(ip_int['proto'] == 'Down')].index
        ip_int.drop(indexNames, inplace=True)
        # indexNames = ip_int[(ip_int['proto'] == 'Down')].index
        # ip_int.drop(indexNames, inplace=True)
        print(ip_int.head())
        df = ip_int.dropna()
        for intf in df['intf']:
            vrf = df.loc[df['intf'] == intf, 'vrf'].iloc[0]
            print(vrf)
            tnt_session.send_command("term le 10")
            try:
                my_vrf = tnt_session.send_command(f"show arp vrf {vrf} detail | i {intf}", use_textfsm=True, expect_string=" --More-- ",delay_factor=3)
                print(type(my_vrf))
                tnt_session.send_command_timing("\x03")
                tnt_session.send_command_timing("show clock")
                tnt_session.send_command("term le 50")
            except:
                my_vrf = tnt_session.send_command(f"show arp vrf {vrf} detail | i {intf}", use_textfsm=True,delay_factor=3)
                print(type(my_vrf))
                tnt_session.send_command("show clock")
                tnt_session.send_command("term le 50")
            if isinstance(my_vrf, str) == True:
                continue
            else:
                for t in my_vrf:
                    vrf_df = vrf_df.append(t,ignore_index=True)
            try:
                tnt_session.send_command("term le 0")
                print(f"show interface {intf}")
                int_facts = tnt_session.send_command(f"show interface {intf}", use_textfsm=True,delay_factor=5)
                desc = int_facts[0]['description']
                rate_pps_in = int_facts[0]['rate_pps_in']
                rate_pps_out = int_facts[0]['rate_pps_out']
                rate_bps_in = int_facts[0]['rate_bps_in']
                rate_bps_out = int_facts[0]['rate_bps_out']
                df.loc[df['intf'] == intf, ['service_name']] = desc
                df.loc[df['intf'] == intf, ['rate_bps_in']] = rate_bps_in
                df.loc[df['intf'] == intf, ['rate_bps_out']] = rate_bps_out
                df.loc[df['intf'] == intf, ['rate_pps_in']] = rate_pps_in
                df.loc[df['intf'] == intf, ['rate_pps_out']] = rate_pps_out
                tnt_session.send_command("show clock")
            except:
                df.loc[df['intf'] == intf, ['service_name']] = ""
                df.loc[df['intf'] == intf, ['rate_bps_in']] = ""
                df.loc[df['intf'] == intf, ['rate_bps_out']] = ""
                df.loc[df['intf'] == intf, ['rate_pps_in']] = ""
                df.loc[df['intf'] == intf, ['rate_pps_out']] = ""
        df_new = df.rename(columns={'intf': 'interface', 'ipaddr': 'src_ip'})
        indexNames = vrf_df[(vrf_df['state'] != 'Dynamic')].index
        vrf_df.drop(indexNames, inplace=True)
        print(vrf_df.head())
        results = pd.merge(df_new, vrf_df, how='left', on=["interface", "interface"])
        results = results.dropna()
        address_list = []
        for ip in results['address']:
            if ip in address_list:
                continue
            else:
                address_list.append(ip)
        for dest_ip in address_list:
            tnt_session.send_command("show clock")
            src_ip = results.loc[results['address'] == dest_ip, 'src_ip'].iloc[0]
            vrf = results.loc[results['address'] == dest_ip, 'vrf'].iloc[0]
            dst_ip = dest_ip
            command = "ping " +'vrf ' +vrf + " " + dst_ip + " source " + src_ip + " repeat 20 timeout 1"
            print(command)
            try:
                ping_result = tnt_session.send_command(command, use_textfsm=True,delay_factor=5)
                ping_json = json.dumps(ping_result[0], indent=4, sort_keys=True)
                if ping_result[0]['success_pct'] == '100':
                    results.loc[results['address'] == dest_ip, ['ping_result']] = "Ping Success"
                elif ping_result[0] == []:
                    results.loc[results['address'] == dest_ip, ['ping_result']] = "Ping Failed"
                else:
                    results.loc[results['address'] == dest_ip, ['ping_result']] = "Ping Failed"
                exec_time = tnt_session.send_command("show clock", use_textfsm=True)
                results.loc[results['address'] == dest_ip, ['exec_time']] = exec_time
                results.loc[results['address'] == dest_ip, ['ping_test']] = ping_json
                results.loc[results['address'] == dest_ip, ['commands']] = command
                tnt_session.send_command("show clock")
            except:
                ping_result = tnt_session.send_command(command, use_textfsm=True,expect_string=".",delay_factor=8,auto_find_prompt=False)
                tnt_session.send_command_timing("\x03")
                tnt_session.send_command_timing("show clock")
                results.loc[results['address'] == dest_ip, ['ping_result']] = "Ping Failed"
                results.loc[results['address'] == dest_ip, ['exec_time']] = ""
                results.loc[results['address'] == dest_ip, ['ping_test']] = ""
                results.loc[results['address'] == dest_ip, ['commands']] = command
        write_df = results[["service_name","interface","rate_bps_in","rate_bps_out","rate_pps_in","rate_pps_out",\
                   "mac","vrf","proto",\
                   "status","src_ip",\
                   "address","commands","ping_test","ping_result","exec_time"]]
        #pd.DataFrame(write_df).to_csv(f"./data_output/final_l3vpn_"+date+".csv", index=False)
        write_df = write_df.drop_duplicates()
        pd.DataFrame(write_df).to_excel(writer, sheet_name="l3vpn",index=False)

    def remote_ping(self,tnt_session,rnode_sess,writer):
        rping = pd.read_csv('./data_output/ip_int.csv')
        indexNames = rping[(rping['proto'] == 'Down')].index
        rping.drop(indexNames, inplace=True)
        # indexNames = ip_int[(ip_int['proto'] == 'Down')].index
        # ip_int.drop(indexNames, inplace=True)
        print(rping.head())
        df = rping.dropna()
        for intf in df['intf']:
            vrf = df.loc[df['intf'] == intf, 'vrf'].iloc[0]
            cmd_list =[]
            print(vrf)
            try:
                remote_ip_ = tnt_session.send_command(f"show run router static vrf {vrf} | i {intf}")
                remote_ip_x = remote_ip_.split('\n')[1]
                remote_ip = remote_ip_x.split(" ")[3]
            except:
                continue
            # if "/32" in remote_ip:
            #     random_ip1 = remote_ip.split('/')[0]
            #     command1 = "ping " + 'vrf ' + vrf + " " + random_ip1 + " repeat 20 timeout 1"
            #     cmd_list.append(command1)
            try:
                network = ipaddr.IPv4Network(remote_ip)
            except:
                continue
            # random_ip1 = ipaddr.IPv4Address(random.randrange(int(network.network) + 1, int(network.broadcast) - 1))
            # random_ip2 = ipaddr.IPv4Address(random.randrange(int(network.network) + 1, int(network.broadcast) - 1))
            # random_ip3 = ipaddr.IPv4Address(random.randrange(int(network.network) + 1, int(network.broadcast) - 1))
            if '/32' in str(network):
                random_ip1 = (network.network)
                random_ip2 = (network.network)
                random_ip3 = (network.network)
            else:
                random_ip1 = (network.network + 1)
                random_ip2 = (network.network + 2)
                random_ip3 = (network.broadcast -1)
            command1 = "ping " + 'vrf ' + vrf + " " + str(random_ip1) + " repeat 20 timeout 1"
            command2 = "ping " + 'vrf ' + vrf + " " + str(random_ip2) + " repeat 20 timeout 1"
            command3 = "ping " + 'vrf ' + vrf + " " + str(random_ip3) + " repeat 20 timeout 1"
            cmd_list.append(command1)
            cmd_list.append(command2)
            cmd_list.append(command3)
            print(cmd_list)
            for i,command in enumerate(cmd_list):
                try:
                    print(rnode_sess)
                    ping_result = rnode_sess.send_command(command, use_textfsm=True, delay_factor=5)
                    print(ping_result)
                    ping_json = json.dumps(ping_result[0], indent=4, sort_keys=True)
                    if ping_result[0]['success_pct'] == '100':
                        df.loc[df['intf'] == intf, ['ping_result_'+str(i)]] = "Ping Success"
                        print("Ping Success")
                    elif ping_result[0] == []:
                        df.loc[df['intf'] == intf, ['ping_result_'+str(i)]] = "Ping Failed"
                        print("Ping Failed")
                    else:
                        df.loc[df['intf'] == intf, ['ping_result_'+str(i)]] = "Ping Failed"
                        print("Ping Failed")
                    exec_time = rnode_sess.send_command("show clock", use_textfsm=True)
                    df.loc[df['intf'] == intf, ['exec_time_'+str(i)]] = exec_time
                    df.loc[df['intf'] == intf,  ['ping_test_'+str(i)]] = ping_json
                    df.loc[df['intf'] == intf,  ['commands_'+str(i)]] = command
                    tnt_session.send_command("show clock")
                    print(df.head())
                except:
                    df.loc[df['intf'] == intf, ['ping_result_'+str(i)]] = "Ping Failed"
                    df.loc[df['intf'] == intf, ['exec_time_'+str(i)]] = ""
                    df.loc[df['intf'] == intf, ['ping_test_'+str(i)]] = ""
                    df.loc[df['intf'] == intf, ['commands_'+str(i)]] = command
                    print(df.head())
            # except:
            #     print('Aborting not IP')
        write_df = df.drop_duplicates()
        pd.DataFrame(write_df).to_excel(writer, sheet_name="remote_ping",index=False)

    def l2vpn_p2p_facts(self,tnt_session,writer):
        #tnt_session = self.init_conn()
        l2p2p = pd.DataFrame()
        l2p2p_facts = tnt_session.send_command("show l2vpn xconnect det", use_textfsm=True)
        #tnt_session.disconnect()
        for t in l2p2p_facts:
            l2p2p = l2p2p.append(t, ignore_index=True)
        #pd.DataFrame(l2p2p).to_csv('./data_output/l2p2p.csv', index=False)
        df = l2p2p.dropna()
        print(l2p2p.head())
        intf_list = []
        for intf in df['interface']:
            if intf in intf_list:
                continue
            else:
                intf_list.append(intf)
        for intf in intf_list:
            int_facts = tnt_session.send_command(f"show interface {intf}", use_textfsm=True)
            desc = int_facts[0]['description']
            rate_pps_in = int_facts[0]['rate_pps_in']
            rate_pps_out = int_facts[0]['rate_pps_out']
            rate_bps_in = int_facts[0]['rate_bps_in']
            rate_bps_out = int_facts[0]['rate_bps_out']
            df.loc[df['interface'] == intf, ['rate_bps_in']] = rate_bps_in
            df.loc[df['interface'] == intf, ['rate_bps_out']] = rate_bps_out
            df.loc[df['interface'] == intf, ['rate_pps_in']] = rate_pps_in
            df.loc[df['interface'] == intf, ['rate_pps_out']] = rate_pps_out
            df.loc[df['interface'] == intf, ['description']] = desc
        try:
            for neig in df['evpn_nei']:
                if neig == '0.0.0.0' or neig == '' or neig == None:
                   continue
                else:
                    command = "ping " + "mpls ipv4 " + neig + "/32" + " timeout 1"
                    print(command)
                    ping_result = tnt_session.send_command(command, use_textfsm=True)
                    ping_json = json.dumps(ping_result[0], indent=4, sort_keys=True)
                    exec_time = tnt_session.send_command("show clock", use_textfsm=True)
                    df.loc[df['evpn_nei'] == neig, ['ping_test']] = ping_json
                    df.loc[df['evpn_nei'] == neig, ['exec_time']] = exec_time
                    if ping_result[0]['success_pct'] == '100':
                        df.loc[df['evpn_nei'] == neig, ['ping_result']] = "Ping Success"
                    elif ping_result[0] == []:
                        df.loc[df['evpn_nei'] == neig, ['ping_test']] = ""
                        df.loc[df['evpn_nei'] == neig, ['exec_time']] = ""
                        df.loc[df['evpn_nei'] == neig, ['ping_result']] = "Ping Failed"
                    else:
                        df.loc[df['evpn_nei'] == neig, ['ping_test']] = ""
                        df.loc[df['evpn_nei'] == neig, ['exec_time']] = ""
                        df.loc[df['evpn_nei'] == neig, ['ping_result']] = "Ping Failed"
        except:
            df.loc[df['evpn_nei'] == neig, ['ping_test']] = ""
            df.loc[df['evpn_nei'] == neig, ['exec_time']] = ""
            df.loc[df['evpn_nei'] == neig, ['ping_result']] = "Ping Failed"


        write_df = df[["description","group","xc","evpn_nei","create_date","create_time","create_dur",\
                       "last_change_date","last_change_time","last_change_dur","last_down_date","last_down_time",\
                       "last_down_dur","state","tx","rx","interface","rate_bps_in","rate_bps_out",\
                       "rate_pps_in","rate_pps_out","ping_test","ping_result","exec_time"]]
        #pd.DataFrame(write_df).to_csv(f"./data_output/final_vpws_"+date+".csv", index=False)
        pd.DataFrame(write_df).to_excel(writer, sheet_name="vpws",index=False)
        #tnt_session.disconnect()
        #print('Disconnected')

    def l2vpn_p2mp_facts(self,tnt_session,writer):
        bdomain = pd.DataFrame()
        #tnt_session = self.init_conn()
        bd_facts = tnt_session.send_command("show l2vpn bridge-domain", use_textfsm=True)
        for t in bd_facts:
            bdomain = bdomain.append(t, ignore_index=True)
            # pd.DataFrame(l2p2p).to_csv('./data_output/l2p2p.csv', index=False)
        df = bdomain.dropna()
        print(bdomain.head())
        intf_list = []
        for intf in df['interface']:
            if intf in intf_list or "EVPN" in intf:
                continue
            else:
                intf_list.append(intf)
        print(intf_list)
        for intf in intf_list:
            try:
                int_facts = tnt_session.send_command(f"show interface {intf}",use_textfsm=True)
                desc = int_facts[0]['description']
                link_status = int_facts[0]['link_status']
                admin_state = int_facts[0]['admin_state']
                df.loc[df['interface'] == intf, ['description']] = desc
                df.loc[df['interface'] == intf, ['link_status']] = link_status
                df.loc[df['interface'] == intf, ['admin_state']] = admin_state
            except:
                continue
            print(intf)

        for bd in df['bridge_dom']:
            try:
                bd_count_0CPU0 = tnt_session.send_command(f"show l2vpn forwarding bridge-domain {bd}:{bd} location \
                              0/0/CPU0 | utility wc lines", use_textfsm=True)
                df.loc[df['bridge_dom'] == bd, ['bd_count_0CPU0']] = bd_count_0CPU0
            except:
                df.loc[df['bridge_dom'] == bd, ['bd_count_0CPU0']] = " "
            try:
                bd_count_1CPU0 = tnt_session.send_command(f"show l2vpn forwarding bridge-domain {bd}:{bd} location \
                              0/1/CPU0 | utility wc lines", use_textfsm=True)
                df.loc[df['bridge_dom'] == bd, ['bd_count_1CPU0']] = bd_count_1CPU0
            except:
                df.loc[df['bridge_dom'] == bd, ['bd_count_1CPU0']] = " "
            try:
                bd_count_6CPU0 = tnt_session.send_command(f"show l2vpn forwarding bridge-domain {bd}:{bd} location \
                              0/6/CPU0 | utility wc lines", use_textfsm=True)
                df.loc[df['bridge_dom'] == bd, ['bd_count_6CPU0']] = bd_count_6CPU0
            except:
                df.loc[df['bridge_dom'] == bd, ['bd_count_6CPU0']] = " "
            try:
                bd_count_7CPU0 = tnt_session.send_command(f"show l2vpn forwarding bridge-domain {bd}:{bd} location \
                              0/7/CPU0 | utility wc lines", use_textfsm=True)
                df.loc[df['bridge_dom'] == bd, ['bd_count_7CPU0']] = bd_count_7CPU0
            except:
                df.loc[df['bridge_dom'] == bd, ['bd_count_7CPU0']] = " "
            try:
                bd_count_RSP0CPU0 = tnt_session.send_command(f"show l2vpn forwarding bridge-domain {bd}:{bd} location \
                              0/RSP0/CPU0 | utility wc lines", use_textfsm=True)
                df.loc[df['bridge_dom'] == bd, ['bd_count_RSP0CPU0']] = bd_count_RSP0CPU0
            except:
                df.loc[df['bridge_dom'] == bd, ['bd_count_RSP0CPU0']] = " "
            try:
                bd_count_RSP1CPU0 = tnt_session.send_command(f"show l2vpn forwarding bridge-domain {bd}:{bd} location \
                              0/RSP1/CPU0 | utility wc lines", use_textfsm=True)
                df.loc[df['bridge_dom'] == bd, ['bd_count_RSP1CPU0']] = bd_count_RSP1CPU0
            except:
                df.loc[df['bridge_dom'] == bd, ['bd_count_RSP1CPU0']] = " "
            # df.loc[df['bridge_dom'] == bd, ['bd_count_0CPU0']] = bd_count_0CPU0
            # df.loc[df['bridge_dom'] == bd, ['bd_count_1CPU0']] = bd_count_1CPU0
            # df.loc[df['bridge_dom'] == bd, ['bd_count_6CPU0']] = bd_count_6CPU0
            # df.loc[df['bridge_dom'] == bd, ['bd_count_7CPU0']] = bd_count_7CPU0
            # df.loc[df['bridge_dom'] == bd, ['bd_count_RSP0CPU0']] = bd_count_RSP0CPU0
            # df.loc[df['bridge_dom'] == bd, ['bd_count_RSP1CPU0']] = bd_count_RSP1CPU0

        write_df = df[["bridge_grp","bridge_dom","state1","interface","description","link_status",\
                       "bd_count_0CPU0","bd_count_1CPU0","bd_count_6CPU0","bd_count_7CPU0",\
                       "bd_count_RSP0CPU0","bd_count_RSP1CPU0"]]
        #pd.DataFrame(write_df).to_csv(f"./data_output/final_vpls_"+date+".csv", index=False)
        pd.DataFrame(write_df).to_excel(writer, sheet_name="vpls",index=False)
        #tnt_session.disconnect()
        #print('Disconnected')
    def dhcp_facts(self,tnt_session,writer):
        dhcp = pd.DataFrame()
        #tnt_session = self.init_conn()
        dhcp_facts = tnt_session.send_command("show dhcp ipv4 server binding summ", use_textfsm=True)
        for t in dhcp_facts:
            dhcp_dict = {"state":t['state'].split('|')[0].strip(),"count":t['state'].split('|')[1].strip()}
            dhcp = dhcp.append(dhcp_dict, ignore_index=True)
            # pd.DataFrame(l2p2p).to_csv('./data_output/l2p2p.csv', index=False)
        df = dhcp.dropna()
        print(dhcp.head())
        write_df = df[["state","count"]]
        #pd.DataFrame(write_df).to_csv(f"./data_output/final_vpls_"+date+".csv", index=False)
        pd.DataFrame(write_df).to_excel(writer, sheet_name="dhcp",index=False)

    def evpn_facts(self,tnt_session,writer):
        evpn = pd.DataFrame()
        #tnt_session = self.init_conn()
        evpn_facts = tnt_session.send_command("show evpn evi", use_textfsm=True)
        for t in evpn_facts:
            evpn = evpn.append(t, ignore_index=True)
            # pd.DataFrame(l2p2p).to_csv('./data_output/l2p2p.csv', index=False)
        print(evpn)
        indexNames = evpn[(evpn['type'] != 'EVPN')].index
        evpn.drop(indexNames, inplace=True)
        df = evpn.dropna()
        print(df.head())
        for id in df["vpn_id"]:
            evpn_mac = tnt_session.send_command(f"show evpn evi vpn-id {id} mac | utility wc lines", use_textfsm=True)
            print(f"show evpn evi vpn-id {id} mac | utility wc lines")
            evpn_neig = tnt_session.send_command(f"show evpn evi vpn-id {id} neighbor")
            print(f"show evpn evi vpn-id {id} neighbor")
            df.loc[df['vpn_id'] == id, ['mac_count']] = evpn_mac
            df.loc[df['vpn_id'] == id, ['evpn_neighbor']] = evpn_neig
        write_df = df[["vpn_id","bridge_dom","type","mac_count","evpn_neighbor"]]
        #pd.DataFrame(write_df).to_csv(f"./data_output/final_vpls_"+date+".csv", index=False)
        pd.DataFrame(write_df).to_excel(writer, sheet_name="evpn",index=False)









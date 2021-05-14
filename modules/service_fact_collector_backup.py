from ntc_templates.parse import parse_output
from netmiko import ConnectHandler
from datetime import datetime
import pandas as pd
import json
l2p2mp=pd.DataFrame()
l3vpn=pd.DataFrame()
ip_int=pd.DataFrame()
int_desc=pd.DataFrame()

date = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
class service_facts():
    def init_conn(self,host):
        print('Connecting to ' + host + '...')
        tnt_session = ConnectHandler(
            device_type="cisco_xr",
            host=host,
            username="pldtadmin",
            password="3nter_Me-1n2admin",
        )
        return tnt_session
    def infra_facts(self,tnt_session):
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
        pd.DataFrame(write_df).to_csv(f"./data_output/final_infra_"+date+".csv", index=False)
        tnt_session.disconnect()
        print('Disconnected')

    def l3vpn_facts(self,tnt_session):
        #tnt_session = self.init_conn()
        l3vpn=pd.DataFrame()
        ip_int=pd.DataFrame() 
        int_desc=pd.DataFrame()
        l3_facts = tnt_session.send_command("show arp vrf all det", use_textfsm=True)
        ip_facts = tnt_session.send_command("show ip interface brief | ex default", use_textfsm=True)
        #tnt_session.disconnect()
        for t in l3_facts:
            l3vpn = l3vpn.append(t, ignore_index=True)
        #print(l3vpn.head())
        pd.DataFrame(l3vpn).to_csv('./data_output/l3vpn.csv', index=False)
        #tnt_session.disconnect()
        for t in ip_facts:
            ip_int=ip_int.append(t, ignore_index=True)
        pd.DataFrame(ip_int).to_csv('./data_output/ip_int.csv', index=False)
        #print(ip_int.head())
        df = pd.read_csv("./data_output/ip_int.csv")
        df1 = pd.read_csv("./data_output/l3vpn.csv")
        df_new = df.rename(columns={'intf': 'interface','ipaddr':'src_ip'})
        results = pd.merge(df_new, df1, how='left', on=["interface", "interface"])
        indexNames = results[(results['state'] == 'Interface')].index
        results.drop(indexNames, inplace=True)
        df = results.dropna()
        print(df.head())
        pd.DataFrame(results).to_csv('./data_output/merged_out.csv', index=False)
        pd.read_csv("./data_output/merged_out.csv")
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
            command = "ping " +'vrf ' +vrf + " " + dst_ip + " source " + src_ip
            print(command)
            ping_result = tnt_session.send_command(command, use_textfsm=True)
            ping_json = json.dumps(ping_result[0],indent=4, sort_keys=True)
            if ping_result[0]['success_pct'] == '100':
                df.loc[df['mac'] == mac_list[0], ['ping_result']] = "Ping Success"
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
            command = "ping " +'vrf ' +vrf + " " + dst_ip + " source " + src_ip
            print(command)
            ping_result = tnt_session.send_command(command, use_textfsm=True)
            ping_json = json.dumps(ping_result[0],indent=4, sort_keys=True)
            if ping_result[0]['success_pct'] == '100':
                df.loc[df['mac'] == mac_list[-1], ['ping_result']] = "Ping Success"
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
        pd.DataFrame(write_df).to_csv(f"./data_output/final_l3vpn_"+date+".csv", index=False)
        tnt_session.disconnect()
        print('Disconnected')

    def l2vpn_p2p_facts(self,tnt_session):
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

        for neig in df['evpn_nei']:
            if neig == '0.0.0.0' or neig == '':
               continue
            else:
                command = "ping " + "mpls ipv4 " + neig + "/32"
                print(command)
                ping_result = tnt_session.send_command(command, use_textfsm=True)
                ping_json = json.dumps(ping_result[0], indent=4, sort_keys=True)
                exec_time = tnt_session.send_command("show clock", use_textfsm=True)
                df.loc[df['evpn_nei'] == neig, ['ping_test']] = ping_json
                df.loc[df['evpn_nei'] == neig, ['exec_time']] = exec_time
                if ping_result[0]['success_pct'] == '100':
                   df.loc[df['evpn_nei'] == neig, ['ping_result']] = "Ping Success"
                else:
                   df.loc[df['evpn_nei'] == neig, ['ping_result']] = "Ping Failed"
        write_df = df[["description","group","xc","evpn_nei","create_date","create_time","create_dur",\
                       "last_change_date","last_change_time","last_change_dur","last_down_date","last_down_time",\
                       "last_down_dur","state","tx","rx","interface","rate_bps_in","rate_bps_out",\
                       "rate_pps_in","rate_pps_out","ping_test","ping_result","exec_time"]]
        pd.DataFrame(write_df).to_csv(f"./data_output/final_vpws_"+date+".csv", index=False)
        tnt_session.disconnect()
        print('Disconnected')

    def l2vpn_p2mp_facts(self,tnt_session):
        tnt_session = self.init_conn()
        l2p2mp_facts = tnt_session.send_command("show l2vpn bridge-domain", use_textfsm=True)
        for t in l2p2mp_facts:
            l2p2mp.append(t, ignore_index=True)
        pd.DataFrame(l2p2mp).to_csv('/data_output/l2p2mp.csv', index=False)
        print(l2p2mp.head())

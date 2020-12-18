import subprocess
import json
import socket
import requests
import netaddr
import os
import string
import time

tmp_asn_ip_ranges = []

final_unresolved_domains = []
final_ip_data = {}
final_found_asns = {}



def su(s):
    # try:
    #     return s.encode('ascii','ignore')
    # except:
    return s

def process_asn(ip_address):
    # Determine if ASN Already Found
    found_asn = 0
    if not len(netaddr.all_matching_cidrs(ip_address, tmp_asn_ip_ranges)):
        r = requests.get('https://api.bgpview.io/ip/'+ip_address)
        asn_data = r.json()
        for prefix in asn_data['data']['prefixes']:
            found_asn = prefix['asn']['asn']
            tmp_asn_ip_ranges.append(su(prefix['prefix']))
            ans_dict = {'asn_number':prefix['asn']['asn'], 'prefixes':[su(prefix['prefix'])], 'country_code':su(prefix['asn']['country_code']), 'name':su(prefix['asn']['name']), 'description':su(prefix['asn']['description'])}
            if prefix['asn']['asn'] not in final_found_asns:
                final_found_asns[prefix['asn']['asn']] = ans_dict
            else:
                if prefix['prefix'] not in final_found_asns[prefix['asn']['asn']]['prefixes']:
                    final_found_asns[prefix['asn']['asn']]['prefixes'].append(prefix['prefix'])
    else:
        for k, v in final_found_asns.items():
            for prefix in v['prefixes']:
                if len(netaddr.all_matching_cidrs(ip_address, [prefix])):
                    found_asn = k

    return final_found_asns[found_asn]

def check_http_port(ip_address):
    ip = netaddr.IPAddress(ip_address)
    ports_to_return = []
    if (ip.version == 4):
        for port in [80, 443]:
             sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
             sock.settimeout(0.5)
             result = sock.connect_ex((ip_address, port))
             if result == 0:
                 ports_to_return.append(port)
             sock.close()
    return ports_to_return

def getRevDns(ip):
    output = str(subprocess.check_output(['dig', '+short', '-x', ip])).split('\n')
    del output[-1]
    output = [x[:-1] for x in output]
    return output



domain = input("Domain? ")

try:
    os.mkdir('projects/'+domain)
    os.mkdir('projects/'+domain+"/images")
except:
    pass

def find_subs():
    try:
        os.remove('tmp/amass_tmp_output.json')
    except:
        pass
    try:
        os.remove('tmp/subfinder_tmp_output.json')
    except:
        pass

    print("Running Amass...")
    print(subprocess.check_output(['amass/amass', 'enum', '-d', domain, '-ip', '-json', 'tmp/amass_tmp_output.json']))

    print("Running Subfinder...")
    print(subprocess.check_output(['subfinder/subfinder', '-d', domain, '-oJ', '-nW', '-o', 'tmp/subfinder_tmp_output.json']))

def process_subs():
    print("Processing Amass Data...")

    # TODO: Add Reverse DNS Lookup to find additional domains/apps
    amass_tmp_json = []
    with open('tmp/amass_tmp_output.json') as fp:
       for cnt, line in enumerate(fp):
            try:
               amass_tmp_json.append(json.loads(line))
            except:
               # Sometimes the JSON from amass is not valid
               print("Unable to Parse JSON on line", str(cnt), str(line))

    print(amass_tmp_json)
    for domain_entry in amass_tmp_json:
        print("processing amass domain", domain_entry)
        for ip_data in domain_entry['addresses']:
            ip = ip_data['ip']
            if ip in final_ip_data:
                if su(domain_entry['name']) not in final_ip_data[ip]['domains']:
                    final_ip_data[ip]['domains'].append(su(domain_entry['name']))
            else:
                ip_obj = {'ip_address': ip, 'domains':[ip, su(domain_entry['name'])], 'discovered_ports':check_http_port(ip), 'ans_info':process_asn(ip)}
                final_ip_data[ip] = ip_obj

            for domain in getRevDns(ip):
                if domain not in final_ip_data[ip]['domains']:
                    print("adding", domain)
                    final_ip_data[ip]['domains'].append(domain)

    print("Processing Subfinder Data...")

    subfinder_json = []
    with open('tmp/subfinder_tmp_output.json', 'r') as f:
        line = f.readline()
        count = 1
        for cnt, line in enumerate(f):
            try:
                subfinder_json.append(json.loads(line)['host'])
            except:
                # Sometimes the JSON from amass is not valid
                print("Unable to Parse JSON on line", str(cnt), str(line))

    for domain_entry in subfinder_json:
        print("processing", domain_entry)
        try:
            ip = socket.gethostbyname(domain_entry)
            if ip in final_ip_data:
                if domain_entry not in final_ip_data[ip]['domains']:
                    final_ip_data[ip]['domains'].append(domain_entry)
            else:
                ip_obj = {'ip_address': ip, 'domains':[ip, domain_entry], 'discovered_ports':check_http_port(ip), 'ans_info':process_asn(ip)}
                final_ip_data[ip] = ip_obj

            for domain in getRevDns(ip):
                if domain not in final_ip_data[ip]['domains']:
                    print("adding", domain)
                    final_ip_data[ip]['domains'].append(domain)

        except Exception as e:
            final_unresolved_domains.append(domain_entry)

    # Add domain Meta
    for k,v in final_ip_data.items():
        print(v, "V")
        final_domain_list = []
        for domain in v['domains']:
            final_domain_list.append({'domain':domain, 'https_image':None, "http_image":None})
        v['domains'] = final_domain_list

def getImages():
    # TODO File name for secureImages and save to json for output
    for k, v, in final_ip_data.items():
        for port in v['discovered_ports']:
            for domain_found_obj in v['domains']:
                domain_found = domain_found_obj['domain']
                if (port == 80):
                    url = "http://" + domain_found
                    domain_found_obj['http_image'] = domain_found.replace('.', '-') + "-full.png"
                    subprocess.Popen(["python", "webkit2png/webkit2png.py", "-F", "-D", "projects/"+domain+"/images", "-o", domain_found.replace('.', '-'),  "--ignore-ssl-check", url])
                elif (port == 443):
                    domain_found_obj['https_image'] = domain_found.replace('.', '-') + "_ssl-full.png"
                    url = "https://" + domain_found
                    subprocess.Popen(["python", "webkit2png/webkit2png.py", "-F", "-D", "projects/"+domain+"/images", "-o", domain_found.replace('.', '-') + "_ssl",  "--ignore-ssl-check", url])
                time.sleep(1)


def generateFiles():
    with open('projects/'+domain+'/unresolved_domains.json', 'w') as outfile1:
        json.dump(final_unresolved_domains, outfile1)

    with open('projects/'+domain+'/ip_data.json', 'w') as outfile2:
        json.dump(final_ip_data.values(), outfile2)

    with open('projects/'+domain+'/found_asns.json', 'w') as outfile3:
        json.dump(final_found_asns.values(), outfile3)


# Kick Everything Off
find_subs()
process_subs()
getImages()
generateFiles()

print("DONE!")

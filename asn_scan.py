import subprocess
import requests
import json
import netaddr
import os
import time

asn = raw_input("ASN? ")

tmp_asn_ip_ranges = []
final_ip_data = {}
final_found_asns = {}
final_unresolved_domains = []

try:
    os.mkdir('projects/'+asn)
    os.mkdir('projects/'+asn+"/images")
except Exception as e:
    print e

def su(s):
    try:
        return s.encode('ascii','ignore')
    except:
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
        for k, v in final_found_asns.iteritems():
            for prefix in v['prefixes']:
                if len(netaddr.all_matching_cidrs(ip_address, [prefix])):
                    found_asn = k

def getAsnInfo(asn):
    prefixs = []
    r = requests.get('https://api.bgpview.io/asn/'+asn+'/prefixes')
    asn_data = r.json()
    for prefix in asn_data['data']['ipv4_prefixes']:
        prefix = prefix['prefix']
        prefixs.append(su(prefix))
    return prefixs

def getRevDns(ip):
    output = subprocess.check_output(['dig', '+short', '-x', ip]).split('\n')
    del output[-1]
    output = [x[:-1] for x in output]
    output.append(ip)
    return output

def scanPrefixes(prefixes):
    for prefix in prefixes:
        output = subprocess.check_output(['masscan/bin/masscan', '-p80,443', prefix, '-oJ', 'tmp/masscan_prefix.json'])
        try:
            with open('tmp/masscan_prefix.json', 'r') as f:
                masscan_json = json.load(f)

            for entry in masscan_json:
                ip = entry['ip']
                if ip in final_ip_data:
                    if su(entry['ports'][0]['port']) not in final_ip_data[ip]['discovered_ports']:
                        final_ip_data[ip]['discovered_ports'].append(su(entry['ports'][0]['port']))
                else:
                    ip_obj = {'ip_address': ip, 'domains':getRevDns(ip), 'discovered_ports':[su(entry['ports'][0]['port'])], 'ans_info':process_asn(ip)}
                    final_ip_data[ip] = ip_obj

        except Exception as e:
            print e

    # Add domain Meta
    for k,v in final_ip_data.iteritems():
        print v, "V"
        final_domain_list = []
        for domain in v['domains']:
            final_domain_list.append({'domain':domain, 'https_image':None, "http_image":None})
            v['domains'] = final_domain_list

def getImages():
    # TODO File name for secureImages and save to json for output
    for k, v, in final_ip_data.iteritems():
        for port in v['discovered_ports']:
            for domain_found_obj in v['domains']:
                domain_found = domain_found_obj['domain']
                if (port == 80):
                    url = "http://" + domain_found
                    domain_found_obj['http_image'] = domain_found.replace('.', '-') + "-full.png"
                    subprocess.Popen(["python", "webkit2png/webkit2png.py", "-F", "-D", "projects/"+asn+"/images", "-o", domain_found.replace('.', '-'),  "--ignore-ssl-check", url])
                elif (port == 443):
                    domain_found_obj['https_image'] = domain_found.replace('.', '-') + "_ssl-full.png"
                    url = "https://" + domain_found
                    subprocess.Popen(["python", "webkit2png/webkit2png.py", "-F", "-D", "projects/"+asn+"/images", "-o", domain_found.replace('.', '-') + "_ssl",  "--ignore-ssl-check", url])
                time.sleep(1)

def generateFiles():
    with open('projects/'+asn+'/unresolved_domains.json', 'w') as outfile1:
        json.dump(final_unresolved_domains, outfile1)

    with open('projects/'+asn+'/ip_data.json', 'w') as outfile2:
        json.dump(final_ip_data.values(), outfile2)

    with open('projects/'+asn+'/found_asns.json', 'w') as outfile3:
        json.dump(final_found_asns.values(), outfile3)

prefixes = getAsnInfo(asn)
scanPrefixes(prefixes)
getImages()
generateFiles()

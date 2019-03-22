# Autorecon

Python tools for automating internet research with a little web UI for reviewing results. Sadly, only works on Mac (webkit2png). Loosely based on the recon section of The Bug Hunter's Methodology by @jhaddix

## Dependancies

* Go
* Python 2.7
* pip
* bower
* wget (`brew install wget`)

Then run `install.sh`

## Recon Scripts

*asn_scan.py*

Input a BGP AS number. All IPs in every prefix are scanned, a reverse DNS lookup is run to try to find domains on the IP, ports 80 and 443 are checked, screenshots of all domains are taken. All data is saved into a project folder in JSON format.


*domain_scan.py*

Input a TLD. Amass and subfinder are run to find any associated subdomains. DNS lookup is performed on the IP and the BGP ASN is recorded. Ports 80 and 443 are checked for web apps and screenshots are taken. All data is saved into a project folder in JSON format. Data includes any discovered BGP prefixes / ASNs, IPs / domains with web applications running on port 80 & 443 with screenshots, and domains that could not be resolved.

## Webapp

![Webapp Screenshot](https://raw.githubusercontent.com/tonykunda/autorecon/master/readme.png)

A quick and dirty little Bootstap/AngularJS web app for viewing the results.

In terminal, navigate to the project folder and run `python -m SimpleHTTPServer`

Open `localhost:8000/webapp` in your browser

Enter the TLD or ASN that was scanned using either tool and click `get`.

* ASNs - Displays all discovered ASNs associated with the recon. Click the AS number on the right to view HE's info on the ASN. Click the masscan button to copy a masscan command to the clipboard to paste into the terminal for manual recon.

* IP's - Displays all discovered IPs, the domains associated with them, and screenshots of the webapps running on ports 80 and 433. Click the 80 or 443 buttons to open that domain in a new tab.

* Unresolved Domains - Displays all domains that could not be resolved.

## Disclaimer

*These things were built quick and dirty - it evolved as I worked on it and almost everything should be refactored. Please don't judge me based on this code.*

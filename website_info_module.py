### Imports:
# Netzwerk und DNS:
#   - import socket:                                               - Für Netzwerkoperationen auf niedriger Ebene,
#                                                                                           z.B. IP-Adressauflösung.
#   - import dns.resolver:                                         - Für DNS-Abfragen und die Auflösung verschiedener
#                                                                                                   DNS-Record-Typen.

# HTTP und SSL:
#   - import requests:                                             - Für HTTP-Anfragen und das Abrufen von HTTP-Headern.
#   - import ssl:                                                  - Für SSL/TLS-Operationen, insbesondere zum Abrufen
#                                                                                   von SSL-Zertifikatsinformationen.

# URL-Verarbeitung:
#   - import urllib.parse:                                         - Zum Parsen und Formatieren von URLs.

### Funktionen:
# Netzwerk und DNS:
#   - get_ip(domain):                                              - Ermittelt die IP-Adresse eines Domänennamens.
#   - dns_lookup(hostname), detailed_dns_lookup(hostname):         - Führen DNS-Abfragen durch und sammeln Informationen
#                                                                                   zu verschiedenen DNS-Record-Typen.
#   - print_dns_results(hostname):                                 - Druckt DNS-Abfrageergebnisse.

# HTTP und SSL:
#   - get_ssl_info(domain):                                        - Ermittelt SSL-Zertifikatsinformationen für
#                                                                                                       eine Domäne.
#   - get_http_headers(url):                                       - Ruft HTTP-Header für eine URL ab.

# URL-Verarbeitung und Website-Information:
#   - format_url(url):                                             - Formatiert eine URL, indem automatisch ein Schema
#                                                                               hinzugefügt wird, falls nicht vorhanden.
#   - website_info_lookup(url):                                    - Sammelt und formatiert Informationen über eine
#                                                                               Website, einschließlich IP-Adresse,
#                                                                                           SSL-Info und HTTP-Header.

# Geolocation:
#   - print_geo_results(ip_address):                                - Druckt Geolokalisierungsinformationen zu einer
#                                                                                                           IP-Adresse.
#   - geo_ip_lookup(ip_address):                                    - Ermittelt Geolokalisierungsinformationen für eine
#                                                                                                           IP-Adresse.
########################################################################################################################

import socket
import ssl
import requests
import urllib.parse
import dns.resolver


def get_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return "IP address not found"


def get_ssl_info(domain):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                if isinstance(cert, dict):
                    return '\n '.join([f"{k}: {v}\n" for k, v in cert.items()])
                else:
                    return "SSL info not found or in unexpected format"
    except ssl.SSLError as e:
        return f"SSL error: {str(e)}"
    except socket.error as e:
        return f"Socket error: {str(e)}"


def get_http_headers(url):
    try:
        response = requests.get(url)
        if response.ok:
            return '\n '.join([f"{k}: {v}\n" for k, v in response.headers.items()])
        else:
            return "HTTP headers not found or request failed"
    except requests.RequestException as e:
        return f"Request failed: {str(e)}"


def format_url(url):
    if not urllib.parse.urlparse(url).scheme:
        url = "http://" + url
    return url


def website_info_lookup(url):
    url = format_url(url)
    parsed_url = urllib.parse.urlparse(url)
    domain = parsed_url.netloc or parsed_url.path

    ip = get_ip(domain)
    ssl_info = get_ssl_info(domain)
    http_headers = get_http_headers(url)

    formatted_output = f"Website Information for {url}:\n\n"
    info = {
        "IP Address": ip,
        "SSL Info": ssl_info,
        "HTTP Headers": http_headers
    }

    for key, value in info.items():
        formatted_output += f"{key}:\n{value}\n\n"

    return formatted_output


def dns_lookup(hostname):
    try:
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except socket.gaierror:
        return "Hostname could not be resolved"


def detailed_dns_lookup(hostname):
    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
    results = {}
    for record_type in record_types:
        try:
            answers = dns.resolver.resolve(hostname, record_type)
            results[record_type] = [rdata.to_text() for rdata in answers]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            results[record_type] = f"No answer for record type {record_type}\n"
        except Exception as e:
            results[record_type] = str(e)

    formatted_output = []
    for record_type, answers in results.items():
        formatted_output.append(f"{record_type} Records:")
        if isinstance(answers, list):
            for answer in answers:
                formatted_output.append(f" - {answer}")
        else:
            formatted_output.append(f" - {answers}")
        formatted_output.append("")

    return "\n".join(formatted_output)


def print_dns_results(hostname):
    print(f"DNS Lookup for {hostname}:\n")
    print(f"IP Address: {dns_lookup(hostname)}\n")
    detailed_results = detailed_dns_lookup(hostname)
    for record_type, answers in detailed_results.items():
        print(f"{record_type} Records:")
        if isinstance(answers, list):
            for answer in answers:
                print(f"\n  - {answer}\n")
        else:
            print(f"\n  - {answers}\n")
        print()


def print_geo_results(ip_address):
    geo_data = geo_ip_lookup(ip_address)
    if isinstance(geo_data, dict):
        geo_info = f"Geo Lookup for IP Address {ip_address}:\n"
        for key, value in geo_data.items():
            geo_info += f"{key.capitalize()}: {value}\n"
    else:
        geo_info = geo_data
    return geo_info


def geo_ip_lookup(ip_address):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        response.raise_for_status()
        data = response.json()
        if data['status'] == 'success':
            return data
        else:
            return "Geolocation lookup failed."
    except requests.exceptions.RequestException as e:
        return str(e)
